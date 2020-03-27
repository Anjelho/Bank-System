from BankAccount import Bank

storage = Bank.PersistanceEngineFactory("Json")

a = Bank.CurrentAccount(4, 1000, '2020-01-30', 10, '2020-02-14', storage)
b = Bank.DepositAccount(2, 200, '2020-01-18', 10, '2020-02-10', '2020-02-13', storage)
a.persist_account()
#b.persist_account()
#a.withdraw(10,'shisha')
#a.persist_account_transactions()
#acc = storage.init_account_from_storage(1)
#acc2 = storage.init_account_from_storage(2)
#acc.transfer(10, acc2)
#acc.persist_account_transactions()
#print(acc.current_balance)
#print(acc2.current_balance)
#c.persist_account()
#acc = storage.init_account_from_storage(1)
#acc.deposit(200, 'dqdo')
#acc.persist_account_transactions()

#b.persist_account()
#a.transfer(10, b)
#a.persist_account_transactions()
