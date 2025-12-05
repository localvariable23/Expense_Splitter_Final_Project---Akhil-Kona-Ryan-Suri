
# Expense Splitter Application

A Python-based expense sharing application similar to Splitwise that helps users track shared expenses and manage balances between friends, roommates, or groups.

### Core Features
1. **User Management**
   - Create and manage user accounts
   - Login system with user IDs
   - User profile with email and name

2. **Expense Tracking**
   - Add expenses with description and amount
   - Track who paid and who owes
   - Automatic equal splitting among participants
   - View expense history

3. **Balance Management**
   - Real-time balance calculation
   - Track who owes whom
   - Settle balances between users
   - View total balance (owed or owing)

4. **Group Management**
   - Create groups for recurring expense sharing
   - Add/remove group members
   - Track group-specific expenses
   - View group details and statistics

5. **Data Persistence**
   - Save all data to JSON file
   - Load existing data on startup
   - Persistent storage across sessions


### Basic Workflow

1. **Create Users**
   - Select option 1 from the menu
   - Enter name and email
   - Note the User ID for login

2. **Login**
   - Select option 2
   - Enter your User ID

3. **Create a Group** (Optional)
   - Select option 3
   - Enter group name
   - Note the Group ID

4. **Add Members to Group**
   - Select option 4
   - Enter Group ID and User IDs to add

5. **Add Expenses**
   - Select option 5
   - Enter expense details
   - Specify who to split among
   - Optionally link to a group

6. **View Balances**
   - Select option 6 to see who owes you and whom you owe

7. **Settle Balances**
   - Select option 8
   - Enter the User ID and amount to settle

### Example Session

```
User A creates account → User ID: U001
User B creates account → User ID: U002
User C creates account → User ID: U003

User A logs in
User A creates group "Roommates" → Group ID: G001
User A adds User B and C to group

User A adds expense:
  Description: "Groceries"
  Amount: $90
  Split among: U001, U002, U003
  Result: B owes A $30, C owes A $30

User B settles $30 with User A
  Result: B balance = $0, A is owed $30 from C only
```

## Project Structure

```
expense-splitter/
 expense_splitter.py      # Main application code
 test_expense_splitter.py # Unit tests
 README.md                # This file
 expense_data.json        # Data storage (auto-generated)
```

## Core Components

### Classes

#### User
Represents a user in the system with:
- User ID, name, email
- Balance tracking with other users

#### Expense
Represents an expense with:
- Expense ID, description, amount
- Payer and participants
- Date and split type

#### Group
Represents a group of users with:
- Group ID, name, creator
- Member list
- Associated expenses

#### ExpenseSplitter
Main application class handling:
- User management
- Expense creation and tracking
- Balance calculation and settlement
- Group management
- Data persistence

### Key Methods

**ExpenseSplitter.add_expense()**
- Adds new expense
- Calculates split amounts
- Updates all user balances
- Supports equal splitting

**ExpenseSplitter.settle_balance()**
- Records payment between users
- Updates balances accordingly
- Removes zero balances

**ExpenseSplitter.get_total_balance()**
- Calculates net balance for a user
- Positive = owed money
- Negative = owes money

## Testing

### Running Tests

### Test Coverage
The test suite includes:
- Unit tests for all classes
- Integration tests for complete workflows
- Balance calculation verification
- Data persistence testing
- Group functionality testing

### Example Test Cases
- Creating users and groups
- Adding and splitting expenses
- Settling balances
- Multiple expense scenarios
- Roommate expense workflow
- Data save/load functionality

## Development Timeline

### Week 1: Core Development (Oct 19-27)

**Saturday, Oct 19 - Core Development Start**
- Implemented User class with balance tracking
- Implemented Expense class with split logic
- Implemented Group class for collective expenses
- Core system architecture functional

**Tuesday, Oct 22 - Check-In Meeting**
- Reviewed progress on core classes
- Discussed balance calculation algorithms
- Adjusted data structure for efficiency

**Thursday, Oct 24 - Peer Review & Feedback**
- Received feedback on code organization
- Improved error handling
- Enhanced user experience in CLI

**Sunday, Oct 27 - Core Feature Deadline**
- All core features completed
- Testing and debugging completed
- Data persistence implemented


## Features Implemented

## Must-Have Features
- User creation and management
- Expense creation and tracking
- Equal expense splitting
- Unequal split options (by percentage or exact amounts)
- Balance calculation
- Balance settlement
- Data persistence
- Group management
- Expense history
- Reset all data

## Additional Features
- JSON data storage
- Group-based expense tracking
- Command-line interface
- Comprehensive error handling
- Detailed balance reports

## Future Enhancements
- Web interface
- Email notifications
- Expense categories and filtering
- Multi-currency support

## Technical Challenges

### Challenge 1: Balance Calculation
**Problem**: Managing balances between users
**Solution**: Implemented dual-sided balance tracking where each user maintains their relationships

### Challenge 2: Precision Tracking
**Problem**: Python floating-point arithmetic caused small rounding errors (e.g., $0.0001), making total balances across all users not sum to exactly zero, creating phantom debts.
**Solution**: Added threshold checking in the settle_balance method. Any balance smaller than $0.01 is automatically removed from the system, treating it as zero and maintaining financial accuracy.


## Lessons Learned
- Importance of planning data structures before implementation
- Value of comprehensive testing for financial calculations
- Benefits of modular class design for maintainability

