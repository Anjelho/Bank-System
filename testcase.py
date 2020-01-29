from datetime import date
from datetime import timedelta

class Account:

    def __init__(self, accNo=0, date=date.today(), deposit=0, type='', termdate=''):
        self.accNo = accNo
        self.date = date
        self.deposit = deposit
        self.type = type
        self.termdate = termdate

x=Account(1,date.today(),deposit=300,type='C',termdate='')

print(x.type)    
