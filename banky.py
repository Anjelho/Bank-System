from typing import List
from abc import ABC, abstractmethod
from datetime import date
from datetime import timedelta
from datetime import datetime as dtm
import psycopg2 as pg
import json


class Account:

    __persistanceengine: "PersistanceEngine"

    def __init__(self, account_num, opening_balance, current_balance, opening_date, interest_rate, last_interest_date, persistance_engine: "PersistanceEngine", transaction_list):
        self.account_num = account_num
        self.opening_balance = opening_balance
        self.current_balance = current_balance
        self.opening_date = opening_date
        self.interest_rate = interest_rate
        self.last_interest_date = last_interest_date
        self.persistance_engine = persistance_engine
        self.transaction_list = transaction_list

    def deposit(self, amount):
        """ modifier/mutator to deposit to account """
        self.accrue_interest()
        self.current_balance += amount

    def withdraw(self, amount):
        """ modifier/mutator to withdraw from account """
        if self.accrue_interest() < amount:
            raise ValueError("Not enough Money!")
        else:
            self.current_balance -= amount

    def transfer(self, amount, target):
        """ modifier/mutator to transfer amount from one account to another """
        if self.accrue_interest() < amount:
            raise ValueError("Not enough Money!")
        else:
            self.current_balance -= amount
            target.current_balance += amount

    def persist_account(self, persistance_engine: "PersistanceEngine"):
        pass

    def accrue_interest(self):
        """Transaction have to be done with this method."""
        d1 = dtm.strptime(str(self.last_interest_date), "%Y-%m-%d")
        d2 = dtm.strptime(str(date.today()), "%Y-%m-%d")
        difference = abs((d2 - d1).days)
        current_balance = self.current_balance * ((self.interest_rate / 100 + 1) ** difference)
        self.current_balance = current_balance
        self.last_interest_date = date.today()
        return current_balance

    def create(self):
        pass

    def check_account(self):
        pass

    def init(self):
        pass


class CurrentAccount(Account):
    """ subclass for current account"""
    def __init__(self, account_num, opening_balance, current_balance, opening_date, interest_rate, last_interest_date, persistance_engine: "PersistanceEngine", transaction_list):
        super().__init__(account_num, opening_balance, current_balance, opening_date, interest_rate, last_interest_date, persistance_engine, transaction_list)
        self.last_interest_date = last_interest_date


class DepositAccount(Account):
    """ subclass for Deposit account"""
    def __init__(self, account_num, opening_balance, current_balance, opening_date, interest_rate, term_date, persistance_engine: "PersistanceEngine", transaction_list):
        super().__init__(account_num, opening_balance, current_balance, opening_date, interest_rate, term_date, persistance_engine, transaction_list)
        self.term_date = term_date

    def withdraw(self, amount):
        if self.current_balance < amount:
            raise ValueError("Withdraw not possible. Not enough funds.")
        elif self.term_date > date.today():
            raise ValueError('It is a Deposit account and the term date is: {}'.format(self.term_date))
        else:
            self.current_balance -= amount

    def transfer(self, amount, target):
        if self.current_balance < amount:
            raise ValueError("Withdraw not possible. Not enough funds.")
        elif self.term_date > date.today():
            raise ValueError('It is a Deposit account and the term date is: {}'.format(self.term_date))
        else:
            self.current_balance -= amount
            target.current_balance += amount


class TransactionList:
    def __init__(self, history: List["Transaction"], new_transactions: List["Transaction"]):
        self.history = history
        self.new_transactions = new_transactions

    def read(self):
        pass

    def append(self):
        pass

    def persist(self):
        pass


class Transaction:

    def __init__(self, transaction_id, amount, transaction_date):
        self.transaction_id = transaction_id
        self.amount = amount
        self.transaction_date = transaction_date

    def add_to_history(self):
        pass


class BankTransfer(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, source, target):
        super().__init__(transaction_id, amount, transaction_date)
        self.source = source
        self.target = target

    def add_to_history(self):
        pass


class CashDeposit(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, target, metadata):
        super().__init__(transaction_id, amount, transaction_date)
        self.target = target
        self.metadata = metadata

    def add_to_history(self):
        pass


class CashWithdraw(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, source, metadata):
        super().__init__(transaction_id, amount, transaction_date)
        self.source = source
        self.metadata = metadata


class AccrueInterest(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, accrue_start, accrue_end, interest_granularity, interest_rate_per_granularity):
        super().__init__(transaction_id, amount, transaction_date)
        self.accrue_start = accrue_start
        self.accrue_end = accrue_end
        self.interest_granularity = interest_granularity
        self.interest_rate_per_granularity = interest_rate_per_granularity


class PersistanceEngine(ABC):

    @abstractmethod
    def persist_acc(self, acc: "Account"):
        pass

    @abstractmethod
    def persist_transaction(self, tr: "Transaction"):
        pass

    @abstractmethod
    def get_all_acc(self):
        pass


class PGPersistanceEngine(PersistanceEngine):

    def open(self):
        """Returns a connection to the database."""

        with open("config/parameters.json") as json_config:
            cfg = json.load(json_config)

        return pg.connect(cfg['postgresql'])

    def persist_acc(self, acc: "Account"):
        conn = self.open()
        pass

    def persist_transaction(self, tr: "Transaction"):
        conn = PGPersistanceEngine.open(self)
        pass

    def get_all_acc(self):
        pass


class JsonPersistanceEngine(PersistanceEngine):

    def persist_acc(self, acc: "Account"):
        pass

    def persist_transaction(self, tr: "Transaction"):
        pass

    def get_all_acc(self):
        pass

