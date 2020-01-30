import pandas as pd
import json
import numpy as np
history = 'history.json'
with open(history, 'r') as infile:
    hist = json.load(infile)
    df = pd.DataFrame(hist).transpose()
    print(df)