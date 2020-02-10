import banky

pgpe = banky.PGPersistanceEngine()
__trlist = banky.TransactionList

a = banky.Account(1, 100, 100, '2020-02-04', 10, '2020-02-01', pgpe, __trlist)
b = banky.Account(2,100,100,'2020-02-10',10,'2020-02-05', pgpe, __trlist)
a.deposit(100)
print(a.current_balance, a.last_interest_date)