from typing import List
from abc import ABC, abstractmethod
from datetime import date
from datetime import timedelta
from datetime import datetime as dtm
import psycopg2 as pg
import json

class Account:

    __acclist: List["Account"]
    __persistanceengine: "PersistanceEngine"


    def getAccList(self):
        return self.__acclist


    def __init__(self, accid, balance, opening_date, acctype, interest_rate, persistanceengine: "PersistanceEngine", term_date = None):
        self.accid = accid
        self.balance = balance
        self.opening_date = opening_date
        self.interest_recalc_date = opening_date
        self.interest_rate = interest_rate
        self.persisanceengine = persistanceengine
        self.term_date = term_date
        self.__trlist = []

        if acctype == "c" or acctype == "C":
            self.type = acctype.upper()
        elif acctype == "d" or acctype == "D":
            self.type = acctype.upper()
            self.term_date = date.today() + timedelta(days=365)
        else:
            raise ValueError("not a valid acc type please choose C or D !")


    def days_between(self):
        d1 = dtm.strptime(str(self.interest_recalc_date), "%Y-%m-%d")
        d2 = dtm.strptime(str(date.today()), "%Y-%m-%d")
        difference = abs((d2 - d1).days)
        current_balance = self.balance
        i = 1
        while i <= difference:
            current_balance = current_balance * (self.interest_rate/100+1)
            i += 1
        return current_balance



    def deposit(self, amount):
        self.balance += amount
        tr = Transaction(self.accid, self.accid, amount, 'deposit', date.today())
        self.__trlist.append(tr)


    def withdraw(self, amount):
        if Account.days_between(self) < amount:
            raise ValueError("Withdraw not possible. Not enough funds.")
        elif self.term_date is not None and self.term_date > date.today():
            raise ValueError("It is a Deposit account. And the term_date is: " + str(self.term_date))
        else:
            self.balance = Account.days_between(self) - amount
            tr = Transaction(self.accid, self.accid, amount, 'withdraw', date.today())
            self.interest_recalc_date = str(date.today())
            self.__trlist.append(tr)

    def transfer(self, amount, tgt):

        if Account.days_between(self) < amount:
            raise ValueError("Withdraw not possible. Not enough funds.")
        elif self.term_date is not None and self.term_date > date.today():
            raise ValueError("It is a Deposit account.")
        else:
            self.balance = Account.days_between(self) - amount
            tgt.balance += amount
            tr = Transaction(self.accid, tgt.id, amount, 'transfer', date.today())
            self.interest_recalc_date = str(date.today())
            self.__trlist.append(tr)

    def displayAcc(self):
        #Account.days_between(self)
        print("Acc Nr: "+ str(self.accid))
        print("Acc balance: " + str(self.balance))
        print("Acc opening_date: " + str(self.opening_date))
        if hasattr(self, 'term_date'):
            print("Acc term_date: " + str(self.term_date))
            print("Acc interest_rate: " + str(self.interest_rate))
        if hasattr(self, 'interest_recalc_date'):
            print("Acc recalculation date: " + str(self.interest_recalc_date))
        print("Acc type: " + self.type)


    def persistAccount(self, persistanceengine: "PersistanceEngine"):
        Account.days_between(self)
        persistanceengine.persistAcc(self)


class Transaction:

    __trlist: List["Transaction"]

    def getTrList(self):
        return self.__trlist


    def __init__(self, src, tgt, amount, transaction_type, transaction_date):
        self.src = src
        self.tgt = tgt
        self.amount = amount
        self.transaction_type = transaction_type
        self.transaction_date = transaction_date

        self.__trlist = []

        self.__trlist.append(src)
        self.__trlist.append(tgt)
        self.__trlist.append(amount)
        self.__trlist.append(type)


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

        if acc.type == "c" or acc.type == "C":
            cur.execute(q_current)
        else:
            cur.execute(q_deposit)

        conn.commit()
        conn.close()

    def persistTransaction(self, tr: "Transaction"):
        conn = PGPersistanceEngine.open()
        q_deposit = '''INSERT INTO transactions (source, target, amount, transaction_type, date)
                                values({},{},{},{},{})'''.format(tr.src, tr.tgt, tr.amount, tr.type, tr.transaction_date)


        cur = conn.cursor()
        print(q)
        cur.execute(q)
        conn.commit()
        conn.close()

    def getAllAcc(self):
        pass


class JSONPersistanceEngine(PersistanceEngine):
    pass
