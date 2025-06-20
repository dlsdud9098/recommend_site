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

        os.remove('data/all_data.json')

    elif isinstance(datas, list):
        with open('data/all_data.data', 'wb') as f:
            pickle.dump(datas, f)


def load_data():
    files = glob('data/*.data')

    all_data = []
    for file in files:
        with open(file, 'rb') as f:
            data = pickle.load(f)
            all_data.extend(data)

    save_data(all_data)
    # os.remove('data/all_data.json')

    return all_data

def drop_dupl(df:pd.DataFrame):
    new_df = df.drop_duplicates(['url'])
    new_df = new_df.drop_duplicates(['title'])
    return new_df

# keywords 처리
def process_keywords(keywords):
    if isinstance(keywords, list):  # 리스트인 경우
        return "#" + " #".join(keywords)
    elif isinstance(keywords, str):  # 문자열인 경우
        return "#" + " #".join(keywords.split())
    return ""  # 다른 데이터 타입은 빈 문자열로 처리

def str_preprocessing(df:pd.DataFrame):
    df = df[df.notnull()]
    df['title'] = df['title'].str.strip()
    df['summary'] = df['summary'].str.replace(r'[\r, \n, \t]',' ', regex = True).replace(r'\s{2,}', ' ', regex=True).str.strip()
    # df['keywords'] = df['keywords'].str.replace(r'[\r, \n, \t]',' ', regex = True).replace(r'\s{2,}', ' ', regex=True).str.strip()
    # df['keywords'] = df['keywords'].apply(process_keywords)

    # df['keywords'] = df['keywords'].apply(lambda x: str(x) if isinstance(x, list) else x)

    df.loc[df['page_unit'] == '권', 'page_unit'] = '회차'
    df.loc[df['page_unit'] == '화', 'page_count'] *= 25



    save_data(df)
    return df
if __name__ == '__main__':
    datas = load_data()
    df = pd.DataFrame(datas)
    # print(df.head())

    df = drop_dupl(df)

    df = str_preprocessing(df)

    # print(str(row['keywords']) if isinstance(row['keywords'], list) else row['keywords'])

    for i, row in df.iterrows():
        pass

    print(row['keywords'])