import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from os.path import exists

path = 'C:/Users/ethan/OneDrive/Desktop/# Data Science/2022-06-30 Jedha_Final_Project/Jedha_Final_Project'
now = datetime.now()

# https://www.marketwatch.com/investing/index/spx/download-data
if not exists(f'{path}/Data/SPX.ftr'):
    df = pd.read_excel(f'{path}/Data/SPX.xlsx')
    df['Date'] = df['Date'].apply(parse)
    df.columns = [col.lower().replace('*','') for col in df.columns]
    df['high-low'] = df['high']-df['low']
    df = df[['date', 'close', 'high-low']].copy()
    df = df.sort_values(by="date")
    df = df.reset_index(drop=True)
    df.to_feather(f'{path}/Data/SPX.ftr')

df_old = pd.read_feather(f'{path}/Data/SPX.ftr')
last_date = df_old['date'].max() + relativedelta(days=1)
df = pd.read_csv('https://www.marketwatch.com/investing/index/spx/downloaddatapartial?startdate={}%2000:00:00&enddate={}%2023:59:59&frequency=p1d&csvdownload=true'
                        .format(last_date.strftime('%m/%d/%Y'), 
                                now.strftime('%m/%d/%Y')))
df.columns = [col.lower() for col in df.columns]
for col in [i for i in df.columns if i != 'date']: #Price data is strings, converting to numbers.
        df[col] = pd.to_numeric(df[col].apply(lambda x: x.replace(',',''))).copy()

df['high-low'] = df['high'] - df['low'] #Creating column to show intra-day variation.
df['date'] = df['date'].apply(lambda x: datetime.strptime(x, '%m/%d/%Y'))
df = df.drop(['open','high','low'], axis=1)

df.columns = df_old.columns
df = df.sort_values(by='date')
df = df.reset_index(drop=True)

df = pd.concat((df_old, df), ignore_index=True)
df = df.drop_duplicates(subset='date', ignore_index=True)
df.to_feather(f'{path}/Data/SPX.ftr')