import banky

pgpe = banky.PGPersistanceEngine()

a = banky.Account(6, 100, '2020-02-04', 'c', 100, pgpe)
b = banky.Account(7, 200, '2020-01-18', 'd', 5, pgpe)

a.days_between()
a.withdraw(100)
a.displayAcc()