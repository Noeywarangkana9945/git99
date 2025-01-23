from datetime import datetime, timedelta

class Bank:
    def __init__(self, name):
        self.name = name
        self.accounts = {}

    def create_account(self, account_number, name, initial_balance, pin, expiry_date):
        self.accounts[account_number] = {
            'name': name,
            'balance': initial_balance,
            'transactions': [],
            'pin': pin,
            'expiry_date': expiry_date
        }

    def deposit(self, account_number, amount):
        self.accounts[account_number]['balance'] += amount
        self.accounts[account_number]['transactions'].append(
            f"Deposit: {amount} THB ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        )

    def withdraw(self, account_number, amount):
        if self.accounts[account_number]['balance'] >= amount:
            self.accounts[account_number]['balance'] -= amount
            self.accounts[account_number]['transactions'].append(
                f"Withdraw: {amount} THB ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
            )
            return True
        else:
            return False

    def transfer(self, sender_account, receiver_account, amount):
        if (
            self.accounts[sender_account]['balance'] >= amount
            and receiver_account in self.accounts
        ):
            self.accounts[sender_account]['balance'] -= amount
            self.accounts[sender_account]['transactions'].append(
                f"Transfer to {receiver_account}: {amount} THB ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
            )
            self.accounts[receiver_account]['balance'] += amount
            self.accounts[receiver_account]['transactions'].append(
                f"Transfer from {sender_account}: {amount} THB ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
            )
            return True
        else:
            return False

    def get_balance(self, account_number):
        return self.accounts[account_number]['balance']

    def get_transactions(self, account_number):
        return self.accounts[account_number]['transactions']

class ATM:
    def __init__(self, atm_code, bank):
        self.atm_code = atm_code
        self.bank = bank
        self.current_user = None
        self.balance = 50000

    def read_card(self, card_number):
        if card_number in self.bank.accounts:
            account_info = self.bank.accounts[card_number]
            if 'expiry_date' in account_info and account_info['expiry_date'] > datetime.now():
                self.current_user = card_number
                return account_info['name']
            else:
                print("Card has expired.")
        else:
            return None

    def eject_card(self):
        self.current_user = None

    def check_pin(self, entered_pin):
        account_number = self.current_user
        if (
            account_number is not None
            and 'pin' in self.bank.accounts[account_number]
            and entered_pin == self.bank.accounts[account_number]['pin']
        ):
            return True
        else:
            return False

    def perform_transaction(self, transaction_type, *args):
        if transaction_type not in ['1', '2', '3']:
            print("Invalid transaction type.")
            return

        if not args:
            print("Missing arguments for transaction.")
            return

        if transaction_type == '1':
            self.balance += args[0]

            sender_balance_before = self.bank.get_balance(self.current_user)
            self.bank.deposit(self.current_user, *args)
            sender_balance_after = self.bank.get_balance(self.current_user)

            print(f"Deposit Successful!")
            print(f"Balance Before: {sender_balance_before} THB")
            print(f"Deposit Amount: {args[0]} THB")
            print(f"Balance After: {sender_balance_after} THB")
        elif transaction_type == '2':
            if (
                self.balance >= args[0]
                and self.bank.withdraw(self.current_user, *args)
            ):
                self.balance -= args[0]

                sender_balance_after = self.bank.get_balance(self.current_user)
                print(f"Withdrawal Successful!")
                print(f"Withdrawal Amount: {args[0]} THB")
                print(f"Balance After: {sender_balance_after} THB")
            else:
                print("Insufficient funds or ATM balance not enough.")
        elif transaction_type == '3':
            if len(args) >= 2:
                receiver_account = args[0]
                amount = args[1]

                if receiver_account not in self.bank.accounts:
                    print("Invalid recipient account.")
                    return

                sender_balance_before = self.bank.get_balance(self.current_user)
                receiver_balance_before = self.bank.get_balance(receiver_account)

                success = self.bank.transfer(
                    self.current_user, receiver_account, amount
                )

                if success:
                    sender_balance_after = self.bank.get_balance(self.current_user)
                    receiver_balance_after = self.bank.get_balance(receiver_account)

                    print(f"Transfer Successful!")
                    print(
                        f"Sender's Balance Before: {sender_balance_before} THB"
                    )
                    print(
                        f"Receiver's Balance Before: {receiver_balance_before} THB"
                    )
                    print(f"Transfer Amount: {amount} THB")
                    print(f"Sender's Balance After: {sender_balance_after} THB")
                    print(
                        f"Receiver's Balance After: {receiver_balance_after} THB"
                    )
                else:
                    print("Transfer failed. Check recipient account.")
            else:
                print("Missing arguments for transfer.")
        else:
            print("Invalid transaction type.")

    def display_summary(self):
        print("\nTransaction Summary:")
        for account_number in self.bank.accounts:
            transactions = self.bank.get_transactions(account_number)
            if transactions:
                print(f"\nAccount Number: {account_number}")
                print(f"User: {self.bank.accounts[account_number]['name']}")
                print("Transactions:")
                for transaction in transactions:
                    print(f"- {transaction}")

        print(f"\nATM Balance: {self.balance} THB")


class Admin:
    def __init__(self, bank, atm, password):
        self.bank = bank
        self.atm = atm
        self.__password = password

    def check_atm(self):
        return self.atm.balance

    def check_history(self):
        self.atm.display_summary()

    def login(self, entered_password):
        return entered_password == self.__password


# สร้างธนาคาร
bank = Bank("My Bank")

# สร้างบัญชี
expiry_date = datetime.now() + timedelta(days=365)
bank.create_account("5069", "Natthaphong", 60000, "5069", expiry_date)
bank.create_account("5178", "Warangkana", 1500, "5178", expiry_date)

# สร้างตู้ ATM
atm = ATM("123", bank)

# สร้าง Admin และกำหนดรหัสผ่าน
admin_password = "admin99"
admin = Admin(bank, atm, admin_password)

while True:
    insert_card = input("Insert your card? (yes/no): ").lower()

    if insert_card == 'yes':
        card_number = input("Enter card number: ")

        user_name = atm.read_card(card_number)

        if user_name:
            print(f"Card accepted. Welcome, {user_name}!")

            pin = input("Enter PIN: ")
            if atm.check_pin(pin):
                print("PIN Correct. Access granted.")
                transaction_type = input(
                    "Enter transaction type (1.deposit, 2.withdraw, 3.transfer): "
                )

                if transaction_type in ['1', '2', '3']:
                    try:
                        amount = float(input("Enter Money: "))
                    except ValueError:
                        print("Invalid amount. Please enter a valid number.")
                        continue

                    if transaction_type == '3':
                        receiver_account = input(
                            "Enter receiver's account number: "
                        )
                        success = atm.perform_transaction(
                            transaction_type, receiver_account, amount
                        )
                    else:
                        success = atm.perform_transaction(
                            transaction_type, amount
                        )

                    if success:
                        atm.display_summary()
                        print("\nDo you want to continue? (yes/no): ")
                    else:
                        print("The transaction was completed successfully.")
                else:
                    print("Invalid transaction type.")
            else:
                print("PIN Incorrect. Access denied.")
        else:
            print("Invalid card number. Please try again.")
    elif insert_card == 'no':
        print("Exiting ATM. Goodbye!")
        break
    elif insert_card == 'admin':
        entered_password = input("Enter admin password: ")
        if admin.login(entered_password):
            admin_option = input(
                "Enter admin option (1.check_atm/2.check_history): "
            ).lower()
            if admin_option == '1':
                atm_balance = admin.check_atm()
                print(f"ATM Balance: {atm_balance} THB")
            elif admin_option == '2':
                admin.check_history()
            else:
                print("Invalid admin option.")
        else:
            print("Incorrect admin password.")
    else:
        print("Invalid input. Please enter 'yes', 'no'")