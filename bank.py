from datetime import date
from datetime import datetime
from datetime import timedelta
import datetime
import json

accfp = 'accounts.json'
history = 'history.json'

class Account:

    def __init__(self, accNo=0, deposit=0, type='', termdate='', interest=0):
        self.accNo = accNo
        self.deposit = deposit
        self.type = type
        self.termdate = termdate
        self.interest = interest

    def createAccount(self):
        x = ''
        self.accNo = str(int(input("Enter the account no : ")))
        self.interest = float(input("Enter the interest ratio : "))
        while x != "C" or x != "D":
            x = input('Please specify the account type [C/D]: ')
            if x == "C":
                self.type = x
                break
            elif x == "D":
                self.type = x
                termdata = date.today() + timedelta(days=365)
                self.termdate = str(termdata)
                break
        self.deposit = int(input("Enter The Initial amount : "))


    def saveAccount(self):

        with open(accfp, 'r') as infile:
            data = json.load(infile)
            if self.accNo in data.keys():
                print('There is already Bank Account ID associated with this number: ')
                print('Action Terminated.')
            elif self.type == "C":
                data[self.accNo] = {}
                data[self.accNo]['created'] = str(date.today())
                data[self.accNo]['deposit'] = self.deposit
                data[self.accNo]['interest'] = self.interest
                data[self.accNo]['type'] = self.type
                print("Current Account Created with ID: " + str(self.accNo))
            else:
                data[self.accNo] = {}
                data[self.accNo]['created'] = str(date.today())
                data[self.accNo]['deposit'] = self.deposit
                data[self.accNo]['interest'] = self.interest
                data[self.accNo]['type'] = self.type
                data[self.accNo]['termdate'] = str(self.termdate)
                print("Deposit Account Created with ID: " + str(self.accNo))

        with open(accfp,'w') as outfile:
            json.dump(data, outfile)

def record(type:str, amount, num1, num2=''):
        timestamp = datetime.datetime.now()

        with open(history, 'r') as infile:
            hist = json.load(infile)
            if not hist:
                hist["1"] = {}
            else:
                hist[str(int(list(hist.keys())[-1])+1)] = {}
            hist[str(int(list(hist.keys())[-1]))]['Time']= str(timestamp)
            hist[str(int(list(hist.keys())[-1]))]["Transaction Type"] = type
            hist[str(int(list(hist.keys())[-1]))]['AccountID'] = num1
            if type == "Transfer":
                hist[str(int(list(hist.keys())[-1]))]['RecipientID'] = num2
            hist[str(int(list(hist.keys())[-1]))]['amount'] = amount
        with open(history, 'w') as outfile:
            json.dump(hist, outfile)


def modifyAccount():
    num = str(input("Please choose the ID of the account to be modified: "))
    with open(accfp, 'r') as infile:
        data = json.load(infile)
        data[num]['type'] = input('Please choose the account type (C/D): ')
        data[num]['interest'] = float(input('Please choose the interest rate: '))
        data[num]['deposit'] = int(input('Enter the new deposit amount: '))
        if data[num]['type'] == "D":
            data[num]['termdate'] = str(date.today() + timedelta(days=365))
        else:
            del data[num]['termdate']
        print('Account Updated')

    with open(accfp, 'w') as outfile:
        json.dump(data, outfile)

def deleteAccount():
    num = str(input("Choose the ID of the account to be deleted: "))
    with open(accfp, 'r') as infile:
        data = json.load(infile)
        del data[num]

    with open(accfp, 'w') as outfile:
        json.dump(data, outfile)
    print('Account Deleted')

def writeAccount():
    account = Account()
    account.createAccount()
    account.saveAccount()


def depositAccount():
    num = str(input("Please select the AccId to deposit: "))
    amount = int(input("Please enter the amount to deposit: "))
    with open(accfp, 'r') as infile:
        data = json.load(infile)
        data[num]['deposit'] += amount

    with open(accfp, 'w') as outfile:
        json.dump(data, outfile)

    record("Deposit",amount,num)
    print('Deposit Accepted')

def withdrawAccount():
    num = str(input("Please select the AccId to withdraw money from: "))
    amount = int(input("Please enter the amount to withdraw: "))
    with open(accfp, 'r') as infile:
        data = json.load(infile)
        if data[num]['deposit'] < amount:
            print("You don't have enough money. You have: "+ data[num]['deposit'])
        elif 'termdate' in data[num] and data[num]['termdate'] != str(date.today()):
            print("It is a Deposit account. You can transfer money only on:"+ data[num]['termdate'])
        else:
            data[num]['deposit'] -= amount
            print("Amount withdraw successfully.")

    with open(accfp, 'w') as outfile:
        json.dump(data, outfile)

    record("Withdraw", amount, num)
    print('Amount withdraw end.')

def transferAccount():
    num1 = str(input("Please select the id to transfer money FROM: "))
    num2 = str(input("Please select the id to transfer money TO: "))
    amount = int(input("How much ?: "))
    with open(accfp, 'r') as infile:
        data = json.load(infile)
        if data[num1]['deposit'] < amount:
            print("You don't have enough money. You have: " + data[num1]['deposit'])
        elif 'termdate' in data[num1] and data[num1]['termdate'] != str(date.today()):
            raise ValueError("It is a Deposit account. You can transfer money only on:" + data[num]['termdate'])
        else:
            data[num1]['deposit'] -= amount
            data[num2]['deposit'] += amount
            print('Amount withdraw Successfully')
    with open(accfp, 'w') as outfile:
        json.dump(data, outfile)

    record("Transfer",amount,num1,num2)
    print('Transaction end.')

def balanceAccount():
    num = str(input("Please select the id to display the balance: "))
    with open(accfp, 'r') as infile:
        data = json.load(infile)
        print("The current balance of the account is: "+data[num]['deposit'])

def listAccount():
    with open(accfp, 'r') as infile:
        data = json.load(infile)
        dumped = json.dumps(data, indent=2)
        print(dumped)

ch = ''
num = 0

def intro():
    print("\t\t\t\t**********************")
    print("\t\t\t\tBANK MANAGEMENT SYSTEM")
    print("\t\t\t\t**********************")

    print("\t\t\t\tBrought To You By:")
    print("\t\t\t\tAngel Kostadinov")
    input()

intro()

while ch != 9:
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

    if ch == '1':
        writeAccount()
    elif ch == '2':
        depositAccount()
    elif ch == '3':
        withdrawAccount()
    elif ch == '4':
        balanceAccount()
    elif ch == '5':
        listAccount()
    elif ch == '6':
        deleteAccount()
    elif ch == '7':
        modifyAccount()
    elif ch == '8':
        transferAccount()
    elif ch == '9':
        print("\tThanks for using bank management system")
        break
    else:
        print("Invalid choice")

    ch = input("Press 'Enter' to Continue\t")
