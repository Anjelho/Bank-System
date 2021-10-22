import bank

a = bank.Account(1, 100, '2020-01-25', 'c', 10, 'PGPersistanceEngine')
b = bank.Account(2, 200,'2020-01-18', 'd', 5, 'PGPersistanceEngine')

#a.displayAcc()
b.term_date = bank.date(2020, 1, 1)
b.interest_recalc_date = bank.date(2020, 1, 30)
#b.withdraw(450) 
b.displayAcc()

#print(str(bank.date(2020,1,25)))
#print(a.displayAcc())
#a.transfer(40, b)

#x = a.gettrList()
#print(x[2].amount)
#print(type(a.opening_date))
#bank.Account.displayAcc(a)
#bank.Account.displayAcc(b)

pe = bank.PGPersistanceEngine(1, 100, '2020-1-25', 10, 'c', '2020-5-16', '2020-2-4')
pe.persistAcc()