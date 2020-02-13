import Bank

pgpe = Bank.PersistanceEngineFactory("Postgres")

a = Bank.CurrentAccount(1, 100, '2020-02-13', 10)
b = Bank.DepositAccount(2, 100, '2020-02-13', 10, '2020-02-13')
b.withdraw(10)
b.persist_account_transactions(pgpe)
