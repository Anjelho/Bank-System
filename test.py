import Bank

pgpe = Bank.PGPersistance()


a = Bank.CurrentAccount(1, 100, '2020-02-12', 10, pgpe)
b = Bank.DepositAccount(2, 100, '2020-02-12', 10, '2021-02-11', pgpe)
a.deposit(50)

print(b.current_balance)
print(b.term_date)
print(b.opening_date)
print(b.opening_balance)

print(a.current_balance)
print(a.opening_date)
print(a.opening_balance)