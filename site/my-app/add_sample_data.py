#!/usr/bin/env python3
"""
더 많은 샘플 데이터 추가 스크립트
"""

import mysql.connector
import json

def add_more_sample_data():
    """더 많은 샘플 데이터 추가"""
    
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234567890',
            database='webtoon_novel_db',
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # 더 많은 샘플 소설 데이터
        sample_novels = [
            {
                'url': 'https://novelpia.com/novel/100001',
                'img': '/placeholder.svg',  # 로컬 이미지 사용
                'title': '전지적 독자 시점',
                'author': '싱숑',
                'recommend': 2500,
                'genre': '판타지',
                'serial': '완결',
                'publisher': '문피아',
                'summary': '소설 속 세상이 현실이 되었을 때, 유일하게 결말을 아는 독자의 이야기',
                'page_count': 551,
                'page_unit': '화',
                'age': '전체이용가',
                'platform': 'munpia',
                'keywords': '["판타지", "게임", "회귀", "현대판타지"]',
                'viewers': 150000
            },
            {
                'url': 'https://novelpia.com/novel/100002',
                'img': '/placeholder.svg',
                'title': '나 혼자만 레벨업',
                'author': '추공',
                'recommend': 3000,
                'genre': '판타지',
                'serial': '완결',
                'publisher': '카카오페이지',
                'summary': '세계 최약체 헌터가 시스템을 얻고 최강이 되어가는 이야기',
                'page_count': 270,
                'page_unit': '화',
                'age': '전체이용가',
                'platform': 'kakao',
                'keywords': '["판타지", "액션", "레벨업", "헌터"]',
                'viewers': 200000
            },
            {
                'url': 'https://novelpia.com/novel/100003',
                'img': '/placeholder.svg',
                'title': '김독자의 재활용',
                'author': '김독자',
                'recommend': 1800,
                'genre': 'SF',
                'serial': '연재중',
                'publisher': '노벨피아',
                'summary': '버려진 것들을 재활용하여 새로운 가치를 창조하는 이야기',
                'page_count': 85,
                'page_unit': '화',
                'age': '전체이용가',
                'platform': 'novelpia',
                'keywords': '["SF", "환경", "재활용", "미래"]',
                'viewers': 45000
            },
            {
                'url': 'https://novelpia.com/novel/100004',
                'img': '/placeholder.svg',
                'title': '악역의 엔딩은 죽음뿐',
                'author': '권규리',
                'recommend': 2200,
                'genre': '로맨스',
                'serial': '완결',
                'publisher': '리디북스',
                'summary': '소설 속 악역으로 빙의한 여주인공의 생존기',
                'page_count': 180,
                'page_unit': '화',
                'age': '15세이용가',
                'platform': 'ridibooks',
                'keywords': '["로맨스", "빙의", "악역", "궁정"]',
                'viewers': 95000
            },
            {
                'url': 'https://novelpia.com/novel/100005',
                'img': '/placeholder.svg',
                'title': '데몬 슬레이어',
                'author': '고토게 코요하루',
                'recommend': 2800,
                'genre': '액션',
                'serial': '완결',
                'publisher': '대원씨아이',
                'summary': '귀멸의 칼날 - 가족을 잃은 소년이 귀살대가 되어 복수하는 이야기',
                'page_count': 205,
                'page_unit': '화',
                'age': '15세이용가',
                'platform': 'daewon',
                'keywords': '["액션", "판타지", "복수", "일본만화"]',
                'viewers': 180000
            }
        ]
        
        # 더 많은 샘플 웹툰 데이터
        sample_webtoons = [
            {
                'url': 'https://comic.naver.com/webtoon/detail/758037',
                'img': '/placeholder.svg',
                'title': '신의 탑',
                'author': 'SIU',
                'recommend': 3500,
                'genre': '판타지',
                'serial': '연재중',
                'publisher': '네이버웹툰',
                'summary': '탑을 오르는 소년 스물다섯번째 밤의 모험',
                'page_count': 590,
                'page_unit': '화',
                'age': '전체이용가',
                'platform': 'naver',
                'keywords': '["판타지", "액션", "모험", "탑"]',
                'viewers': 250000
            },
            {
                'url': 'https://comic.naver.com/webtoon/detail/183559',
                'img': '/placeholder.svg',
                'title': '마음의 소리',
                'author': '조석',
                'recommend': 4000,
                'genre': '일상',
                'serial': '완결',
                'publisher': '네이버웹툳',
                'summary': '조석과 친구들의 일상을 그린 개그 웹툰',
                'page_count': 1122,
                'page_unit': '화',
                'age': '전체이용가',
                'platform': 'naver',
                'keywords': '["개그", "일상", "조석", "유머"]',
                'viewers': 500000
            },
            {
                'url': 'https://webtoon.kakao.com/content/화산귀환',
                'img': '/placeholder.svg',
                'title': '화산귀환',
                'author': '비가',
                'recommend': 3200,
                'genre': '무협',
                'serial': '연재중',
                'publisher': '카카오웹툰',
                'summary': '화산파 최고의 검객이 과거로 돌아가 다시 시작하는 이야기',
                'page_count': 180,
                'page_unit': '화',
                'age': '15세이용가',
                'platform': 'kakao',
                'keywords': '["무협", "회귀", "검객", "화산파"]',
                'viewers': 180000
            },
            {
                'url': 'https://comic.naver.com/webtoon/detail/779707',
                'img': '/placeholder.svg',
                'title': '외모지상주의',
                'author': '박태준',
                'recommend': 2900,
                'genre': '드라마',
                'serial': '연재중',
                'publisher': '네이버웹툰',
                'summary': '외모 때문에 괴롭힘 받던 소년이 새로운 몸을 얻게 되는 이야기',
                'page_count': 480,
                'page_unit': '화',
                'age': '15세이용가',
                'platform': 'naver',
                'keywords': '["드라마", "학원", "외모", "성장"]',
                'viewers': 220000
            },
            {
                'url': 'https://page.kakao.com/home/여신강림',
                'img': '/placeholder.svg',
                'title': '여신강림',
                'author': '야옹이',
                'recommend': 2700,
                'genre': '로맨스',
                'serial': '완결',
                'publisher': '카카오페이지',
                'summary': '화장으로 완전히 달라진 소녀의 학교생활과 로맨스',
                'page_count': 150,
                'page_unit': '화',
                'age': '전체이용가',
                'platform': 'kakao',
                'keywords': '["로맨스", "학원", "화장", "첫사랑"]',
                'viewers': 190000
            },
            {
                'url': 'https://comic.naver.com/webtoon/detail/747269',
                'img': '/placeholder.svg',
                'title': '이태원 클라쓰',
                'author': '조광진',
                'recommend': 2600,
                'genre': '드라마',
                'serial': '완결',
                'publisher': '네이버웹툰',
                'summary': '아버지의 복수를 위해 이태원에서 술집을 운영하는 청년의 이야기',
                'page_count': 180,
                'page_unit': '화',
                'age': '15세이용가',
                'platform': 'naver',
                'keywords': '["드라마", "복수", "사업", "이태원"]',
                'viewers': 160000
            }
        ]
        
        # 기존 데이터 삭제 (중복 방지)
        cursor.execute("DELETE FROM novels WHERE id > 2")
        cursor.execute("DELETE FROM webtoons WHERE id > 1")
        
        # 소설 데이터 삽입
        novel_query = """
        INSERT INTO novels (url, img, title, author, recommend, genre, serial, publisher, 
                           summary, page_count, page_unit, age, platform, keywords, viewers)
        VALUES (%(url)s, %(img)s, %(title)s, %(author)s, %(recommend)s, %(genre)s, %(serial)s, 
                %(publisher)s, %(summary)s, %(page_count)s, %(page_unit)s, %(age)s, %(platform)s, 
                %(keywords)s, %(viewers)s)
        """
        
        cursor.executemany(novel_query, sample_novels)
        print(f"✓ {len(sample_novels)}개의 소설 데이터 추가 완료")
        
        # 웹툰 데이터 삽입
        webtoon_query = """
        INSERT INTO webtoons (url, img, title, author, recommend, genre, serial, publisher, 
                             summary, page_count, page_unit, age, platform, keywords, viewers)
        VALUES (%(url)s, %(img)s, %(title)s, %(author)s, %(recommend)s, %(genre)s, %(serial)s, 
                %(publisher)s, %(summary)s, %(page_count)s, %(page_unit)s, %(age)s, %(platform)s, 
                %(keywords)s, %(viewers)s)
        """
        
        cursor.executemany(webtoon_query, sample_webtoons)
        print(f"✓ {len(sample_webtoons)}개의 웹툰 데이터 추가 완료")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("=== 샘플 데이터 추가 완료 ===")
        print(f"총 소설: {len(sample_novels)}개")
        print(f"총 웹툰: {len(sample_webtoons)}개")
        
    except mysql.connector.Error as err:
        print(f"데이터베이스 오류: {err}")
    except Exception as e:
        print(f"일반 오류: {e}")

if __name__ == "__main__":
    add_more_sample_data()
