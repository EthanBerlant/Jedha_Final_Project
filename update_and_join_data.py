import pandas as pd
import os
from datetime import datetime
from functools import reduce

now = datetime.now()
path = 'C:/Users/ethan/OneDrive/Desktop/# Data Science/2022-06-30 Jedha_Final_Project/Jedha_Final_Project'

# Updating data from all sources
for script in os.listdir(f'{path}/Scripts'):
    exec(open(f'{path}/Scripts/{script}').read())

# Merging all datasets into 1 dataframe
file_list = [file.replace('.ftr','') for file in os.listdir(f'{path}/Data') if '.ftr' in file and file != 'cleaned_dataset.ftr'] #Reading filenames in Data folder.
joining_dict = {filename : pd.read_feather(f'{path}/Data/{filename}.ftr') for filename in file_list} #Creating a dictionary of dataframes read from each file.
start_date = max([df['date'].min() for df in joining_dict.values()]) #Calculating the first date from which data exists in all dataframes.
joining_dict = {key : df[df['date'] >= start_date] for key, df in zip(joining_dict.keys(), joining_dict.values())} #Only taking data after the date found above.
joined = reduce(lambda left,right: pd.merge(left, right, on='date'), joining_dict.values(), joining_dict.pop('SPX')) #Joining all dataframes into one.
joined = joined[joined['date'] <= now].reset_index(drop=True).rename(columns={'close':'SPX'}) #Removing any future data.
joined = joined.fillna(method='ffill') #Filling NaNs from missing data.

DFF_delta = []  #Creating a column to signal when (and how) the Fed changes rate.
for i in range(len(joined) - 1):
    DFF_delta.append(joined['DFF'][i+1] - joined['DFF'][i])   
DFF_delta.append(0)
joined['DFF_delta'] = DFF_delta

joined.to_feather(f'{path}/cleaned_dataset.ftr')