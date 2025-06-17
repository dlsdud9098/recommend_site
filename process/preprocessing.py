import pandas as pd
import pickle
from glob import glob
import json
import os

def save_data(datas):
    if isinstance(datas, pd.DataFrame):
        datas.to_json('data/all_data.json', orient='records')

        with open('data/all_data.json', 'r') as f:
            data = json.load(f)
            
        with open('data/all_data.data', 'wb') as f:
            pickle.dump(data, f)

    elif isinstance(datas, list):
        with open('data/all_data.data', 'wb') as f:
            pickle.dump(datas, f)


def load_data():
    if os.path.exists('data/all_data.data'):
        with open('data/all_data.data', 'rb') as f:
            all_data = pickle.load(f)
    else:
        files = glob('data/*.data')

        all_data = []
        for file in files:
            with open(file, 'rb') as f:
                data = pickle.load(f)
                all_data.extend(data)

        save_data(all_data)
        os.remove('data/all_data.json')

    return all_data


def drop_dupl(df:pd.DataFrame):
    new_df = df.drop_duplicates(['url'])
    new_df = new_df.drop_duplicates(['title'])
    return new_df

def str_preprocessing(df:pd.DataFrame):
    
    df['title'] = df['title'].str.strip()
    df['summary'] = df['summary'].str.replace(r'[\r, \n, \t]',' ', regex = True).replace(r'\s{2,}', ' ', regex=True).str.strip()
    df['keywords'] = df['keywords'].str.replace(r'[\r, \n, \t]',' ', regex = True).replace(r'\s{2,}', ' ', regex=True).str.strip()


    save_data(df)
if __name__ == '__main__':
    datas = load_data()
    df = pd.DataFrame(datas)

    df = drop_dupl(df)

    str_preprocessing(df)