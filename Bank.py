from abc import ABC, abstractmethod
from datetime import date
from datetime import datetime
import uuid
import psycopg2 as pg
import json


class Account:
    """Superclass representing Bank account."""

    def __init__(self, acc_id: int, balance: float, opening_date, interest_rate: float):

        self.acc_id = acc_id
        self.opening_balance = balance
        self.current_balance = balance
        self.opening_date = datetime.strptime(opening_date, "%Y-%m-%d").date()
        self.interest_rate = interest_rate
        self.accrue_interest_date = datetime.strptime(opening_date, "%Y-%m-%d").date()
        self.transaction_list = TransactionList()

    def deposit(self, amount):
        """
        The deposit method is valid for current and deposit accounts.
        amount - the amount of the deposit. (int)
        """

        self.check_balance()
        self.current_balance += amount
        tr = CashMovementDeposit(str(uuid.uuid4()), amount, datetime.now(), self.acc_id, 'deposit')
        self.transaction_list.new_transactions.append(tr)

    def withdraw(self, amount):
        """
        this withdraw method is valid only for the current accounts.
        """

        if self.check_balance() < amount:
            raise ValueError("Not enough Money!")
        else:
            self.current_balance -= amount

            tr = CashMovementWithdraw(str(uuid.uuid4()), amount, datetime.now(), self.acc_id, 'withdraw')

            self.transaction_list.new_transactions.append(tr)

    def transfer(self, amount, tgt):
        """
        This transfer method is valid only for the current accounts.
        """
        if self.check_balance() < amount:
            raise ValueError("Not enough Money!")
        else:
            tgt.accrue_interest()
            self.current_balance -= amount
            tgt.current_balance += amount

            tr = BankTransfer(str(uuid.uuid4()), amount, datetime.now(),
                              self.acc_id, tgt.acc_id, 'Bank Transfer')
            self.transaction_list.new_transactions.append(tr)

    def persist_account_transactions(self, persistance_engine):
        """
        Method for persisting transactions in database or json file with selected persistance engine.
        Iterating over all transactions one by one, persisting transactions in new_transaction list,
        moving new transactions to history list and clear new_transaction list.
        """

        for tr in self.transaction_list.new_transactions:
            tr.persist(persistance_engine)
            self.transaction_list.history_transactions.append(tr)
        self.transaction_list.new_transactions.clear()

    def check_balance(self):
        """
        Method to check the current balance after the accrual of the interest rate.
        """
        if self.accrue_interest_date != date.today():
            d1 = datetime.strptime(str(self.accrue_interest_date), "%Y-%m-%d")
            d2 = datetime.strptime(str(date.today()), "%Y-%m-%d")
            difference = abs((d2 - d1).days)

            current_balance = self.current_balance * ((self.interest_rate / 100 + 1) ** difference)

            self.current_balance = current_balance
            return current_balance
        else:
            return self.current_balance

    def accrue_interest(self, persistance_engine):
        """
        Transaction have to be executed with this method.
        """
        if self.accrue_interest_date != date.today():
            d1 = datetime.strptime(str(self.accrue_interest_date), "%Y-%m-%d")
            d2 = datetime.strptime(str(date.today()), "%Y-%m-%d")
            difference = abs((d2 - d1).days)

            current_balance = self.current_balance * pow((self.interest_rate / 100 + 1), difference) - self.current_balance

            self.current_balance = current_balance
            self.accrue_interest_date = date.today()

            tr = AccrueInterest(str(uuid.uuid4()), self.current_balance, self.accrue_interest_date, self.acc_id)
            tr.persist(persistance_engine)
            return current_balance
        else:
            return self.current_balance


class CurrentAccount(Account):

    """
    Child class on Account.
    accrue_interest_date - the date of last update on the account balance.
    """

    def __init__(self, acc_id, balance, opening_date, interest_rate):

        super().__init__(acc_id, balance, opening_date, interest_rate)

        self.account_type = 'Current'
        self.accrue_interest_date = datetime.strptime(opening_date, "%Y-%m-%d").date()

    def persist_account(self, persistance_engine):
        account = dict()
        account['acc_id'] = self.acc_id
        account['account_type'] = self.account_type
        account['current_balance'] = self.current_balance
        account['opening_balance'] = self.opening_balance
        account['interest_rate'] = self.interest_rate
        account['accrue_interest_date'] = self.accrue_interest_date
        account['opening_date'] = self.opening_date
        persistance_engine.persist_account(account)


