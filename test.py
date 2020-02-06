import banky

pgpe = banky.PGPersistanceEngine()

a = banky.Account(1, 100, '2020-02-04', 'c', 100, pgpe)
b = banky.Account(2, 200, '2020-01-18', 'd', 5, pgpe)

a.persistAccount(pgpe)
b.persistAccount(pgpe)

a.withdraw(10)
b.deposit(20)
a.transfer(10,b)