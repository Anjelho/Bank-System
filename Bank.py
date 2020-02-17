from abc import ABC, abstractmethod
from datetime import date
from datetime import datetime as dtm
import datetime
import uuid
import psycopg2 as pg
import json


class Account:
    """
    Superclass which has child classes -> CurrentAccount and DepositAccount
    """

    def __init__(self, acc_id, balance, opening_date,
                 interest_rate, last_interest_date, persistance_engine):

        self.acc_id = acc_id
        self.opening_balance = balance
        self.current_balance = balance
        self.opening_date = datetime.datetime.strptime(opening_date, "%Y-%m-%d")
        self.interest_rate = interest_rate
        self.last_interest_date = last_interest_date
        self.transaction_list = TransactionList()
        self.persistance_engine = persistance_engine
        self.accrue_interest(persistance_engine)

    def deposit(self, amount, recipient):
        """
        The deposit method is valid for current and deposit accounts.
        amount - the amount of the deposit. (int)
        recipient - the person which deposits the money. (str)
        """

        self.current_balance += amount
        tr = CashMovementDeposit(str(uuid.uuid4()), amount,
                                 datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"), recipient,
                                 self.acc_id, 'deposit')

        self.transaction_list.new_transactions.append(tr)

    def withdraw(self, amount, recipient):
        """
        this withdraw method is valid only for the current accounts.
        """

        if self.current_balance < amount:
            raise ValueError("Not enough Money!")
        else:
            self.current_balance -= amount

            tr = CashMovementWithdraw(str(uuid.uuid4()), amount,
                                      datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"),
                                      recipient, self.acc_id, 'withdraw')

            self.transaction_list.new_transactions.append(tr)

    def transfer(self, amount, tgt):
        """
        This transfer method is valid only for the current accounts.
        """
        if self.current_balance < amount:
            raise ValueError("Not enough Money!")
        else:
            self.current_balance -= amount
            tgt.current_balance += amount

            tr = BankTransfer(str(uuid.uuid4()), amount,
                              datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"),
                              self.acc_id, tgt.acc_id, 'Bank Transfer')

            self.transaction_list.new_transactions.append(tr)

    def persist_account_transactions(self):
        """
        Method for persisting transactions in database or json file with selected persistance engine.
        Iterating over all transactions one by one, persisting transactions in new_transaction list,
        moving new transactions to history list and delete new_transaction list.
        """

        for tr in self.transaction_list.new_transactions:
            tr.persist(self.persistance_engine)
            self.transaction_list.history_transactions.append(tr)

        self.transaction_list.new_transactions.clear()

    def accrue_interest(self, persistance_engine):
        """
        Transaction have to be executed with this method.
        """
        if self.last_interest_date != date.today():
            d1 = dtm.strptime(str(self.last_interest_date), "%Y-%m-%d")
            d2 = dtm.strptime(str(date.today()), "%Y-%m-%d")
            difference = abs((d2 - d1).days)

            current_balance = self.current_balance * ((self.interest_rate / 100 + 1) ** difference)

            self.current_balance = current_balance
            self.last_interest_date = date.today()

            tr = AccrueInterest(str(uuid.uuid4()), self.current_balance, self.last_interest_date, self.acc_id)
            tr.persist(persistance_engine)
            return current_balance
        else:
            return self.current_balance


class CurrentAccount(Account):
    """
    Child class on Account.
    last_interest_date - the date of last update on the account balance.
    """

    def __init__(self, acc_id, balance, opening_date,
                 interest_rate, last_interest_date, persistance_engine):
        super().__init__(acc_id, balance, opening_date,
                         interest_rate, last_interest_date, persistance_engine)

        self.last_interest_date = datetime.datetime.strptime(last_interest_date, "%Y-%m-%d")

    def persist_account(self):
        account = dict()
        account['acc_id'] = self.acc_id
        account['current_balance'] = self.current_balance
        account['opening_balance'] = self.opening_balance
        account['interest_rate'] = self.interest_rate
        account['acc_type'] = 'C'
        account['interest_date'] = datetime.datetime.strftime(self.last_interest_date, "%Y-%m-%d")
        account['opening_date'] = datetime.datetime.strftime(self.opening_date, "%Y-%m-%d")
        account['term_date'] = '1999-01-01'
        self.persistance_engine.persist_account(account)


