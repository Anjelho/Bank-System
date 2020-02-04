from datetime import datetime
from datetime import timedelta
import psycopg2 as pg
import json
from decimal import *

def connect_to_postgres():
    """Returns a connection to the database.

    TODO: Remove hardcoded connection string
    """
    with open("config/config.json") as json_config:
        cfg = json.load(json_config)

    return pg.connect(cfg['localdb'])


class BalanceError(Exception):
    value = "Sorry you have only $%6.2f in your account"


class Account:
    """represents type of bank account """

    def __init__(self, customer_name: str, opening_date, account_number, balance=0):
        """ Constructor for bank account """
        self.customer_name = customer_name
        self.opening_date = datetime.strptime(opening_date, "%Y-%m-%d").date()
        self.account_number = account_number
        self.balance = balance

    @staticmethod
    def get_current_date():
        date = datetime.today().date()
        return date

    def deposit(self, deposit_amount):
        """ modifier/mutator to deposit to account """

        self.balance = self.balance + deposit_amount
        return self.balance

    def withdraw(self, withdraw_amount):
        """ modifier/mutator to withdraw from account """
        if self.balance >= withdraw_amount:
            self.balance = self.balance - withdraw_amount
        else:
            raise BalanceError(BalanceError.value % self.balance)

    def transfer(self, account, amount: float):
        try:
            self.withdraw(amount)
            account.deposit(amount)
        except BalanceError:
            print(BalanceError.value % self.balance)

    def get_balance(self):
        """ Accessor method for balance """
        return self.balance

    def set_balance(self, new_balance):
        """ modifier/mutator method for balance """

        self.balance = new_balance

    def display(self):
        """ helper/support method to display account info """
        print("Customer name:", self.customer_name)
        print("Opening date:", self.opening_date)
        print("Balance: ${0:.2f}".format(self.balance))


class CurrentAccount(Account):
    """ subclass for current account """

    def __init__(self, customer_name, opening_date, account_number, balance):
        """ constructor for current account """
        self.interest = 0
        self.account_type = 'Current Account'

        if datetime.strptime(opening_date, "%Y-%m-%d").date() < datetime.today().date():
            raise ValueError('Opening date cannot be earlier than Current day')
        elif account_number < 0 or balance < 0:
            raise ValueError('Account number or balance cannot be negative')
        else:
            super().__init__(customer_name, opening_date, account_number, balance)

    def display_monthly_statement(self):
        print("Current Account Monthly Statement")
        super().display()

    def display(self):
        super().display()
        print("Account No:", self.account_number)
        print("Account type:", self.account_type)
        print("Interest:", self.interest)

    def get_rate_of_interest(self):
        return self.interest


class DepositAccount(Account):  # inheritance
    """ subclass for deposit account """

    def __init__(self, customer_name, opening_date, account_number, term_date, interest: float, balance):
        """ constructor for Deposit account
         :param interest:
                percentage
         :param opening_date:
                :returns datetime.date
        :param term_date:
               :returns datetime.date"""

        self.account_type = 'Deposit Account'
        self.interest = interest
        self.term_date = datetime.strptime(term_date, "%Y-%m-%d").date()

        if datetime.strptime(term_date, "%Y-%m-%d").date() < datetime.today().date():
            raise ValueError('Term date cannot be earlier than Current day')

        elif datetime.strptime(opening_date, "%Y-%m-%d").date() < datetime.today().date():
            raise ValueError('Opening date cannot be earlier than Current day')

        elif account_number < 0 or balance < 0:
            raise ValueError('Account number or balance cannot be negative')

        else:
            super().__init__(customer_name, opening_date, account_number, balance)

    def get_term_date(self):
        return self.term_date.strftime("%Y-%m-%d")

    def set_term_date(self, value):
        self.term_date = datetime.strptime(value, "%Y-%m-%d").date()

    def get_rate_of_interest(self):
        return self.interest

    def display(self):
        super().display()
        print("Account No:", self.account_number)
        print("Account type:", self.account_type)
        print("Term date:", self.term_date)
        print("Interest: {}%".format(self.interest))

    def display_yearly_statement(self):
        self.set_balance(self.get_balance() * (1 + self.interest / 100))
        print("Deposit Account yearly Statement")
        super().display()

    def display_term_date(self):
        print('Current term date is: {}'.format(self.term_date))

    def withdraw(self, withdraw_amount):
        """ modifier/mutator to withdraw from account """

        if self.term_date == Account.get_current_date():
            return Account.withdraw(self, withdraw_amount)
        else:
            raise ValueError("You can withdraw only on term date!")

    def transfer(self, account, amount):
        if self.term_date == Account.get_current_date():
            return Account.transfer(self, account, amount)
        else:
            raise ValueError("You can transfer only on term date!")


d = DepositAccount('Shawn','2020-02-04', 1, '2021-02-03',0.1,1000)
c = CurrentAccount('Clown','2020-02-05', -1, 1000)


d.display()
#d.display_yearly_statement()
#d.transfer(c,100)
#c.display()
