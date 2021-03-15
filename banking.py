from random import randint
import sqlite3


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

def check_db_table():
    sql = ''' 
    SELECT count(name) FROM sqlite_master WHERE type='table' AND name='card'
    '''
    cur.execute(sql)
    return cur.fetchone()[0]==1

def create_db_table():
    sql = '''
    CREATE TABLE card(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0
    );
    '''
    cur.execute(sql)
    conn.commit()

if not check_db_table():
    print('--creating table card in DB----')
    create_db_table()

def insert_table(number,pin,balance):
    sql = f'''
          INSERT INTO card(number, pin, balance) 
          VALUES ({str(number)}, {pin}, {balance});
          '''
    cur.execute(sql)
    conn.commit()

def find_account(card_number, pin):
    sql = f'''
    SELECT * from card WHERE number={card_number} and pin={pin}'''
    cur.execute(sql)
    return cur.fetchone()

def find_target_account(card_number):
    sql = f'''
    SELECT * from card WHERE number={card_number}'''
    cur.execute(sql)
    return cur.fetchone()

def change_balance(card_number,new_balance):
    sql = f'''
    UPDATE card
    SET balance={new_balance}
    WHERE number={card_number}
    '''
    cur.execute(sql)
    conn.commit()

def show_all_account():
    sql = f'''
    SELECT * from card
    '''
    cur.execute(sql)
    return cur.fetchall()

def check_balance(card_number):
    sql = f'''
    SELECT balance from card WHERE number={card_number}
    '''
    cur.execute(sql)
    return cur.fetchone()

def close_account(card_number, pin):
    sql = f'''
    DELETE FROM card WHERE number={card_number} AND pin={pin}
    '''
    cur.execute(sql)
    conn.commit()

def drop_table():
    sql = "DROP TABLE card"
    cur.execute(sql)
    conn.commit()

def remove_all_records():
    sql = "DELETE FROM card"
    cur.execute(sql)
    conn.commit()

def luhn_test(card_number):
    card_number_list = 1 * list(card_number)
    initial_number = card_number_list[0:(len(card_number_list)-1)]
    last_digit = int(card_number_list[-1])

    for i in range(len(initial_number)):
        initial_number[i] = int(initial_number[i])
        if i % 2 == 0:
            initial_number[i] *= 2
            if initial_number[i] > 9:
                initial_number[i] -= 9

    # calculate checksum according to LUHN
    mod_initial_number = sum(initial_number) % 10
    return mod_initial_number + last_digit == 10

class Account:

    def __init__(self):
        IIN = '400000'
        can = ''.join(["{}".format(randint(0, 9)) for num in range(0, 9)])
        # populate intial id (IIN + can) into list with initial id var
        initial_number = IIN + can

        # processing the id for LUHN
        luhn_check = 1 * list(initial_number)

        for i in range(len(initial_number)):
            luhn_check[i] = int(initial_number[i])
            if i % 2 == 0:
                luhn_check[i] *= 2
                if luhn_check[i] > 9:
                    luhn_check[i] -= 9

        # calculate checksum according to LUHN
        check = 10 - (sum(luhn_check) % 10)
        if check == 10:
            checksum = 0
        else:
            checksum = check

        # construct the card number
        number = str(initial_number) + str(checksum)
        self.number = int(number)

        # generate pin
        pin = randint(1000, 9999)
        self.pin = pin

        # generate initial balance
        self.balance = 0

choice = 1

while choice != 0:
    choice = int(input("\n1. Create an account\n2. Log into account\n0. Exit\n"))

    if choice == 1:
       new_account = Account()
       insert_table(new_account.number , new_account.pin, new_account.balance)
       print("\nYour card has been created")
       print("Your card number:")
       print(new_account.number)
       print('Your card PIN:')
       print(new_account.pin)

    elif choice == 2:
       input_number = input("Enter your card number:\n")
       input_pin = input("Enter you PIN:\n")
       found_account = find_account(input_number, input_pin)
       if not found_account:
           print("\nWrong card number or PIN!")

       else:
           print("\nYou have successfully logged in !\n")
           print(found_account)
           choice = 1
           while choice in [1,2,3]:
                   choice = int(input("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log Out\n0. Exit\n"))
                   if choice == 1:
                       found_balance = check_balance(input_number)
                       print(f"\nBalance: {found_balance[0]}\n")
                   elif choice == 2:
                       found_balance = check_balance(input_number)
                       income = int(input("Enter income:\n"))
                       new_balance = found_balance[0] + income
                       change_balance(found_account[1],new_balance)
                       print("\nIncome was added!")

                   elif choice == 3:
                       print("Transfer")
                       target_card = input("Enter card number:\n")
                       if not luhn_test(target_card):
                           print("Probably you made a mistake in the card number.")
                           print("Please try again!\n")

                       else:
                           if not find_target_account(target_card):
                               print("Such a card does not exist.\n")
                           else:
                               found_balance = check_balance(input_number)
                               transfer_amount = int(input("Enter how much money you want to transfer:\n"))
                               if transfer_amount <= found_balance[0]:
                                   #deduct source account balance
                                   src_balance = found_balance[0] - transfer_amount
                                   change_balance(found_account[1],src_balance)

                                   #add target account balance
                                   target_balance = check_balance(target_card)[0] + transfer_amount
                                   change_balance(target_card, target_balance)
                                   print("Success!")
                               else:
                                   print("Not enough money!\n")


                   elif choice == 4:
                       close_account(found_account[1],found_account[2])
                       print("\nThe account has been closed!\n")
                   elif choice == 5:
                       print("\nYou have successfully log out!")

print('Bye!')

