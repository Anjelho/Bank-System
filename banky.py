from typing import List
from abc import ABC, abstractmethod
from datetime import date
from datetime import timedelta
from datetime import datetime as dtm
import psycopg2 as pg
import json


class Account:

    __trlist: List["Account"]
    __persistanceengine: "PersistanceEngine"

    def __init__(self, acc_id, opening_balance, current_balance, opening_date, interest_rate, last_interest_date, persistance_engine: "PersistanceEngine", __trlist: []):
        self.acc_id = acc_id
        self.opening_balance = opening_balance
        self.current_balance = current_balance
        self.opening_date = opening_date
        self.interest_rate = interest_rate
        self.last_interest_date = last_interest_date
        self.persisance_engine = persistance_engine
        self.__trlist = []

    def deposit(self, amount):
        self.accrue_interest()
        self.current_balance += amount

    def withdraw(self, amount):
        if self.accrue_interest() < amount:
            raise ValueError("Not enough Money!")
        else:
            self.current_balance -= amount

    def transfer(self, amount, tgt):
        if self.accrue_interest() < amount:
            raise ValueError("Not enough Money!")
        else:
            self.current_balance -= amount
            tgt.current_balance += amount

    def persist_account(self, persistance_engine: "PersistanceEngine"):
        pass

    def accrue_interest(self):
        '''

        Transaction have to be done with this method.

        '''

        d1 = dtm.strptime(str(self.last_interest_date), "%Y-%m-%d")
        d2 = dtm.strptime(str(date.today()), "%Y-%m-%d")
        difference = abs((d2 - d1).days)
        current_balance = self.current_balance * ((self.interest_rate / 100 + 1) ** difference)
        self.current_balance = current_balance
        self.last_interest_date = date.today()
        return current_balance


class CurrentAccount(Account):

    def __init__(self, acc_id, opening_balance, current_balance, opening_date, interest_rate, persistance_engine: "PersistanceEngine", last_interest_date):
        super().__init__(acc_id, opening_balance, current_balance, opening_date, interest_rate, persistance_engine)
        self.last_interest_date = last_interest_date


class DepositAccount(Account):

    def __init__(self, acc_id, opening_balance, current_balance, opening_date, interest_rate, persistance_engine: "PersistanceEngine", term_date):
        super().__init__(acc_id, opening_balance, current_balance, opening_date, interest_rate, persistance_engine)
        self.term_date = term_date

    def withdraw(self, amount):
        if self.current_balance < amount:
            raise ValueError("Withdraw not possible. Not enough funds.")
        elif self.term_date > date.today():
            raise ValueError('It is a Deposit account and the term date is: {}'.format(self.term_date))
        else:
            self.current_balance -= amount

    def transfer(self, amount, tgt):
        if self.current_balance < amount:
            raise ValueError("Withdraw not possible. Not enough funds.")
        elif self.term_date > date.today():
            raise ValueError('It is a Deposit account and the term date is: {}'.format(self.term_date))
        else:
            self.current_balance -= amount
            tgt.current_balance += amount


class Transaction:

    def __init__(self, transaction_id, amount, transaction_date):
        self.transaction_id = transaction_id
        self.amount = amount
        self.transaction_date = transaction_date

    def add_to_history(self):
        pass


class BankTransfer(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, src, tgt):
        super().__init__(transaction_id, amount, transaction_date)
        self.src = src
        self.tgt = tgt

    def add_to_history(self):
        pass


class CashDeposit(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, tgt, metadata):
        super().__init__(transaction_id, amount, transaction_date)
        self.tgt = tgt
        self.metadata = metadata

    def add_to_history(self):
        pass


class CashWithdraw(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, src, metadata):
        super().__init__(transaction_id, amount, transaction_date)
        self.src = src
        self.metadata = metadata


class AccrueInterest(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, accrue_start, accrue_end, interest_granularity, interest_rate_per_granularity):
        super().__init__(transaction_id, amount, transaction_date)


class TransactionList:

    def __init__(self):
        pass


class PersistanceEngine(ABC):

    @abstractmethod
    def persistAcc(self, acc: "Account"):
        pass

    @abstractmethod
    def persistTransaction(self, tr: "Transaction"):
        pass

    @abstractmethod
    def getAllAcc(self):
        pass


class PGPersistanceEngine(PersistanceEngine):


    def open(self):
        """Returns a connection to the database.
        """

        with open("config/parameters.json") as json_config:
            cfg = json.load(json_config)

        return pg.connect(cfg['postgresql'])


    def persistAcc(self, acc: "Account"):
        conn = self.open()
        q_deposit = '''INSERT INTO accounts (accnr, balance, interest_rate, acctype, interest_recalc_date, opening_date, term_date)
                        values({},{},{},{},{},{},{})'''.format(acc.accid, acc.balance, acc.interest_rate, '\''+acc.type+'\'', '\''+acc.interest_recalc_date+'\'', '\''+acc.opening_date+'\'', '\''+str(acc.term_date)+'\'')

        q_current = '''INSERT INTO accounts (accnr, balance, interest_rate, acctype, interest_recalc_date, opening_date)
                        values({},{},{},{},{},{})'''.format(acc.accid, acc.balance, acc.interest_rate, '\''+acc.type+'\'', '\''+acc.interest_recalc_date+'\'', '\''+acc.opening_date+'\'')

        cur = conn.cursor()

        if acc.acctype == "c" or acc.acctype == "C":
            cur.execute(q_current)
        else:
            cur.execute(q_deposit)

        conn.commit()
        conn.close()


    def persistTransaction(self, tr: "Transaction"):
        conn = PGPersistanceEngine.open(self)
        q = '''INSERT INTO transactions (source, target, amount, transaction_type, datetime)
                                values({},{},{},'''.format(tr.src, tr.tgt, tr.amount) +'\''+tr.transaction_type +'\','+'\''+str(tr.transaction_date)+'\')'


        cur = conn.cursor()
        print(q)
        cur.execute(q)
        conn.commit()
        conn.close()


    def getAllAcc(self):
        pass


class JSONPersistanceEngine(PersistanceEngine):
    pass
