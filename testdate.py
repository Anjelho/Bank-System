import banky
import datetime
from datetime import datetime as dtm

def days_between(d1, d2):
    d1 = dtm.strptime(d1, "%Y-%m-%d")
    d2 = dtm.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

d = datetime.date(2019, 2 ,5)
x=days_between(str(banky.date.today()), str(datetime.date(2020, 2, 1)))
print(x)

d1 = dtm.strptime(str(self.interest_recalc_date), "%Y-%m-%d")
d2 = dtm.strptime(str(banky.date.today()), "%Y-%m-%d")

print(d1)
print(d2)