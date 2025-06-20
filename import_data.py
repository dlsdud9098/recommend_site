#!/usr/bin/env python3
"""
크롤링된 데이터를 MySQL 데이터베이스에 삽입하는 스크립트
"""

import json
import pickle
import mysql.connector
import os
from tqdm import tqdm
import re

def create_connection():
    """MySQL 연결 생성"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234567890',  # 실제 MySQL 비밀번호
            database='webtoon_novel_db',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        print("✓ MySQL 연결 성공!")
        return connection
    except mysql.connector.Error as err:
        print(f"✗ MySQL 연결 실패: {err}")
        return None

def load_data(file_path):
    """데이터 파일 로드 (pickle 또는 json)"""
    try:
        if file_path.endswith('.data'):
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                print(f"✓ Pickle 파일 로드 성공: {len(data)}개 항목")
                return data
        elif file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✓ JSON 파일 로드 성공: {len(data)}개 항목")
                return data
        else:
            print(f"✗ 지원하지 않는 파일 형식: {file_path}")
            return []
    except Exception as e:
        print(f"✗ 파일 로드 실패 {file_path}: {e}")
        return []

def clean_number(value, default=0):
    """숫자 데이터 정리"""
    if value is None:
        return default
    try:
        # 숫자가 아닌 문자 제거
        cleaned = re.sub(r'[^0-9]', '', str(value))
        return int(cleaned) if cleaned else default
    except:
        return default

def clean_data(data):
    """데이터 정리 및 검증"""
    cleaned_data = []
    
    print("데이터 정리 중...")
    for item in tqdm(data):
        if not item or not isinstance(item, dict):
            continue
            
        # 필수 필드 확인
        title = item.get('title', '').strip()
        author = item.get('author', '').strip()
        
        if not title or not author:
            continue
        
        # 숫자 필드 정리
        recommend = clean_number(item.get('recommend'), 0)
        page_count = clean_number(item.get('page_count'), 0)
        viewers = clean_number(item.get('viewers'), 0)
        
        # 키워드 정리
        keywords = item.get('keywords', '')
        if isinstance(keywords, str):
            # 키워드를 리스트로 변환
            keywords_list = [kw.strip() for kw in keywords.replace(',', ' ').split() if kw.strip()]
            keywords_json = json.dumps(keywords_list, ensure_ascii=False)
        elif isinstance(keywords, list):
            keywords_json = json.dumps(keywords, ensure_ascii=False)
        else:
            keywords_json = json.dumps([], ensure_ascii=False)
        
        # 이미지 URL 정리
        img = item.get('img', '')
        if img and not img.startswith('http'):
            if img.startswith('//'):
                img = 'https:' + img
            elif img.startswith('/'):
                img = 'https://novelpia.com' + img
        
        # 정리된 데이터
        cleaned_item = {
            'url': item.get('url', ''),
            'img': img,
            'title': title,
            'author': author,
            'recommend': recommend,
            'genre': item.get('genre', '기타'),
            'serial': item.get('serial', '연재중'),
            'publisher': item.get('publisher', ''),
            'summary': item.get('summary', ''),
            'page_count': page_count,
            'page_unit': item.get('page_unit', '화'),
            'age': item.get('age', '전체'),
            'platform': item.get('platform', 'novelpia'),
            'keywords': keywords_json,
            'viewers': viewers
        }
        
        cleaned_data.append(cleaned_item)
    
    print(f"✓ 데이터 정리 완료: {len(cleaned_data)}개 유효 항목")
    return cleaned_data

def insert_data_to_mysql(connection, data, table_name):
    """MySQL에 데이터 삽입"""
    cursor = connection.cursor()
    
    # 기존 데이터 삭제 (선택사항)
    print(f"기존 {table_name} 데이터 삭제...")
    cursor.execute(f"DELETE FROM {table_name}")
    
    # 삽입 쿼리
    if table_name == 'novels':
        query = """
        INSERT INTO novels (
            url, img, title, author, recommend, genre, serial, publisher,
            summary, page_count, page_unit, age, platform, keywords, viewers
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    elif table_name == 'webtoons':
        query = """
        INSERT INTO webtoons (
            url, img, title, author, recommend, genre, serial, publisher,
            summary, page_count, page_unit, age, platform, keywords, viewers
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    else:
        print(f"✗ 지원하지 않는 테이블: {table_name}")
        return
    
    # 배치 삽입
    print(f"{table_name}에 데이터 삽입 중...")
    batch_size = 100
    for i in tqdm(range(0, len(data), batch_size)):
        batch = data[i:i+batch_size]
        batch_values = []
        
        for item in batch:
            values = (
                item['url'], item['img'], item['title'], item['author'],
                item['recommend'], item['genre'], item['serial'], item['publisher'],
                item['summary'], item['page_count'], item['page_unit'],
                item['age'], item['platform'], item['keywords'], item['viewers']
            )
            batch_values.append(values)
        
        try:
            cursor.executemany(query, batch_values)
            connection.commit()
        except mysql.connector.Error as err:
            print(f"✗ 삽입 오류: {err}")
            connection.rollback()
    
    print(f"✓ {table_name}에 {len(data)}개 데이터 삽입 완료!")
    cursor.close()

def main():
    print("=== 크롤링 데이터를 MySQL에 삽입 ===")
    
    # 데이터 디렉토리 경로
    data_dir = "/home/apic/python/recommend_site/data"
    
    # MySQL 연결
    connection = create_connection()
    if not connection:
        return
    
    # 사용 가능한 데이터 파일들
    data_files = {
        'novelpia': 'novelpia_novel_data.data',
        'naver': 'naver_novel_data.data',
        'all_data': 'all_data.json'
    }
    
    print("\\n사용 가능한 데이터 파일:")
    for key, filename in data_files.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath) / (1024*1024)  # MB
            print(f"  {key}: {filename} ({size:.1f}MB)")
    
    # 사용자 선택
    print("\\n어떤 데이터를 사용하시겠습니까?")
    print("1. novelpia_novel_data.data (노벨피아 소설)")
    print("2. naver_novel_data.data (네이버 소설)")
    print("3. all_data.json (전체 데이터)")
    
    choice = input("선택하세요 (1-3): ").strip()
    
    if choice == '1':
        filename = 'novelpia_novel_data.data'
        table_name = 'novels'
    elif choice == '2':
        filename = 'naver_novel_data.data'
        table_name = 'novels'
    elif choice == '3':
        filename = 'all_data.json'
        table_name = 'novels'  # 기본적으로 소설 테이블에 삽입
    else:
        print("✗ 잘못된 선택입니다.")
        return
    
    filepath = os.path.join(data_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"✗ 파일이 존재하지 않습니다: {filepath}")
        return
    
    # 데이터 로드 및 정리
    raw_data = load_data(filepath)
    if not raw_data:
        return
    
    cleaned_data = clean_data(raw_data)
    if not cleaned_data:
        print("✗ 유효한 데이터가 없습니다.")
        return
    
    # MySQL에 삽입
    insert_data_to_mysql(connection, cleaned_data, table_name)
    
    # 연결 종료
    connection.close()
    print("\\n=== 완료 ===")

if __name__ == "__main__":
    main()
