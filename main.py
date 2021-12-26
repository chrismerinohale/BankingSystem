import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS card')
conn.commit()

cur.execute('''
            CREATE TABLE IF NOT EXISTS card(
            id INTEGER,
            number TEXT,
            pin TEXT,
            balance INTEGER DEFAULT 0)
            ''')
conn.commit()

bank_accounts = {}
PINs = []


# Function to get sum of digits
def get_sum(number):
    sum_of_digits = 0
    for digit in str(number):
        sum_of_digits += int(digit)

    return sum_of_digits


def luhn_algorithm(card_no):
    # Drop the last digit
    array_of_card_no = [int(x) for x in str(card_no)]
    original_array_of_cards = [int(x) for x in str(card_no)]
    card_no = card_no // 10

    # Slot card no. into an array
    array_of_card_no = [int(x) for x in str(card_no)]

    # Multiply odd arrays by 2
    for number in range(1, 16):
        if number % 2 != 0:
            array_of_card_no[number - 1] = array_of_card_no[number - 1] * 2

            # Subtract 9 from digits over 9
            if array_of_card_no[number - 1] > 9:
                array_of_card_no[number - 1] = array_of_card_no[number - 1] - 9

    # Append all the new numbers to luhn card no.
    luhn_algo_numbers = 0
    for number in range(1, 16):
        luhn_algo_numbers = int(str(luhn_algo_numbers) + str(array_of_card_no[number - 1]))

    # Get sum of lugn algo numbers
    sum_of_bank_card = get_sum(luhn_algo_numbers)
    modulo_value = sum_of_bank_card % 10

    remainder = 0
    if modulo_value != 0:
        remainder = (10 - sum_of_bank_card % 10)
    original_card_no_with_checksum = int(str(card_no) + str(remainder))

    sum_of_bank_card = get_sum(luhn_algo_numbers)
    modulo_value = sum_of_bank_card % 10
    return original_card_no_with_checksum


def return_to_start():
    user_inputs = int(input("1. Back to Start\n2. Exit\n"))
    if user_inputs == 1:
        pass
    elif user_inputs == 2:
        Recursion = False
    else:
        print("Sorry, that was an invalid command!")


def check_account_exists(bank_account):
    check_number = cur.execute('''
                SELECT COUNT(number)
                FROM card
                WHERE number = :bank_account''',
                               {"bank_account": bank_account})

    if check_number.fetchone()[0] > 0:
        check_number = True
    else:
        check_number = False
    return check_number


def check_pin_matches(bank_account, pin):
    check_pin = cur.execute('''
                SELECT COUNT(*)
                FROM card
                WHERE number = ?
                    AND PIN = ?''',
                            (bank_account, pin))

    if check_pin.fetchone()[0] == 0:
        check_pin = False
    else:
        check_pin = True
    return check_pin


def get_balance(bank_account):
    balance = cur.execute('''
                SELECT balance
                FROM card
                WHERE number = ?
                        ''', (bank_account,)).fetchone()[0]
    return balance


def close_account(bank_account):
    cur.execute('''
                DELETE
                FROM card
                WHERE number = ?
                        ''', [bank_account])
    conn.commit()


def add_income(bank_account, amount):
    cur.execute('''
                UPDATE card
                SET balance = balance + ?
                WHERE number = ?
                        ''', (amount, bank_account))
    conn.commit()
    print("Income was added!")


def reduce_income(bank_account, amount):
    cur.execute('''
                UPDATE card
                SET balance = balance - ?
                WHERE number = ?
                        ''', (amount, bank_account))
    conn.commit()


def transfer(from_bank_account, to_bank_account, number_of_checks):
    if check_account_exists(to_bank_account):
        transfer_amount_input = int(input("Enter how much money you want to transfer:"))

        if get_balance(from_bank_account) > transfer_amount_input:
            reduce_income(from_bank_account, transfer_amount_input)
            add_income(to_bank_account, transfer_amount_input)
            print("Success!")
        else:
            print("Not enough money!")

    else:
        number_of_checks = number_of_checks + 1
        if number_of_checks == 1:
            print("Probably you made a mistake in the card number. Please try again!")
        if number_of_checks > 1:
            print("Such a card does not exist.")
    return number_of_checks


class BankAccount:
    def __init__(self):
        self.card = 0
        self.PIN = 0
        self.balance = 0

    def create_account(self):
        self.card = int("400000" + str((random.randint(1000000000, 9999999999))))
        self.PIN = random.randint(1000, 9999)
        self.balance = 0

        self.card = luhn_algorithm(self.card)
        bank_accounts[self.card] = self.PIN

        cur.execute('''
                    INSERT INTO card(number, pin)
                    VALUES (?, ?)
                    ''', (self.card, self.PIN))
        conn.commit()

        print("Your card has been created\nYour card number:\n{}\nYour card PIN:\n{}\n".format(self.card, self.PIN))


Recursion = True
Recursion2 = True
while Recursion:
    number_of_checks = 0
    user_input = int(input("1. Create an account\n2. Log into account\n0. Exit\n"))

    if user_input == 1:
        NewAccount = BankAccount()
        NewAccount.create_account()


    elif user_input == 2:
        card_number_input = int(input("Enter your card number:\n"))

        # if card_number in bank_accounts.keys():
        if check_account_exists(card_number_input):
            PIN_input = int(input("Enter your PIN:\n"))

            if check_pin_matches(card_number_input, PIN_input):
                print("You have successfully logged in!\n")

                while Recursion2:

                    user_input = int(input("1. Balance\n2. Add income\n3. Do transfer"
                                           "\n4. Close account\n5. Log Out\n0. Exit\n"))

                    if user_input == 1:
                        print(get_balance(card_number_input))
                    elif user_input == 2:
                        amount = int(input("Enter income:\n"))
                        add_income(card_number_input, amount)

                    elif user_input == 3:
                        to_card_number_input = int(input("Enter card number:"))
                        number_of_checks = transfer(card_number_input, to_card_number_input, number_of_checks)
                    elif user_input == 4:
                        close_account(card_number_input)
                        print("The account has been closed!")
                    elif user_input == 5:
                        print("You have successfully logged out!\n")
                        Recursion2 = False
                    elif user_input == 0:
                        Recursion2 = False
                        Recursion = False
                    else:
                        print("Sorry, that was an invalid command!")
            else:
                print("wrong\n")
        else:
            print("wrong\n")

    elif user_input == 0:
        Recursion = False

    else:
        print("Sorry, that was an invalid command!")