class DepositAccount(Account):
    """
    Child class on Account.
    last_interest_date: the date of last update on the account balance.
    term_date: the date from which the account is able to withdraw money.
    """

    def __init__(self, acc_id, balance, opening_date,
                 interest_rate, term_date, last_interest_date, persistance_engine):

        super().__init__(acc_id, balance, opening_date,
                         interest_rate, last_interest_date, persistance_engine)

        self.term_date = datetime.datetime.strptime(term_date, "%Y-%m-%d")
        self.last_interest_date = datetime.datetime.strptime(last_interest_date, "%Y-%m-%d")

    def withdraw(self, amount, recipient):

        """
        withdraw method only for deposit accounts.
        """

        if self.current_balance < amount:
            raise ValueError("Withdraw not possible. Not enough funds.")
        elif self.term_date > date.today():
            raise ValueError('It is a Deposit account and the '
                             'term date is: {}'.format(self.term_date))
        else:
            self.current_balance -= amount

            tr = CashMovementWithdraw(str(uuid.uuid4()), amount,
                                      datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"),
                                      recipient, self.acc_id, 'withdraw')

            self.transaction_list.new_transactions.append(tr)

    def transfer(self, amount, tgt):
        """
        this transfer method is valid only for deposit accounts.
        amount - amount to transfer (int)
        tgt - the target which will receive the amount (object)
        """

        if self.current_balance < amount:
            raise ValueError("Withdraw not possible. Not enough funds.")
        elif self.term_date > date.today():
            raise ValueError('It is a Deposit account and the term date is: {}'.format(self.term_date))
        else:
            self.current_balance -= amount
            tgt.accrue_interest(self.persistance_engine)
            tgt.current_balance += amount

            tr = BankTransfer(str(uuid.uuid4()), amount,
                              datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"),
                              self.acc_id, tgt.acc_id, 'Bank Transfer')

            self.transaction_list.new_transactions.append(tr)

    def persist_account(self):
        account = dict()
        account['acc_id'] = self.acc_id
        account['current_balance'] = self.current_balance
        account['opening_balance'] = self.opening_balance
        account['interest_rate'] = self.interest_rate
        account['acc_type'] = 'D'
        account['interest_date'] = datetime.datetime.strftime(self.last_interest_date, "%Y-%m-%d")
        account['opening_date'] = datetime.datetime.strftime(self.opening_date, "%Y-%m-%d")
        account['term_date'] = datetime.datetime.strftime(self.term_date, "%Y-%m-%d")
        self.persistance_engine.persist_account(account)


class Transaction:

    def __init__(self, transaction_id, amount, transaction_date):
        self.transaction_id = transaction_id
        self.amount = amount
        self.transaction_date = transaction_date

    def persist(self, persistance_engine):
        pass


class BankTransfer(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, src, tgt, metadata):
        super().__init__(transaction_id, amount, transaction_date)
        self.src = src
        self.tgt = tgt
        self.metadata = metadata

    def persist(self, persistance_engine):
        persisted_data = dict()
        persisted_data['transaction_id'] = self.transaction_id
        persisted_data['amount'] = self.amount
        persisted_data['transaction_date'] = self.transaction_date
        persisted_data['src'] = self.src
        persisted_data['tgt'] = self.tgt
        persisted_data['metadata'] = self.metadata
        persistance_engine.persist_bank_transfer_transaction(persisted_data)


