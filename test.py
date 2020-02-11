import BankSystem_OOP

pgpe = BankSystem_OOP.PGPersistance()


a = BankSystem_OOP.CurrentAccount(1, 100, 100, '2020-02-04', 10, '2020-02-08', pgpe)
b = BankSystem_OOP.DepositAccount(1, 100, 100, '2020-02-10', 10, '2020-02-11', pgpe)
b.deposit(50)

print(b.current_balance)
print(b.last_interest_date)
print(b.opening_date)
print(b.opening_balance)
