"""
Unit Tests for Expense Splitter Application
"""

import unittest
import os
import json
from expense_splitter import User, Expense, Group, ExpenseSplitter


class TestUser(unittest.TestCase):
    """Test User class"""
    
    def test_user_creation(self):
        user = User("U001", "John Doe", "john@example.com")
        self.assertEqual(user.user_id, "U001")
        self.assertEqual(user.name, "John Doe")
        self.assertEqual(user.email, "john@example.com")
        self.assertEqual(user.balances, {})
    
    def test_user_serialization(self):
        user = User("U001", "John Doe", "john@example.com")
        user.balances = {"U002": 50.0}
        
        user_dict = user.to_dict()
        self.assertEqual(user_dict['user_id'], "U001")
        self.assertEqual(user_dict['balances']['U002'], 50.0)
        
        restored_user = User.from_dict(user_dict)
        self.assertEqual(restored_user.user_id, user.user_id)
        self.assertEqual(restored_user.balances, user.balances)


class TestExpense(unittest.TestCase):
    """Test Expense class"""
    
    def test_expense_creation(self):
        expense = Expense("E001", "Lunch", 60.0, "U001", ["U001", "U002", "U003"])
        self.assertEqual(expense.expense_id, "E001")
        self.assertEqual(expense.description, "Lunch")
        self.assertEqual(expense.amount, 60.0)
        self.assertEqual(expense.paid_by, "U001")
        self.assertEqual(len(expense.split_among), 3)
    
    def test_expense_serialization(self):
        expense = Expense("E001", "Lunch", 60.0, "U001", ["U001", "U002"])
        
        expense_dict = expense.to_dict()
        restored_expense = Expense.from_dict(expense_dict)
        
        self.assertEqual(restored_expense.expense_id, expense.expense_id)
        self.assertEqual(restored_expense.amount, expense.amount)
        self.assertEqual(restored_expense.split_among, expense.split_among)


class TestGroup(unittest.TestCase):
    """Test Group class"""
    
    def test_group_creation(self):
        group = Group("G001", "Roommates", "U001")
        self.assertEqual(group.group_id, "G001")
        self.assertEqual(group.name, "Roommates")
        self.assertEqual(group.created_by, "U001")
        self.assertIn("U001", group.members)
    
    def test_add_member(self):
        group = Group("G001", "Roommates", "U001")
        result = group.add_member("U002")
        self.assertTrue(result)
        self.assertIn("U002", group.members)
        
        # Try adding same member again
        result = group.add_member("U002")
        self.assertFalse(result)
    
    def test_remove_member(self):
        group = Group("G001", "Roommates", "U001")
        group.add_member("U002")
        
        # Remove regular member
        result = group.remove_member("U002")
        self.assertTrue(result)
        self.assertNotIn("U002", group.members)
        
        # Try to remove creator (should fail)
        result = group.remove_member("U001")
        self.assertFalse(result)
        self.assertIn("U001", group.members)