class CashMovementDeposit(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, src, tgt, metadata):
        super().__init__(transaction_id, amount, transaction_date)
        self.src = src
        self.tgt = tgt
        self.metadata = metadata

    def persist(self, persistance_engine):
        persisted_data = dict()
        persisted_data['transaction_id'] = self.transaction_id
        persisted_data['amount'] = self.amount
        persisted_data['transaction_date'] = self.transaction_date
        persisted_data['src'] = self.src
        persisted_data['tgt'] = self.tgt
        persisted_data['metadata'] = self.metadata
        persistance_engine.persist_cash_movement_deposit(persisted_data)


class CashMovementWithdraw(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, src, tgt, metadata):
        super().__init__(transaction_id, amount, transaction_date)
        self.src = src
        self.tgt = tgt
        self.metadata = metadata

    def persist(self, persistance_engine):
        persisted_data = dict()
        persisted_data['transaction_id'] = self.transaction_id
        persisted_data['amount'] = self.amount
        persisted_data['transaction_date'] = self.transaction_date
        persisted_data['src'] = self.src
        persisted_data['tgt'] = self.tgt
        persisted_data['metadata'] = self.metadata
        persistance_engine.persist_cash_movement_withdraw(persisted_data)


class AccrueInterest(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, acc_id):
        super().__init__(transaction_id, amount, transaction_date)
        self.acc_id = acc_id

    def persist(self, persistance_engine):
        persisted_data = dict()
        persisted_data['balance'] = self.amount
        persisted_data['date'] = self.transaction_date
        persisted_data['acc_id'] = self.acc_id
        persistance_engine.accrue_interest_account_update(persisted_data)


class TransactionList:

    def __init__(self):
        self.history_transactions = []
        self.new_transactions = []

    def read(self, new_or_history):
        if new_or_history == 'new':
            i = len(self.new_transactions) - 1
            print(self.new_transactions[i])
        elif new_or_history == 'history':
            i = len(self.history_transactions) - 1
            print(self.history_transactions[i])
        else:
            raise ValueError("Choose 'new' or 'history'.")

    def append(self, transaction):
        pass

    def persist(self):
        for tr in self.new_transactions:
            tr.persist()


class PersistanceEngineFactory:
    postgres_engine = None
    json_engine = None

    def __new__(cls, engine_name):
        if engine_name == "Postgres":
            if PersistanceEngineFactory.postgres_engine is None:
                PersistanceEngineFactory.postgres_engine = object.__new__(cls)
                PersistanceEngineFactory.postgres_engine.postgres = PGPersistanceEngine()
                return PersistanceEngineFactory.postgres_engine.postgres
            else:
                return PersistanceEngineFactory.postgres_engine.postgres
        elif engine_name == "Json":
            if PersistanceEngineFactory.json_engine is None:
                PersistanceEngineFactory.json_engine = object.__new__(cls)
                PersistanceEngineFactory.json_engine.json = JSONPersistanceEngine()
                return PersistanceEngineFactory.json_engine.json
            else:
                return PersistanceEngineFactory.json_engine.json
        else:
            raise ValueError('Choose correct persistance engine')


class PersistanceEngine(ABC):

    @abstractmethod
    def persist_cash_movement_deposit(self, tr: dict):
        pass

    @abstractmethod
    def persist_cash_movement_withdraw(self, tr: dict):
        pass

    @abstractmethod
    def persist_bank_transfer_transaction(self, tr: dict):
        pass

    @abstractmethod
    def persist_account(self, tr: dict):
        pass

    @abstractmethod
    def init_account_from_storage(self, acc):
        pass


