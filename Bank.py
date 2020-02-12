from typing import List
from abc import ABC, abstractmethod
from datetime import date
from datetime import timedelta
from datetime import datetime
import psycopg2 as pg
import json
import uuid


class Account(object):
    """Class that represents Bank account"""

    def __init__(self, account_num: int, balance: float, opening_date, interest_rate: float, persistance_engine: "Persistable"):
        self.account_num = account_num
        self.opening_balance = balance
        self.current_balance = balance
        self.opening_date = datetime.strptime(opening_date, "%Y-%m-%d").date()
        self.interest_rate = interest_rate
        self.last_interest_date = datetime.strptime(opening_date, "%Y-%m-%d").date()
        self.persistance_engine = persistance_engine
        self.transaction_list = TransactionList()

    def deposit(self, amount):
        """ modifier/mutator to deposit to account"""
        self.accrue_interest()
        self.current_balance += amount
        self.last_interest_date = datetime.now()

    def withdraw(self, amount):
        """ modifier/mutator to withdraw from account """
        if self.accrue_interest() < amount:
            raise ValueError("Not enough Money!")
        else:
            self.current_balance -= amount
            self.last_interest_date = datetime.now()

    def transfer(self, amount, target):
        """ modifier/mutator to transfer amount from one account to another """
        if self.accrue_interest() < amount:
            raise ValueError("Not enough Money!")
        else:
            self.current_balance -= amount
            target.current_balance += amount
            self.last_interest_date = datetime.now()

    def persist_account(self):
        """Method for persisting transactions in database or json file with selected persistance engine.
        Iterating over all transactions one by one, persisting transactions in new_transaction list,
        moving new transactions to history list and delete new_transaction list. """

        for tr in self.transaction_list.new_transactions:
            tr.persist()
            self.transaction_list.history_transactions.append(tr)
            self.transaction_list.new_transactions.remove(tr)

        Persistable.get_default_persistance_engine().persist_account(self)

    def accrue_interest(self):
        """Accrue interest calculation method."""

        d1 = datetime.strptime(str(self.last_interest_date), "%Y-%m-%d")
        d2 = datetime.strptime(str(date.today()), "%Y-%m-%d")
        difference = abs((d2 - d1).days)
        self.current_balance = self.current_balance * ((self.interest_rate / 100 + 1) ** difference)

    def create(self):
        """When account is being created it must be initialized from storage with init method."""
        pass

    def check_account(self, account_number):    # Must check for existing account on transfer method call
        """Checks for existing account by given account number"""
        pass

    def init(self):
        """Opposite of method persist - restore info for account from storage"""
        pass


class CurrentAccount(Account):
    """ subclass for current account"""
    def __init__(self, account_num, balance, opening_date, interest_rate, persistance_engine: "Persistable"):
        super().__init__(account_num, balance, opening_date, interest_rate, persistance_engine)

        if datetime.strptime(opening_date, "%Y-%m-%d").date() < datetime.today().date():
            raise ValueError('Opening date cannot be earlier than Current day')

        elif account_num < 0:
            raise ValueError('Account number cannot be negative')


class DepositAccount(Account):
    """ subclass for Deposit account"""
    def __init__(self, account_num, balance, opening_date, interest_rate, term_date, persistance_engine: "Persistable"):
        super().__init__(account_num, balance, opening_date, interest_rate, persistance_engine)
        self.term_date = datetime.strptime(term_date, "%Y-%m-%d").date()

        if datetime.strptime(term_date, "%Y-%m-%d").date() < datetime.today().date():
            raise ValueError('Term date cannot be earlier than Current day')

        elif datetime.strptime(opening_date, "%Y-%m-%d").date() < datetime.today().date():
            raise ValueError('Opening date cannot be earlier than Current day')

        elif account_num < 0:
            raise ValueError('Account number cannot be negative')

    def withdraw(self, amount):
        """ modifier/mutator to withdraw from Deposit account.
        Deposit accounts has additional restriction - Withdrawn is possible only on term date"""

        if self.current_balance < amount:
            raise ValueError("Withdraw not possible. Not enough funds.")
        elif self.term_date > date.today():
            raise ValueError('It is a Deposit account and the term date is: {}'.format(self.term_date))
        else:
            self.current_balance -= amount

    def transfer(self, amount, target):
        """ modifier/mutator to transfer amount from Deposit account to another account.
         Deposit accounts has additional restriction - transfer is possible only on term date"""

        if self.current_balance < amount:
            raise ValueError("Withdraw not possible. Not enough funds.")
        elif self.term_date > date.today():
            raise ValueError('It is a Deposit account and the term date is: {}'.format(self.term_date))
        else:
            self.current_balance -= amount
            target.current_balance += amount