class TestExpenseSplitter(unittest.TestCase):
    """Test main ExpenseSplitter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_file = "test_expense_data.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.app = ExpenseSplitter(self.test_file)
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_create_user(self):
        user = self.app.create_user("Alice", "alice@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "Alice")
        self.assertIn(user.user_id, self.app.users)
    
    def test_create_group(self):
        user = self.app.create_user("Alice", "alice@example.com")
        group = self.app.create_group("Test Group", user.user_id)
        
        self.assertIsNotNone(group)
        self.assertEqual(group.name, "Test Group")
        self.assertIn(group.group_id, self.app.groups)
        self.assertIn(user.user_id, group.members)
    
    def test_add_expense_equal_split(self):
        alice = self.app.create_user("Alice", "alice@example.com")
        bob = self.app.create_user("Bob", "bob@example.com")
        charlie = self.app.create_user("Charlie", "charlie@example.com")
        
        # Alice pays $90 for 3 people (should be $30 each)
        expense = self.app.add_expense(
            "Dinner", 90.0, alice.user_id,
            [alice.user_id, bob.user_id, charlie.user_id]
        )
        
        self.assertIsNotNone(expense)
        
        # Check balances
        alice_balance = self.app.get_total_balance(alice.user_id)
        bob_balance = self.app.get_total_balance(bob.user_id)
        charlie_balance = self.app.get_total_balance(charlie.user_id)
        
        # Alice should be owed $60 (paid $90, owes $30)
        self.assertAlmostEqual(alice_balance, 60.0, places=2)
        # Bob and Charlie each owe $30
        self.assertAlmostEqual(bob_balance, -30.0, places=2)
        self.assertAlmostEqual(charlie_balance, -30.0, places=2)
    
    def test_settle_balance(self):
        alice = self.app.create_user("Alice", "alice@example.com")
        bob = self.app.create_user("Bob", "bob@example.com")
        
        # Alice pays $50 for both
        self.app.add_expense("Lunch", 50.0, alice.user_id, 
                            [alice.user_id, bob.user_id])
        
        # Bob owes $25
        self.assertAlmostEqual(self.app.get_total_balance(bob.user_id), -25.0)
        
        # Bob settles the balance
        self.app.settle_balance(bob.user_id, alice.user_id, 25.0)
        
        # Both should have zero balance
        self.assertAlmostEqual(self.app.get_total_balance(alice.user_id), 0.0)
        self.assertAlmostEqual(self.app.get_total_balance(bob.user_id), 0.0)
    
    def test_multiple_expenses(self):
        alice = self.app.create_user("Alice", "alice@example.com")
        bob = self.app.create_user("Bob", "bob@example.com")
        
        # Expense 1: Alice pays $100, split between both
        self.app.add_expense("Groceries", 100.0, alice.user_id,
                            [alice.user_id, bob.user_id])
        
        # Expense 2: Bob pays $60, split between both
        self.app.add_expense("Dinner", 60.0, bob.user_id,
                            [alice.user_id, bob.user_id])
        
        # Alice should be owed: $50 (from first) - $30 (from second) = $20
        alice_balance = self.app.get_total_balance(alice.user_id)
        self.assertAlmostEqual(alice_balance, 20.0, places=2)
        
        # Bob should owe: -$50 (from first) + $30 (from second) = -$20
        bob_balance = self.app.get_total_balance(bob.user_id)
        self.assertAlmostEqual(bob_balance, -20.0, places=2)
    
    def test_data_persistence(self):
        # Create users and expense
        alice = self.app.create_user("Alice", "alice@example.com")
        bob = self.app.create_user("Bob", "bob@example.com")
        self.app.add_expense("Test", 100.0, alice.user_id,
                            [alice.user_id, bob.user_id])
        
        # Create new app instance (should load from file)
        new_app = ExpenseSplitter(self.test_file)
        
        self.assertEqual(len(new_app.users), 2)
        self.assertEqual(len(new_app.expenses), 1)
        self.assertIn(alice.user_id, new_app.users)
        self.assertAlmostEqual(new_app.get_total_balance(alice.user_id), 50.0)
    
    def test_get_user_expenses(self):
        alice = self.app.create_user("Alice", "alice@example.com")
        bob = self.app.create_user("Bob", "bob@example.com")
        
        self.app.add_expense("Expense 1", 50.0, alice.user_id,
                            [alice.user_id, bob.user_id])
        self.app.add_expense("Expense 2", 30.0, bob.user_id,
                            [alice.user_id, bob.user_id])
        
        alice_expenses = self.app.get_user_expenses(alice.user_id)
        self.assertEqual(len(alice_expenses), 2)
    
    def test_group_expenses(self):
        alice = self.app.create_user("Alice", "alice@example.com")
        bob = self.app.create_user("Bob", "bob@example.com")
        group = self.app.create_group("Test Group", alice.user_id)
        group.add_member(bob.user_id)
        
        # Add expense to group
        self.app.add_expense("Group Expense", 100.0, alice.user_id,
                            [alice.user_id, bob.user_id], group.group_id)
        
        group_expenses = self.app.get_group_expenses(group.group_id)
        self.assertEqual(len(group_expenses), 1)
        self.assertEqual(group_expenses[0].description, "Group Expense")


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        self.test_file = "test_integration_data.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.app = ExpenseSplitter(self.test_file)
    
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_roommate_scenario(self):
        """Test a realistic roommate expense scenario"""
        # Create roommates
        alice = self.app.create_user("Alice", "alice@example.com")
        bob = self.app.create_user("Bob", "bob@example.com")
        charlie = self.app.create_user("Charlie", "charlie@example.com")
        
        # Create group
        group = self.app.create_group("Apartment 3B", alice.user_id)
        group.add_member(bob.user_id)
        group.add_member(charlie.user_id)
        
        # Month's expenses
        self.app.add_expense("Rent", 1500.0, alice.user_id,
                            [alice.user_id, bob.user_id, charlie.user_id],
                            group.group_id)
        
        self.app.add_expense("Utilities", 150.0, bob.user_id,
                            [alice.user_id, bob.user_id, charlie.user_id],
                            group.group_id)
        
        self.app.add_expense("Groceries", 200.0, charlie.user_id,
                            [alice.user_id, bob.user_id, charlie.user_id],
                            group.group_id)
        
        # Calculate what each person should have paid
        total = 1500 + 150 + 200  # $1850
        per_person = total / 3  # $616.67
        
        # Alice paid $1500, should have paid $616.67, so owed $883.33
        alice_balance = self.app.get_total_balance(alice.user_id)
        self.assertAlmostEqual(alice_balance, 1500 - per_person, places=2)
        
        # Bob paid $150, should have paid $616.67, so owes $466.67
        bob_balance = self.app.get_total_balance(bob.user_id)
        self.assertAlmostEqual(bob_balance, 150 - per_person, places=2)
        
        # Charlie paid $200, should have paid $616.67, so owes $416.67
        charlie_balance = self.app.get_total_balance(charlie.user_id)
        self.assertAlmostEqual(charlie_balance, 200 - per_person, places=2)
        
        # Total should sum to zero
        total_balance = alice_balance + bob_balance + charlie_balance
        self.assertAlmostEqual(total_balance, 0.0, places=2)


if __name__ == '__main__':
    unittest.main()
