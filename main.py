import pickle
import os
import pathlib
from datetime import date
from datetime import timedelta


class Account:

    def __init__(self, accNo=0, interest=0, date=date.today(), deposit=0, type='', termdate=''):
        self.accNo = accNo
        self.date = date
        self.deposit = deposit
        self.interest = interest
        self.type = type
        self.termdate = termdate

    def createAccount(self):
        x = ''
        self.accNo = int(input("Enter the account no : "))
        self.interest = float(input("Enter the interest ratio : "))
        while x != "C" or x != "D":
            x = input('Please specify the account type [C/D]: ')
            if x == "C":
                self.type = x
                break
            elif x == "D":
                self.type = x
                self.termdate = date.today() + timedelta(days=365)
                break
        self.deposit = int(input("Enter The Initial amount : "))
        self.date = date.today()
        print("\n\n\nAccount Created")

    def showAccount(self):
        print("Account Number : ", self.accNo)
        print("Type of Account : ", self.type)
        print("Term date : ", self.termdate)
        print("Balance : ", self.deposit)

    def depositAmount(self, amount):
        self.deposit += amount

    def withdrawAmount(self, amount):
        self.deposit -= amount

    def report(self):
        print(self.accNo, " ", self.type, " ", self.deposit, " ", self.date, " ", self.termdate)

    def getAccountNo(self):
        return self.accNo

    def getAccountType(self):
        return self.type

    def getDeposit(self):
        return self.deposit


def intro():
    print("\t\t\t\t**********************")
    print("\t\t\t\tBANK MANAGEMENT SYSTEM")
    print("\t\t\t\t**********************")

    print("\t\t\t\tBrought To You By:")
    print("\t\t\t\tprojectworlds.in")
    input()


def writeAccount():
    account = Account()
    account.createAccount()
    writeAccountsFile(account)


def displayAll():
    file = pathlib.Path("accounts.data")
    if file.exists():
        infile = open('accounts.data', 'rb')
        mylist = pickle.load(infile)
        for item in mylist:
            print(item.accNo, " ", item.type, " ", item.deposit, " ", item.date, " ", item.termdate)
        infile.close()
    else:
        print("No records to display")


def displaySp(num):
    file = pathlib.Path("accounts.data")
    if file.exists():
        infile = open('accounts.data', 'rb')
        mylist = pickle.load(infile)
        infile.close()
        found = False
        for item in mylist:
            if item.accNo == num:
                print("Your account Balance is = ", item.deposit)
                found = True
    else:
        print("No records to Search")
    if not found:
        print("No existing record with this number")

    def transfer(self, amount, account):
        pass

def depositAndWithdraw(num1, num2, amount):
    file = pathlib.Path("accounts.data")
    if file.exists():
        infile = open('accounts.data', 'rb')
        mylist = pickle.load(infile)
        infile.close()
        os.remove('accounts.data')
        for item in mylist:
            while item.accNo == num1:
                if num2 == 1:
                    item.deposit += amount
                    print("Your account is updated")
                    break
                elif num2 == 2:
                    if amount <= item.deposit and item.type == 'C':
                        item.deposit -= amount
                    elif amount <= item.deposit and item.type == 'D':
                        print(f'You have a Deposit Account and Withdrawals are forbidden until '+str(item.termdate))
                        break
                    else:
                        print("You cannot withdraw larger amount!")
                        break
    else:
        print("No records to Search")
    outfile = open('newaccounts.data', 'wb')
    pickle.dump(mylist, outfile)
    outfile.close()
    os.rename('newaccounts.data', 'accounts.data')


def deleteAccount(num):
    file = pathlib.Path("accounts.data")
    if file.exists():
        infile = open('accounts.data', 'rb')
        oldlist = pickle.load(infile)
        infile.close()
        newlist = []
        for item in oldlist:
            if item.accNo != num:
                newlist.append(item)
        os.remove('accounts.data')
        outfile = open('newaccounts.data', 'wb')
        pickle.dump(newlist, outfile)
        outfile.close()
        os.rename('newaccounts.data', 'accounts.data')


def modifyAccount(num):
    file = pathlib.Path("accounts.data")
    if file.exists():
        infile = open('accounts.data', 'rb')
        oldlist = pickle.load(infile)
        infile.close()
        os.remove('accounts.data')
        for item in oldlist:
            if item.accNo == num:
                while item.type != "C" or item.type != "D":
                    item.type = input('Please specify the account type [C/D]: ')
                    if item.type == "C":
                        item.termdate = ''
                        item.deposit = int(input("Enter the Amount : "))
                        break
                    elif item.type == "D":
                        item.termdate = item.date + timedelta(days=365)
                        item.deposit = int(input("Enter the Amount : "))
                        break
        outfile = open('newaccounts.data', 'wb')
        pickle.dump(oldlist, outfile)
        outfile.close()
        os.rename('newaccounts.data', 'accounts.data')

def writeAccountsFile(account):
    file = pathlib.Path("accounts.data")
    if file.exists():
        infile = open('accounts.data', 'rb')
        oldlist = pickle.load(infile)
        oldlist.append(account)
        infile.close()
        os.remove('accounts.data')
    else:
        oldlist = [account]
    outfile = open('newaccounts.data', 'wb')
    pickle.dump(oldlist, outfile)
    outfile.close()
    os.rename('newaccounts.data', 'accounts.data')

# start of the program
ch = ''
num = 0
intro()

while ch != 9:
    # system("cls");
    print("\tMAIN MENU")
    print("\t1. NEW ACCOUNT")
    print("\t2. DEPOSIT AMOUNT")
    print("\t3. WITHDRAW AMOUNT")
    print("\t4. BALANCE ENQUIRY")
    print("\t5. ALL ACCOUNT HOLDER LIST")
    print("\t6. CLOSE AN ACCOUNT")
    print("\t7. MODIFY AN ACCOUNT")
    print("\t8. TRANSFER BETWEEN BANK ACCOUNTS")
    print("\t9. EXIT")
    print("\tSelect Your Option (1-8) ")
    ch = input()
    # system("cls");

    if ch == '1':
        writeAccount()
    elif ch == '2':
        num = int(input("\tEnter The account No. : "))
        amount = int(input("\tEnter the amount to deposit : "))
        depositAndWithdraw(num, 1, amount)
    elif ch == '3':
        num = int(input("\tEnter The account No. : "))
        amount = int(input("\tEnter the amount to deposit : "))
        depositAndWithdraw(num, 2, amount)
    elif ch == '4':
        num = int(input("\tEnter The account No. : "))
        displaySp(num)
    elif ch == '5':
        displayAll();
    elif ch == '6':
        num = int(input("\tEnter The account No. : "))
        deleteAccount(num)
    elif ch == '7':
        num = int(input("\tEnter The account No. : "))
        modifyAccount(num)
    elif ch == '8':
        num1 = int(input("\tEnter The account id to transfer money from : "))
        num2 = int(input("\tEnter The account id to transfer money to : "))
        amount = int(input("\tEnter the amount to deposit : "))
        #transfer(num1,num2,amount)
    elif ch == '9':
        print("\tThanks for using bank managemnt system")
        break
    else:
        print("Invalid choice")

    ch = input("Press 'Enter' to Continue\t")