class DepositAccount(Account):

    """
    Child class on Account.
    accrue_interest_date: the date of last update on the account balance.
    term_date: the date from which the account is able to withdraw money.
    """

    def __init__(self, acc_id, balance, opening_date, interest_rate, term_date):
        super().__init__(acc_id, balance, opening_date, interest_rate)

        self.accrue_interest_date = datetime.strptime(opening_date, "%Y-%m-%d").date()
        self.term_date = datetime.strptime(term_date, "%Y-%m-%d").date()
        self.account_type = 'Deposit'

    def withdraw(self, amount):

        """
        withdraw method only for deposit accounts.
        """

        if self.check_balance() < amount:
            raise ValueError("Withdraw not possible. Not enough funds.")
        elif self.term_date > date.today():
            raise ValueError('It is a Deposit account and the '
                             'term date is: {}'.format(self.term_date))
        else:
            self.current_balance -= amount

            tr = CashMovementWithdraw(str(uuid.uuid4()), amount, datetime.now(), self.acc_id, 'withdraw')
            self.transaction_list.new_transactions.append(tr)

    def transfer(self, amount, tgt):
        """
        this transfer method is valid only for deposit accounts.
        amount - amount to transfer (int)
        tgt - the target which will receive the amount (object)
        """

        if self.check_balance() < amount:
            raise ValueError("Withdraw not possible. Not enough funds.")
        elif self.term_date > date.today():
            raise ValueError('It is a Deposit account and the term date is: {}'.format(self.term_date))
        else:
            self.current_balance -= amount
            tgt.current_balance += amount

            tr = BankTransfer(str(uuid.uuid4()), amount, datetime.now(),
                              self.acc_id, tgt.acc_id, 'Bank Transfer')
            self.transaction_list.new_transactions.append(tr)

    def persist_account(self, persistance_engine):
        account = dict()
        account['acc_id'] = self.acc_id
        account['account_type'] = self.account_type
        account['current_balance'] = self.current_balance
        account['opening_balance'] = self.opening_balance
        account['interest_rate'] = self.interest_rate
        account['accrue_interest_date'] = self.accrue_interest_date
        account['opening_date'] = self.opening_date
        account['term_date'] = self.term_date
        account['account_type'] = self.account_type
        persistance_engine.persist_account(account)


class Transaction:

    def __init__(self, transaction_id, amount, transaction_date):
        self.transaction_id = transaction_id
        self.amount = amount
        self.transaction_date = transaction_date

    def add_to_history(self):
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

    def __init__(self, transaction_id, amount, transaction_date, src, metadata):
        super().__init__(transaction_id, amount, transaction_date)
        self.src = src
        self.metadata = metadata

    def persist(self, persistance_engine):
        persisted_data = dict()
        persisted_data['transaction_id'] = self.transaction_id
        persisted_data['amount'] = self.amount
        persisted_data['transaction_date'] = self.transaction_date
        persisted_data['src'] = self.src
        persisted_data['metadata'] = self.metadata
        persistance_engine.persist_cash_movement_deposit(persisted_data)


class CashMovementWithdraw(Transaction):

    def __init__(self, transaction_id, amount, transaction_date, src, metadata):
        super().__init__(transaction_id, amount, transaction_date)
        self.src = src
        self.metadata = metadata

    def persist(self, persistance_engine):
        persisted_data = dict()
        persisted_data['transaction_id'] = self.transaction_id
        persisted_data['amount'] = self.amount
        persisted_data['transaction_date'] = self.transaction_date
        persisted_data['src'] = self.src
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

    def append(self, trlist):
        pass

    def persist(self):
        for tr in self.new_transactions:
            tr.persist()


