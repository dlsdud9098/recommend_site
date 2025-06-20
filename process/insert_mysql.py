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

    # 테이블 초기화
    table_name = "novels"
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    # 테이블 재생성
    create_table_sql = f"""
    CREATE TABLE {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url VARCHAR(255),
        img VARCHAR(255),
        title VARCHAR(255),
        author VARCHAR(255),
        recommend INT,
        genre VARCHAR(255),
        serial VARCHAR(255),
        publisher VARCHAR(255),
        summary TEXT,
        page_count INT,
        page_unit VARCHAR(10),
        age VARCHAR(10),
        platform VARCHAR(255),
        keywords TEXT,
        viewers INT
    )
    """
    cursor.execute(create_table_sql)

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
            recommend = int(data['recommend'].replace(',', ''))
            genre = data['genre']
            serial = data['serial']
            publisher = data['publisher']
            summary = data['summary']
            page_unit = data['page_unit']
            page_count = data['page_count']
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
                viewers
            ))
        except Exception as e:
            import traceback
            print(data)
            print(e)
            traceback.print_exc()
            break

    db.commit()

    db.close()
