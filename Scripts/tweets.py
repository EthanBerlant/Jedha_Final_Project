import pandas as pd
import os
from datetime import datetime
import fnmatch
import tensorflow_hub as hub

path = 'C:/Users/ethan/OneDrive/Desktop/# Data Science/2022-06-30 Jedha_Final_Project/Jedha_Final_Project'

# Function removing '@' and '#' characters, and links, from tweets.
def cleaning(tweet):
  new_tweet = []
  for word in tweet.split():
    if word not in fnmatch.filter(tweet.split(), 'http*'):
      new_tweet.append(word.replace('@','').replace('#',''))
  return ' '.join(new_tweet)

# Function that creates an embedding for each tweet, then takes all the tweets from a given source
# in a given day and averages their embeddings, so that there is one embedding per day per source.
# Based on a "token based text 128-embedding trained on English Google News 200B corpus."
def embedding(df, tweet_source_name):
    embed = hub.load("https://tfhub.dev/google/tf2-preview/nnlm-en-dim128-with-normalization/1")
    tweet_embedding_df = pd.DataFrame(embed(df[tweet_source_name]).numpy())
    tweet_embedding_df['date'] = df['date']
    return tweet_embedding_df.groupby(by='date').mean().reset_index()

def fill_dates(df):
    full_dates = pd.date_range(start=df['date'].min(), end=datetime.now(), freq='1D')
    df.index = df['date']
    df = df.reindex(index=full_dates)
    df['date'] = df.index
    df = df.reset_index(drop=True)
    df = df.fillna(method='ffill')
    return df

tweet_sources = [file.replace('.json','') for file in os.listdir(f'{path}/Tweets') if '.json' in file]
for tweet_source in tweet_sources:
    df = pd.read_json(f'{path}/Tweets/{tweet_source}.json').drop(['Tweet Id', 'Username'], axis=1).rename(columns={'Datetime':'date','Text':tweet_source})
    df['date'] = df['date'].dt.date.astype('datetime64')
    df = df.sort_values(by='date')
    df[tweet_source] = df[tweet_source].apply(cleaning)
    df = embedding(df, tweet_source)
    df.columns = [str(x) for x in df.columns]
    df = fill_dates(df)
    df.to_feather(f'{path}/Tweets/{tweet_source}.ftr')