import pandas as pd
from datetime import datetime
from dateutil.parser import parse

path = 'C:/Users/ethan/OneDrive/Desktop/# Data Science/2022-06-30 Jedha_Final_Project/Jedha_Final_Project'

def fill_dates(df):
    full_dates = pd.date_range(start=df['date'].min(), end=datetime.now(), freq='1D')
    df.index = df['date']
    df = df.reindex(index=full_dates)
    df['date'] = df.index
    df = df.reset_index(drop=True)
    df = df.fillna(method='ffill')
    return df

# https://download.bls.gov/pub/time.series/cu/cu.txt
CPI_types = ['11.USFoodBeverage', '12.USHousing', '13.USApparel', '14.USTransportation', '15.USMedical', '16.USRecreation', '17.USEducationAndCommunication', '18.USOtherGoodsAndServices', '20.USCommoditiesServicesSpecial']
CPI_dict = {}

for name in CPI_types:
    df = pd.read_csv(f'https://download.bls.gov/pub/time.series/cu/cu.data.{name}', delimiter='\t')
    df = df.iloc[:,:4]
    df.columns = ['series_id','year','month','CPI']
    df['month'] = df['month'].apply(lambda x: int(x[1:]))
    df = df[df['month'] != 13]
    df = df.reset_index(drop=True)

    # Calculating the mean CPI for each of the categories in CPI_types,
    # and filling a dictionary with those series.
    new_CPI = []
    for y in df['year'].unique():
        for m in df['month'].unique():
            year = df[df['year']==y]
            month = year[year['month']==m]
            thingy = (y, m, month['CPI'].mean(skipna=True))
            new_CPI.append(thingy)
    new_name = name.split('.')[1]
    new_name = 'CPI-' + new_name.split('US')[1]
    CPI_dict[f'{new_name}'] = pd.DataFrame(new_CPI, columns=['year', 'month', new_name])

df = CPI_dict[list(CPI_dict.keys())[0]][['year', 'month']]
for key in list(CPI_dict.keys()):
    df[key] = CPI_dict[key].iloc[:,2]

df['day'] = 1
date_creation = df[['year', 'month', 'day']].astype(str).copy()
date_creation['date'] = date_creation['year']+'-'+date_creation['month']+'-'+date_creation['day']
df['date'] = date_creation['date'].apply(parse)
df = df.drop(['year','month','day'], axis=1)
df = df.sort_values(by='date')
df = fill_dates(df)
df = df.dropna().reset_index(drop='True')

for name in CPI_dict.keys():
    df[['date', name]].to_feather(f'{path}/Data/{name}.ftr')