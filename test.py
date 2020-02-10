import banky

pgpe = banky.PGPersistanceEngine()
__trlist = []

a = banky.Account(1, 100, 100, '2020-02-04', 10, '2020-02-06', pgpe, __trlist)
#b = banky.Account(2, 200, '2020-01-18', 'd', 5, pgpe)

a.deposit(100)
a.deposit(100)
a.deposit(100)
print(a.current_balance, a.last_interest_date)