class TransactionList:
    # new_transactions: transaction list for not persisted transactions. After, persist transactions goes to history list
    # and new list is being deleted.

    history_transactions: List["Transaction"]
    new_transactions: List["Transaction"]

    def read(self):
        for i in self.new_transactions:
            print(i)

    # Adding transaction

    def append(self, info):
        self.new_transactions.append(info)
        return TransactionList.read(self)

    def persist(self):
        for tr in self.new_transactions:
            tr.persist()


class Transaction:
    # Should call "Account" methods
    def __init__(self, transaction_id, amount, transaction_date):
        self.transaction_id = transaction_id
        self.amount = amount
        self.transaction_date = transaction_date

    def persist(self):
        pass

    # Should know what kind of object to pass to append method
    def add_to_history(self):
        pass


class BankTransfer(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, source, target):
        super().__init__(transaction_id, amount, transaction_date)
        self.source = source
        self.target = target

    def persist(self):
        Persistable.get_default_persistance_engine().persist_bank_transfer_transaction(self)
        pass

    def add_to_history(self):
        pass


class CashDeposit(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, target, metadata):
        super().__init__(transaction_id, amount, transaction_date)
        self.target = target
        self.metadata = metadata

    def persist(self):
        Persistable.get_default_persistance_engine().persist_cash_movement_transaction(self)
        pass

    def add_to_history(self):
        pass


class CashWithdraw(Transaction):
    def __init__(self, transaction_id, amount, transaction_date, source, metadata):
        super().__init__(transaction_id, amount, transaction_date)
        self.source = source
        self.metadata = metadata

    def persist(self):
        Persistable.get_default_persistance_engine().cash_movement_transaction(self)


class AccrueInterest(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, accrue_start, accrue_end, interest_granularity, interest_rate_per_granularity):
        super().__init__(transaction_id, amount, transaction_date)
        self.accrue_start = accrue_start
        self.accrue_end = accrue_end
        self.interest_granularity = interest_granularity
        self.interest_rate_per_granularity = interest_rate_per_granularity


class Persistable(ABC):

    def get_default_persistance_engine(self):
        pass

    @abstractmethod
    def persist_account(self, acc: "Account"):
        pass

    @abstractmethod
    def persist_bank_transfer_transaction(self, tr: "Transaction"):
        pass

    @abstractmethod
    def persist_cash_movement_transaction(self, tr: "Transaction"):
        pass

    @abstractmethod
    def persist_transaction_list(self, tr: "Transaction"):
        pass

    @abstractmethod
    def read_transaction_list(self, tr: "Transaction"):
        pass

    @abstractmethod
    def check_account(self, acc: "Account"):
        pass


class PGPersistance(Persistable):

    def open(self):
        """Returns a connection to the database."""

        with open("config/parameters.json.json") as json_config:
            cfg = json.load(json_config)

        return pg.connect(cfg['postgresql'])

    def persist_account(self, acc: "Account"):
        conn = PGPersistance.open(self)
        pass

    def persist_bank_transfer_transaction(self, tr: "Transaction"):
        conn = PGPersistance.open(self)
        pass

    def persist_cash_movement_transaction(self, tr: "Transaction"):
        pass

    def persist_transaction_list(self, tr: "Transaction"):
        conn = PGPersistance.open(self)
        pass

    def read_transaction_list(self, tr: "Transaction"):
        conn = PGPersistance.open(self)
        pass

    def check_account(self, acc: "Account"):
        pass


class JsonPersistance(Persistable):

    def open(self):
        pass
    def persist_account(self, acc: "Account"):
        pass

    def persist_transaction_list(self, tr: "Transaction"):
        pass

    def read_transaction_list(self, tr: "Transaction"):
        pass

    def check_account(self, acc: "Account"):
        pass

