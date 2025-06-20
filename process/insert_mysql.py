import pymysql
import pickle
from glob import glob

if __name__ == '__main__':

    db = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='1234567890',
        db='webtoon_novel_db',
        charset='utf8'
    )

    cursor = db.cursor()

    insert_sql = """
    INSERT INTO novels (url, img, title, author, recommend, genre, serial, publisher, summary, page_count, page_unit, age, platform, keywords, viewers) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    with open('data/all_data.data', 'rb') as f:
        datas = pickle.load(f)

    for data in datas:
        try:
            url = data['url']
            img = data['img']
            title = data['title']
            author = data['author']
            recommend = int(data['recommend'].replace(',',''))
            genre = data['genre']
            serial = data['serial']
            publisher = data['publisher']
            summary = data['summary']
            page_unit = data['page_unit']

            
            if page_unit == '권':
                
                page_count = int(data['page_count'].replace('회차 ', '').replace(',', ''))*25, 
                page_unit = '화'
            else:
                page_count = int(data['page_count'].replace('회차', '').replace(',', '')), 
            
            age = data['age']
            platform = data['platform']
            keywords = data['keywords']
            viewers = int(data['viewers'].replace(',', ''))

            cursor.execute(insert_sql, (
                                    url,
                                    img,
                                    title,
                                    author,
                                    recommend,
                                    genre,
                                    serial,
                                    publisher,
                                    summary,
                                    page_count,
                                    page_unit,
                                    age,
                                    platform,
                                    keywords,
                                    viewers,)
            )
        except Exception as e:
            import traceback
            print(data)
            print(e)
            traceback.print_exc()
            break
        
    db.commit()

    db.close()