class PGPersistanceEngine(PersistanceEngine):
    """
    This class will manage a local Postgresql database
    with 2 tables (accounts and transactions)
    """

    @staticmethod
    def open_engine():
        """
        Returns connection to the database.
        """

        with open("config/parameters.json") as json_config:
            cfg = json.load(json_config)

        return pg.connect(cfg['localdb'])

    def persist_cash_movement_deposit(self, tr: dict):
        conn = self.open_engine()
        q = '''INSERT INTO transactions (transaction_id, source, target, amount, transaction_type, datetime, metadata)
            values('{}', '{}', {}, {}, '{}', '{}', '{}')'''.format(tr['transaction_id'], tr['tgt'], tr['tgt'],
                                                                   tr['amount'], tr['metadata'], tr['transaction_date'],
                                                                   tr['src'])

        update_acc = '''UPDATE public.accounts SET current_balance = current_balance + {} WHERE accnr = {}'''.format(
            tr['amount'], tr['tgt'])
        cur = conn.cursor()
        cur.execute(q)
        cur.execute(update_acc)
        conn.commit()
        conn.close()

    def persist_cash_movement_withdraw(self, tr: dict):
        conn = self.open_engine()
        q = '''INSERT INTO transactions (transaction_id, source, target, amount, transaction_type, datetime, metadata)
                                values('{}', '{}', {}, {}, '{}', '{}', '{}')'''.format(tr['transaction_id'], tr['tgt'],
                                                                                       tr['tgt'], tr['amount'],
                                                                                       tr['metadata'],
                                                                                       tr['transaction_date'],
                                                                                       tr['src'])
        update_acc = '''UPDATE public.accounts SET current_balance = current_balance - {} WHERE accnr = {}'''.format(
            tr['amount'], tr['tgt'])
        cur = conn.cursor()
        cur.execute(q)
        cur.execute(update_acc)
        conn.commit()
        conn.close()

    def persist_bank_transfer_transaction(self, tr: dict):
        conn = self.open_engine()
        insert = '''INSERT INTO transactions (transaction_id, source, target, amount, transaction_type, datetime)
                                values('{}','{}', {}, {}, '{}', '{}')'''.format(tr['transaction_id'], tr['src'],
                                                                                tr['tgt'], tr['amount'], tr['metadata'],
                                                                                tr['transaction_date'])
        update_source = '''UPDATE public.accounts SET current_balance = current_balance - {} WHERE accnr = {}'''.format(
            tr['amount'], tr['src'])
        update_target = '''UPDATE public.accounts SET current_balance = current_balance + {} WHERE accnr = {}'''.format(
            tr['amount'], tr['tgt'])
        cur = conn.cursor()
        cur.execute(insert)
        cur.execute(update_source)
        cur.execute(update_target)
        conn.commit()
        conn.close()

    def persist_account(self, tr: dict):
        conn = self.open_engine()
        q = '''INSERT INTO public.accounts(accnr, opening_balance, current_balance, interest_rate, acctype, interest_recalc_date, opening_date, term_date)
        VALUES ({}, {}, {},  {}, '{}', '{}', '{}', '{}');'''.format(tr['acc_id'], tr['opening_balance'],
                                                                    tr['current_balance'], tr['interest_rate'],
                                                                    tr['acc_type'], tr['interest_date'],
                                                                    tr['opening_date'], tr['term_date'])

        cur = conn.cursor()
        cur.execute(q)
        conn.commit()
        conn.close()

    def accrue_interest_account_update(self, tr: dict):
        conn = self.open_engine()
        q = '''UPDATE public.accounts SET current_balance = {}, interest_recalc_date = '{}'
        WHERE accnr = {}'''.format(tr['balance'], tr['date'], tr['acc_id'])

        cur = conn.cursor()
        cur.execute(q)
        conn.commit()
        conn.close()

    def init_account_from_storage(self, acc):
        conn = self.open_engine()
        q = '''select accnr, current_balance, interest_rate, acctype, interest_recalc_date, 
        opening_date, term_date, opening_balance from accounts WHERE accnr = {}'''.format(acc)

        cur = conn.cursor()
        cur.execute(q)
        rows = cur.fetchall()

        for row in rows:
            accnr = row[0]
            current_balance = row[1]
            interest_rate = row[2]
            acctype = row[3]
            interest_date = row[4]
            opening_date = row[5]
            term_date = row[6]
            if acctype == 'C':
                acc = CurrentAccount(accnr, current_balance, str(opening_date), interest_rate, str(interest_date), PersistanceEngineFactory('Postgres'))
                return acc
            elif acctype == 'D':
                acc = DepositAccount(accnr, current_balance, str(opening_date), interest_rate, str(term_date), str(interest_date), PersistanceEngineFactory('Postgres'))
                return acc

        conn.commit()
        conn.close()