class PersistanceEngineFactory:

    __postgres_engine = None
    __json_engine = None

    def __new__(cls, engine_name: str):
        if engine_name == "Postgres":
            if PersistanceEngineFactory.__postgres_engine is None:
                PersistanceEngineFactory.__postgres_engine = object.__new__(cls)
                PersistanceEngineFactory.__postgres_engine.postgres = PGPersistanceEngine()
                return PersistanceEngineFactory.__postgres_engine.postgres
            else:
                return PersistanceEngineFactory.__postgres_engine.postgres
        elif engine_name == "Json":
            if PersistanceEngineFactory.__json_engine is None:
                PersistanceEngineFactory.__json_engine = object.__new__(cls)
                PersistanceEngineFactory.__json_engine.json = JSONPersistanceEngine()
                return PersistanceEngineFactory.__json_engine.json
            else:
                return PersistanceEngineFactory.__json_engine.json
        else:
            raise ValueError("Choose correct persistance engine")


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
    def accrue_interest_account_update(self, tr: dict):
        pass


class PGPersistanceEngine(PersistanceEngine):

    def open_engine(self):
        """
        Returns connection to the database.
        """

        with open("config/parameters.json") as json_config:
            cfg = json.load(json_config)

        return pg.connect(cfg['localdb'])

    def persist_cash_movement_deposit(self, tr: dict):
        conn = self.open_engine()
        q = '''INSERT INTO transactions (transaction_id, source, amount, transaction_type, datetime, metadata)
                                values('{}', '{}', {}, '{}', '{}', '{}')'''.format(tr['transaction_id'], tr['src'], tr['amount'], tr['metadata'], tr['transaction_date'], tr['src'])

        cur = conn.cursor()
        cur.execute(q)
        conn.commit()
        conn.close()

    def persist_cash_movement_withdraw(self, tr: dict):
        conn = self.open_engine()
        q = '''INSERT INTO transactions (transaction_id, source, amount, transaction_type, datetime, metadata)
        values('{}', '{}', {}, '{}', '{}', '{}')'''.format(tr['transaction_id'], tr['src'], tr['amount'], tr['metadata'], tr['transaction_date'], tr['src'])
        update_acc = '''UPDATE public.accounts SET current_balance = current_balance - {} WHERE acc_id = {}'''.format(tr['amount'], tr['src'])
        cur = conn.cursor()
        cur.execute(q)
        cur.execute(update_acc)
        conn.commit()
        conn.close()

    def persist_bank_transfer_transaction(self, tr: dict):
        conn = self.open_engine()
        insert = '''INSERT INTO transactions (transaction_id, source, amount, transaction_type, datetime)
                                    values('{}','{}', {}, '{}', '{}')'''.format(tr['transaction_id'], tr['src'],
                                                                                    tr['src'], tr['amount'],
                                                                                    tr['metadata'],
                                                                                    tr['transaction_date'])
        updatesrc = '''UPDATE public.accounts SET current_balance = current_balance - {} WHERE acc_id = {}'''.format(
            tr['amount'], tr['src'])
        updatetgt = '''UPDATE public.accounts SET current_balance = current_balance + {} WHERE acc_id = {}'''.format(
            tr['amount'], tr['src'])
        cur = conn.cursor()
        cur.execute(insert)
        cur.execute(updatesrc)
        cur.execute(updatetgt)
        conn.commit()
        conn.close()

    def persist_account(self, tr: dict):
        conn = self.open_engine()
        q = '''INSERT INTO public.accounts(acc_id, opening_balance, current_balance, interest_rate, account_type, accrue_interest_date, opening_date, term_date)
        VALUES ({}, {}, {},  {}, '{}', '{}', '{}', '{}');'''.format(tr['acc_id'], tr['opening_balance'], tr['current_balance'], tr['interest_rate'],
                                                                        tr['account_type'], tr['accrue_interest_date'],
                                                                        tr['opening_date'], tr['term_date'])

        cur = conn.cursor()
        cur.execute(q)
        conn.commit()
        conn.close()

    def accrue_interest_account_update(self, tr: dict):
        conn = self.open_engine()
        q = '''UPDATE public.accounts SET current_balance = {}, accrue_interest_date = '{}'
            WHERE acc_id = {}'''.format(tr['balance'], tr['date'], tr['acc_id'])

        cur = conn.cursor()
        cur.execute(q)
        conn.commit()
        conn.close()


class JSONPersistanceEngine(PersistanceEngine):

    def persist_cash_movement_transaction(self, tr: dict):
        pass

    def persist_bank_transfer_transaction(self, tr: dict):
        pass
