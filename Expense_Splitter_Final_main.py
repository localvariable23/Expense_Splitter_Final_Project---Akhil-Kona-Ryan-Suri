"""
Expense Splitter Application
A simple expense sharing application similar to Splitwise
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class User:
    """Represents a user in the expense splitting system"""
    
    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.balances: Dict[str, float] = {}
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'balances': self.balances
        }
    
    @staticmethod
    def from_dict(data):
        user = User(data['user_id'], data['name'], data['email'])
        user.balances = data.get('balances', {})
        return user


class Expense:
    """Represents an expense that needs to be split"""
    
    def __init__(self, expense_id: str, description: str, amount: float, 
                 paid_by: str, split_among: List[str], date: str = None,
                 split_type: str = "equal", split_details: Dict[str, float] = None):
        self.expense_id = expense_id
        self.description = description
        self.amount = amount
        self.paid_by = paid_by
        self.split_among = split_among
        self.date = date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.split_type = split_type # "equal", "exact", or "percentage"
        self.split_details = split_details or {} # user_id -> amount/percentage
    
    def to_dict(self):
        return {
            'expense_id': self.expense_id,
            'description': self.description,
            'amount': self.amount,
            'paid_by': self.paid_by,
            'split_among': self.split_among,
            'date': self.date,
            'split_type': self.split_type,
            'split_details': self.split_details
        }
    
    @staticmethod
    def from_dict(data):
        expense = Expense(
            data['expense_id'],
            data['description'],
            data['amount'],
            data['paid_by'],
            data['split_among'],
            data.get('date'),
            data.get('split_type', 'equal'),
            data.get('split_details', {})
        )
        return expense


class Group:
    """Represents a group of users who share expenses"""
    
    def __init__(self, group_id: str, name: str, created_by: str):
        self.group_id = group_id
        self.name = name
        self.created_by = created_by
        self.members: List[str] = [created_by]
        self.expenses: List[str] = []
    
    def add_member(self, user_id: str):
        if user_id not in self.members:
            self.members.append(user_id)
            return True
        return False
    
    def remove_member(self, user_id: str):
        if user_id in self.members and user_id != self.created_by:
            self.members.remove(user_id)
            return True
        return False
    
    def to_dict(self):
        return {
            'group_id': self.group_id,
            'name': self.name,
            'created_by': self.created_by,
            'members': self.members,
            'expenses': self.expenses
        }
    
    @staticmethod
    def from_dict(data):
        group = Group(data['group_id'], data['name'], data['created_by'])
        group.members = data.get('members', [data['created_by']])
        group.expenses = data.get('expenses', [])
        return group


class ExpenseSplitter:
    """Main application class for managing expenses"""
    
    def __init__(self, data_file: str = "expense_data.json"):
        self.data_file = data_file
        self.users: Dict[str, User] = {}
        self.expenses: Dict[str, Expense] = {}
        self.groups: Dict[str, Group] = {}
        self.current_user: Optional[User] = None
        self.load_data()
    
    def save_data(self):
        """Save all data to JSON file"""
        data = {
            'users': {uid: user.to_dict() for uid, user in self.users.items()},
            'expenses': {eid: expense.to_dict() for eid, expense in self.expenses.items()},
            'groups': {gid: group.to_dict() for gid, group in self.groups.items()}
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                self.users = {uid: User.from_dict(udata) 
                             for uid, udata in data.get('users', {}).items()}
                self.expenses = {eid: Expense.from_dict(edata) 
                                for eid, edata in data.get('expenses', {}).items()}
                self.groups = {gid: Group.from_dict(gdata) 
                              for gid, gdata in data.get('groups', {}).items()}
            except Exception as e:
                print(f"Error loading data: {e}")
    
    def create_user(self, name: str, email: str) -> User:
        """Create a new user"""
        user_id = f"U{len(self.users) + 1:03d}"
        user = User(user_id, name, email)
        self.users[user_id] = user
        self.save_data()
        return user
    
    def create_group(self, name: str, creator_id: str) -> Optional[Group]:
        """Create a new group"""
        if creator_id not in self.users:
            return None
        
        group_id = f"G{len(self.groups) + 1:03d}"
        group = Group(group_id, name, creator_id)
        self.groups[group_id] = group
        self.save_data()
        return group
    
    def add_expense(self, description: str, amount: float, paid_by: str, 
               split_among: List[str], group_id: Optional[str] = None,
               split_type: str = "equal", split_details: Dict[str, float] = None) -> Optional[Expense]:
        """Add a new expense and update balances"""
        if paid_by not in self.users:
            return None
    
        for user_id in split_among:
            if user_id not in self.users:
                return None
    
        # Validate split_details based on split_type
        if split_type == "percentage":
            if not split_details:
                return None
            total_percentage = sum(split_details.values())
            if abs(total_percentage - 100.0) > 0.01:
                print(f"Error: Percentages must sum to 100% (currently {total_percentage}%)")
                return None
    
        elif split_type == "exact":
            if not split_details:
                return None
            total_exact = sum(split_details.values())
            if abs(total_exact - amount) > 0.01:
                print(f"Error: Exact amounts must sum to total ${amount} (currently ${total_exact})")
                return None
    
        expense_id = f"E{len(self.expenses) + 1:04d}"
        expense = Expense(expense_id, description, amount, paid_by, split_among,
                          split_type=split_type, split_details=split_details or {})
        self.expenses[expense_id] = expense
    
        if group_id and group_id in self.groups:
            self.groups[group_id].expenses.append(expense_id)
    
        # Calculate split amounts based on type
        split_amounts = {}
    
        if split_type == "equal":
            split_amount = amount / len(split_among)
            for user_id in split_among:
                split_amounts[user_id] = split_amount
    
        elif split_type == "percentage":
            for user_id in split_among:
                percentage = split_details.get(user_id, 0)
                split_amounts[user_id] = (percentage / 100.0) * amount
    
        elif split_type == "exact":
            split_amounts = split_details.copy()
    
        # Update balances
        payer = self.users[paid_by]
        for user_id in split_among:
            if user_id != paid_by:
                owed_amount = split_amounts[user_id]
            
                # Payer is owed money
                if user_id not in payer.balances:
                    payer.balances[user_id] = 0
                payer.balances[user_id] += owed_amount
            
                # Other user owes money
                user = self.users[user_id]
                if paid_by not in user.balances:
                    user.balances[paid_by] = 0
                user.balances[paid_by] -= owed_amount
    
        self.save_data()
        return expense
    
    def settle_balance(self, payer_id: str, receiver_id: str, amount: float) -> bool:
        """Settle a balance between two users"""
        if payer_id not in self.users or receiver_id not in self.users:
            return False
        
        payer = self.users[payer_id]
        receiver = self.users[receiver_id]
        
        # Update balances
        if receiver_id in payer.balances:
            payer.balances[receiver_id] += amount
            if abs(payer.balances[receiver_id]) < 0.01:
                del payer.balances[receiver_id]
        
        if payer_id in receiver.balances:
            receiver.balances[payer_id] -= amount
            if abs(receiver.balances[payer_id]) < 0.01:
                del receiver.balances[payer_id]
        
        self.save_data()
        return True
    
    def get_user_balance(self, user_id: str) -> Dict[str, float]:
        """Get all balances for a user"""
        if user_id not in self.users:
            return {}
        return self.users[user_id].balances.copy()
    
    def get_total_balance(self, user_id: str) -> float:
        """Get total balance for a user (positive = owed, negative = owes)"""
        if user_id not in self.users:
            return 0.0
        return sum(self.users[user_id].balances.values())
    
    def get_user_expenses(self, user_id: str) -> List[Expense]:
        """Get all expenses involving a user"""
        user_expenses = []
        for expense in self.expenses.values():
            if user_id == expense.paid_by or user_id in expense.split_among:
                user_expenses.append(expense)
        return sorted(user_expenses, key=lambda x: x.date, reverse=True)
    
    def get_group_expenses(self, group_id: str) -> List[Expense]:
        """Get all expenses for a group"""
        if group_id not in self.groups:
            return []
        
        group = self.groups[group_id]
        return [self.expenses[eid] for eid in group.expenses if eid in self.expenses]


def print_menu():
    """Display main menu"""
    print("\n" + "="*50)
    print("EXPENSE SPLITTER")
    print("="*50)
    print("1. Create User")
    print("2. Login as User")
    print("3. Create Group")
    print("4. Add Member to Group")
    print("5. Add Expense")
    print("6. View My Balances")
    print("7. View My Expenses")
    print("8. Settle Balance")
    print("9. View Group Details")
    print("10. View All Users")
    print("11. Add Expense with Custom Split")
    print("12. Reset All Data")
    print("0. Exit")
    print("="*50)


def main():
    """Main application loop"""
    app = ExpenseSplitter()
    
    while True:
        print_menu()
        choice = input("\nEnter your choice (0-10): ").strip()
        
        if choice == "1":
            name = input("Enter name: ").strip()
            email = input("Enter email: ").strip()
            user = app.create_user(name, email)
            print(f"\n User created successfully! User ID: {user.user_id}")
        
        elif choice == "2":
            user_id = input("Enter User ID: ").strip()
            if user_id in app.users:
                app.current_user = app.users[user_id]
                print(f"\n Logged in as {app.current_user.name}")
            else:
                print("\n User not found!")
        
        elif choice == "3":
            if not app.current_user:
                print("\n Please login first!")
                continue
            
            name = input("Enter group name: ").strip()
            group = app.create_group(name, app.current_user.user_id)
            if group:
                print(f"\n Group created successfully! Group ID: {group.group_id}")
            else:
                print("\n Error creating group!")
        
        elif choice == "4":
            group_id = input("Enter Group ID: ").strip()
            user_id = input("Enter User ID to add: ").strip()
            
            if group_id in app.groups and user_id in app.users:
                if app.groups[group_id].add_member(user_id):
                    app.save_data()
                    print("\n User added to group!")
                else:
                    print("\n User already in group!")
            else:
                print("\n Group or user not found!")
        
        elif choice == "5":
            if not app.current_user:
                print("\n Please login first!")
                continue
            
            description = input("Enter expense description: ").strip()
            amount = float(input("Enter amount: ").strip())
            
            print("\nSplit among (enter User IDs separated by commas):")
            split_ids = [uid.strip() for uid in input().split(",")]
            
            group_id = input("Enter Group ID (optional, press Enter to skip): ").strip()
            group_id = group_id if group_id else None
            
            expense = app.add_expense(description, amount, app.current_user.user_id, 
                                     split_ids, group_id)
            if expense:
                print(f"\n Expense added successfully! Expense ID: {expense.expense_id}")
                print(f"Split amount per person: ${amount/len(split_ids):.2f}")
            else:
                print("\n Error adding expense!")
        
        elif choice == "6":
            if not app.current_user:
                print("\n Please login first!")
                continue
            
            balances = app.get_user_balance(app.current_user.user_id)
            total = app.get_total_balance(app.current_user.user_id)
            
            print(f"\n{'='*50}")
            print(f"BALANCES FOR {app.current_user.name}")
            print(f"{'='*50}")
            
            if not balances:
                print("No outstanding balances!")
            else:
                for user_id, amount in balances.items():
                    other_user = app.users[user_id]
                    if amount > 0:
                        print(f"{other_user.name} owes you: ${amount:.2f}")
                    else:
                        print(f"You owe {other_user.name}: ${abs(amount):.2f}")
            
            print(f"\nTotal balance: ${total:.2f}")
            if total > 0:
                print("(You are owed money)")
            elif total < 0:
                print("(You owe money)")
        
        elif choice == "7":
            if not app.current_user:
                print("\n Please login first!")
                continue
            
            expenses = app.get_user_expenses(app.current_user.user_id)
            
            print(f"\n{'='*50}")
            print(f"EXPENSES FOR {app.current_user.name}")
            print(f"{'='*50}")
            
            if not expenses:
                print("No expenses found!")
            else:
                for expense in expenses[:10]:  # Show last 10
                    payer = app.users[expense.paid_by]
                    split_count = len(expense.split_among)
                    print(f"\n{expense.date}")
                    print(f"Description: {expense.description}")
                    print(f"Amount: ${expense.amount:.2f}")
                    print(f"Paid by: {payer.name}")
                    print(f"Split among {split_count} people")
        
        elif choice == "8":
            if not app.current_user:
                print("\n Please login first!")
                continue
            
            receiver_id = input("Enter User ID to settle with: ").strip()
            amount = float(input("Enter settlement amount: ").strip())
            
            if app.settle_balance(app.current_user.user_id, receiver_id, amount):
                print("\n Balance settled successfully!")
            else:
                print("\n Error settling balance!")
        
        elif choice == "9":
            group_id = input("Enter Group ID: ").strip()
            if group_id in app.groups:
                group = app.groups[group_id]
                print(f"\n{'='*50}")
                print(f"GROUP: {group.name}")
                print(f"{'='*50}")
                print(f"Created by: {app.users[group.created_by].name}")
                print("\nMembers:")
                for member_id in group.members:
                    print(f"  - {app.users[member_id].name} ({member_id})")
                print(f"\nTotal expenses: {len(group.expenses)}")
            else:
                print("\n Group not found!")
        
        elif choice == "10":
            print(f"\n{'='*50}")
            print("ALL USERS")
            print(f"{'='*50}")
            for user in app.users.values():
                print(f"{user.user_id}: {user.name} ({user.email})")
                
        elif choice == "11":
            if not app.current_user:
                print("\n✗ Please login first!")
                continue
            
            description = input("Enter expense description: ").strip()
            amount = float(input("Enter amount: ").strip())
            
            print("\nSplit among (enter User IDs separated by commas):")
            split_ids = [uid.strip() for uid in input().split(",")]
            
            print("\nSplit type:")
            print("1. Equal split")
            print("2. Percentage split")
            print("3. Exact amounts")
            split_choice = input("Enter choice (1-3): ").strip()
            
            split_type = "equal"
            split_details = {}
            
            if split_choice == "1":
                split_type = "equal"
            
            elif split_choice == "2":
                split_type = "percentage"
                print("\nEnter percentage for each user (must sum to 100%):")
                for user_id in split_ids:
                    user_name = app.users[user_id].name if user_id in app.users else user_id
                    percentage = float(input(f"{user_name} ({user_id}): ").strip())
                    split_details[user_id] = percentage
            
            elif split_choice == "3":
                split_type = "exact"
                print(f"\nEnter exact amount for each user (must sum to ${amount}):")
                for user_id in split_ids:
                    user_name = app.users[user_id].name if user_id in app.users else user_id
                    exact_amount = float(input(f"{user_name} ({user_id}): $").strip())
                    split_details[user_id] = exact_amount
            
            group_id = input("\nEnter Group ID (optional, press Enter to skip): ").strip()
            group_id = group_id if group_id else None
            
            expense = app.add_expense(description, amount, app.current_user.user_id, 
                                     split_ids, group_id, split_type, split_details)
            if expense:
                print(f"\n Expense added successfully! Expense ID: {expense.expense_id}")
                print(f"Split type: {split_type}")
                if split_type == "equal":
                    print(f"Split amount per person: ${amount/len(split_ids):.2f}")
                elif split_type == "percentage":
                    for uid, pct in split_details.items():
                        print(f"{app.users[uid].name}: {pct}% (${(pct/100)*amount:.2f})")
                elif split_type == "exact":
                    for uid, amt in split_details.items():
                        print(f"{app.users[uid].name}: ${amt:.2f}")
            else:
                print("\n Error adding expense! Check validation errors above.")
        
        elif choice == "12":
            confirm = input("\n  WARNING: This will delete ALL data! Type 'RESET' to confirm: ").strip()
            if confirm == "RESET":
                app.users = {}
                app.expenses = {}
                app.groups = {}
                app.current_user = None
                app.save_data()
                print("\n All data has been reset!")
            else:
                print("\n Reset cancelled.")
                
        elif choice == "0":
            print("\nThank you for using Expense Splitter!")
            break
        
        else:
            print("\n Invalid choice! Please try again.")


if __name__ == "__main__":
    main()