class JSONPersistanceEngine(PersistanceEngine):

    def open_transactions(self):
        with open('config/transactions.json', 'r') as infile:
            account = json.load(infile)
        return account

    def save_transactions(self, data):
        with open('config/transactions.json', 'w') as outfile:
            json.dump(data, outfile)

    def open_accounts(self):
        with open('config/accounts.json', 'r') as infile:
            account = json.load(infile)
        return account

    def save_accounts(self, data):
        with open('config/accounts.json', 'w') as outfile:
            json.dump(data, outfile)

    def persist_account(self, acc: dict):
        account = self.open_accounts()
        account[acc['acc_id']] = acc

        self.save_accounts(account)

    def persist_cash_movement_deposit(self, tr: dict):
        account = self.open_accounts()
        transaction = self.open_transactions()
        transaction[tr['transaction_id']] = {}
        transaction[tr['transaction_id']]['src'] = tr['src']
        transaction[tr['transaction_id']]['tgt'] = tr['tgt']
        transaction[tr['transaction_id']]['datetime'] = tr['transaction_date']
        transaction[tr['transaction_id']]['amount'] = tr['amount']
        transaction[tr['transaction_id']]['transaction_type'] = tr['metadata']
        account[str(tr['tgt'])]['current_balance'] += tr['amount']
        account[str(tr['tgt'])]['interest_date'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        self.save_accounts(account)
        self.save_transactions(transaction)

    def persist_cash_movement_withdraw(self, tr: dict):
        account = self.open_accounts()
        transaction = self.open_transactions()
        transaction[tr['transaction_id']] = {}
        transaction[tr['transaction_id']]['src'] = tr['src']
        transaction[tr['transaction_id']]['tgt'] = tr['tgt']
        transaction[tr['transaction_id']]['datetime'] = tr['transaction_date']
        transaction[tr['transaction_id']]['amount'] = tr['amount']
        transaction[tr['transaction_id']]['transaction_type'] = tr['metadata']
        account[str(tr['tgt'])]['current_balance'] -= tr['amount']
        account[str(tr['tgt'])]['interest_date'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        self.save_accounts(account)
        self.save_transactions(transaction)

    def persist_bank_transfer_transaction(self, tr: dict):
        account = self.open_accounts()
        transaction = self.open_transactions()
        transaction[tr['transaction_id']] = {}
        transaction[tr['transaction_id']]['src'] = tr['src']
        transaction[tr['transaction_id']]['tgt'] = tr['tgt']
        transaction[tr['transaction_id']]['datetime'] = tr['transaction_date']
        transaction[tr['transaction_id']]['amount'] = tr['amount']
        transaction[tr['transaction_id']]['transaction_type'] = tr['metadata']
        account[str(tr['tgt'])]['current_balance'] += tr['amount']
        account[str(tr['tgt'])]['interest_date'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        account[str(tr['src'])]['current_balance'] -= tr['amount']
        account[str(tr['src'])]['interest_date'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        self.save_accounts(account)
        self.save_transactions(transaction)

    def init_account_from_storage(self, id):
        account = self.open_accounts()
        acc = account.get(id)
        acc_id = acc['acc_id']
        current_balance = acc['current_balance']
        interest_rate = acc['interest_rate']
        acc_type = acc['acc_type']
        interest_date = acc['interest_date']
        opening_date = acc['opening_date']
        term_date = acc['term_date']

        if acc_type == "C":
            acc = CurrentAccount(acc_id, current_balance, opening_date, interest_rate, interest_date, PersistanceEngineFactory('Json'))
            return acc
        else:
            acc = DepositAccount(acc_id, current_balance, opening_date, interest_rate, term_date, interest_date, PersistanceEngineFactory('Json'))
            return acc

    def accrue_interest_account_update(self, tr: dict):
        pass
