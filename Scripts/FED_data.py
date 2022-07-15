import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from functools import reduce

path = 'C:/Users/ethan/OneDrive/Desktop/# Data Science/2022-06-30 Jedha_Final_Project/Jedha_Final_Project'

def americanize_time(date):
    return datetime.strftime(date, '%Y-%m-%d')

now = americanize_time(datetime.now())

def fill_dates(df):
    full_dates = pd.date_range(start=df['date'].min(), end=datetime.now(), freq='1D')
    df.index = df['date']
    df = df.reindex(index=full_dates)
    df['date'] = df.index
    df = df.reset_index(drop=True)
    df = df.fillna(method='ffill')
    return df

# Federal Reserve Data - https://fred.stlouisfed.org/
FED_series_list = ['DFF', 'MORTGAGE30US', 'DPRIME', 'DTB3', 'DTB1YR', 
                    'DTB6', 'DGS30', 'DGS20', 'DGS10', 'DGS7', 
                    'DGS5', 'DGS3', 'DGS2', 'DGS1', 'DGS3MO', 'DGS6MO', 
                    'CPIAUCSL', 'M2SL', 'A191RP1Q027SBEA', 'UNRATE', 
                    'A191RL1Q225SBEA', 'MSPUS', 'M1SL', 'PSAVERT', 
                    'CIVPART', 'WAAA', 'PCE', 'NFCI', 'MTSDS133FMS',
                    'GFDEGDQ188S', 'MEHOINUSA672N', 'ICSA', 'CURRCIR', 
                    'BOGMBASE', 'INDPRO', 'RECPROUSM156N']

for series in FED_series_list:
    old_df = pd.read_feather(f'{path}/Data/FED_data-{series}.ftr')
    start_date = americanize_time(old_df['date'].max() - timedelta(days=60))
    df = pd.read_excel(f'https://fred.stlouisfed.org/graph/fredgraph.xls?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id={series}&scale=left&cosd={start_date}&coed={now}&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Daily&fam=avg&fgst=lin&fgsnd={now}&line_index=1&transformation=lin&vintage_date={now}&revision_date={now}&nd={start_date}',
                        header=10, 
                        names=['date', f'FED_data-{series}'])

    new_df = pd.concat([old_df, df], ignore_index=True)
    new_df = new_df.drop_duplicates(subset='date', ignore_index=True)
    new_df = fill_dates(new_df)
    new_df.to_feather(f'{path}/Data/FED_data-{series}.ftr')