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


    def __init__(self, id, balance, opening_date, acctype, interest_rate, persistanceengine: "PersistanceEngine"):
        self.id = id
        self.balance = balance
        self.opening_date = opening_date
        self.interest_recalc_date = opening_date
        self.interest_rate = interest_rate
        self.persisanceengine = persistanceengine

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
        i = 1
        while i <= difference:
            self.balance = self.balance * (self.interest_rate/100+1)
            i += 1
        return self.balance


    def deposit(self, amount):
        self.balance += amount
        tr = Transaction(self.id, self.id, amount, 'deposit', date.today())


    def withdraw(self, amount):
        Account.days_between(self)
        if self.balance < amount:
            raise ValueError("Withdraw not possible. Not enough funds.")
        elif hasattr(self, 'term_date') and self.term_date > date.today():
            raise ValueError("It is a Deposit account. And the term_date is: " + str(self.term_date))
        else:
            self.balance -= amount
            tr = Transaction(self.id, self.id, amount, 'withdraw', date.today())
            self.interest_recalc_date = str(date.today())


    def transfer(self, amount, tgt):
        Account.days_between(self)
        if self.balance < amount:
            raise ValueError("Withdraw not possible. Not enough funds.")
        elif hasattr(self, 'term_date') and self.term_date > date.today():
            raise ValueError("It is a Deposit account.")
        else:
            self.balance -= amount
            tgt.balance += amount
            tr = Transaction(self.id, tgt.id, amount, 'transfer', date.today())
            self.interest_recalc_date = str(date.today())


    def displayAcc(self):
        #Account.days_between(self)
        print("Acc Nr: "+ str(self.id))
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
        if hasattr(self, 'id'):
            self.__acclist.append(self.id)
        if hasattr(self, 'balance'):
            self.__acclist.append(self.balance)
        if hasattr(self, 'opening_date'):
            self.__acclist.append(self.opening_date)
        if hasattr(self, 'term_date'):
            self.__acclist.append(self.term_date)
        if hasattr(self, 'interest_rate'):
            self.__acclist.append(self.interest_rate)
        if hasattr(self, 'interest_recalc_date'):
            self.__acclist.append(self.interest_recalc_date)
        if hasattr(self, 'type'):
            self.__acclist.append(self.type)
        print(self.__acclist)


class Transaction:

    __trlist: List["Transaction"]

    def getTrList(self):
        return self.__trlist


    def __init__(self, src, tgt, amount, type, transaction_date):
        self.src = src
        self.tgt = tgt
        self.amount = amount
        self.type = type
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
        q = '''INSERT INTO accounts (accnr, balance, interest_rate, acctype, interest_recalc_date, opening_date, term_date)
                        values({},{},{},{},{},{},{})'''.format(acc.id, acc.balance, acc.interest_rate, '\''+acc.type+'\'', '\''+acc.interest_recalc_date+'\'', '\''+acc.opening_date+'\'', '\''+str(acc.term_date)+'\'')
        cur = conn.cursor()
        print(q)
        cur.execute(q)
        conn.commit()
        conn.close()

    def persistTransaction(self, tr: "Transaction"):
        conn = PGPersistanceEngine.open()
        q = '''INSERT INTO transactions (source, target, amount, transaction_type, date)
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
