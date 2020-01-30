from datetime import date
from datetime import timedelta

accounts = {}
accounts["AccNr"] = {}
accounts["AccNr"]["created"] = str(date.today())
accounts['AccNr']['deposit'] = "500"
accounts['AccNr']['interest'] = "5.5"
accounts['AccNr']['type'] = "C"
accounts['AccNr']['termdate'] = "20-02-21"

print(accounts)
