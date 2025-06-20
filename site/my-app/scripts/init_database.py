#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
"""

import mysql.connector
import json
import os
from typing import Optional

def create_database_connection(
    host: str = "localhost",
    user: str = "root", 
    password: str = "",
    database: Optional[str] = None
) -> mysql.connector.MySQLConnection:
    """MySQL 데이터베이스 연결 생성"""
    config = {
        'host': host,
        'user': user,
        'password': password,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    if database:
        config['database'] = database
    
    return mysql.connector.connect(**config)

def execute_sql_file(cursor, sql_content: str):
    """SQL 파일 내용 실행"""
    # SQL 문을 세미콜론으로 분리
    statements = sql_content.split(';')
    
    for statement in statements:
        statement = statement.strip()
        if statement:
            try:
                cursor.execute(statement)
                print(f"✓ 실행 완료: {statement[:50]}...")
            except mysql.connector.Error as err:
                print(f"✗ 오류: {err}")
                print(f"문제가 된 SQL: {statement}")

def initialize_database():
    """데이터베이스 초기화"""
    
    # 환경 변수에서 데이터베이스 설정 읽기
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', '1234567890'),
        'database_name': os.getenv('DB_NAME', 'webtoon_novel_db')
    }
    
    print("=== 데이터베이스 초기화 시작 ===")
    
    try:
        # 데이터베이스 없이 연결
        conn = create_database_connection(
            db_config['host'], 
            db_config['user'], 
            db_config['password']
        )
        cursor = conn.cursor()
        
        # SQL 스키마 내용
        schema_sql = """
-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS webtoon_novel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE webtoon_novel_db;

-- 1. 유저 테이블
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    blocked_tags JSON DEFAULT NULL COMMENT '차단된 태그 목록 저장',
    preferences JSON DEFAULT NULL COMMENT '사용자 선호 설정'
);

-- 2. 소설 테이블
CREATE TABLE IF NOT EXISTS novels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(500) NOT NULL,
    img VARCHAR(500) DEFAULT NULL,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    recommend INT DEFAULT 0,
    genre VARCHAR(100) DEFAULT NULL,
    serial ENUM('연재중', '완결', '휴재', '단편') DEFAULT NULL,
    publisher VARCHAR(100) DEFAULT NULL,
    summary TEXT DEFAULT NULL,
    page_count INT DEFAULT 0,
    page_unit VARCHAR(20) DEFAULT '화',
    age VARCHAR(20) DEFAULT NULL,
    platform VARCHAR(50) DEFAULT 'novelpia',
    keywords JSON DEFAULT NULL COMMENT '키워드 배열 저장',
    viewers INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_title (title),
    INDEX idx_author (author),
    INDEX idx_genre (genre),
    INDEX idx_platform (platform),
    INDEX idx_serial (serial),
    FULLTEXT INDEX ft_title_summary (title, summary)
);

-- 3. 웹툰 테이블
CREATE TABLE IF NOT EXISTS webtoons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(500) NOT NULL,
    img VARCHAR(500) DEFAULT NULL,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    recommend INT DEFAULT 0,
    genre VARCHAR(100) DEFAULT NULL,
    serial ENUM('연재중', '완결', '휴재', '단편') DEFAULT NULL,
    publisher VARCHAR(100) DEFAULT NULL,
    summary TEXT DEFAULT NULL,
    page_count INT DEFAULT 0,
    page_unit VARCHAR(20) DEFAULT '화',
    age VARCHAR(20) DEFAULT NULL,
    platform VARCHAR(50) NOT NULL,
    keywords JSON DEFAULT NULL COMMENT '키워드 배열 저장',
    viewers INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_title (title),
    INDEX idx_author (author),
    INDEX idx_genre (genre),
    INDEX idx_platform (platform),
    INDEX idx_serial (serial),
    FULLTEXT INDEX ft_title_summary (title, summary)
);

-- 4. 사용자 즐겨찾기 테이블 (소설)
CREATE TABLE IF NOT EXISTS user_novel_favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    novel_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_novel (user_id, novel_id)
);

-- 5. 사용자 즐겨찾기 테이블 (웹툰)
CREATE TABLE IF NOT EXISTS user_webtoon_favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    webtoon_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (webtoon_id) REFERENCES webtoons(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_webtoon (user_id, webtoon_id)
);

-- 6. 사용자 읽기 기록 테이블 (소설)
CREATE TABLE IF NOT EXISTS user_novel_reading_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    novel_id INT NOT NULL,
    last_read_page INT DEFAULT 1,
    reading_progress DECIMAL(5,2) DEFAULT 0.00 COMMENT '읽기 진행률 (0.00-100.00)',
    last_read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_novel_history (user_id, novel_id)
);

-- 7. 사용자 읽기 기록 테이블 (웹툰)
CREATE TABLE IF NOT EXISTS user_webtoon_reading_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    webtoon_id INT NOT NULL,
    last_read_page INT DEFAULT 1,
    reading_progress DECIMAL(5,2) DEFAULT 0.00 COMMENT '읽기 진행률 (0.00-100.00)',
    last_read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (webtoon_id) REFERENCES webtoons(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_webtoon_history (user_id, webtoon_id)
);

-- 8. 평점 테이블 (소설)
CREATE TABLE IF NOT EXISTS novel_ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    novel_id INT NOT NULL,
    rating DECIMAL(2,1) NOT NULL CHECK (rating >= 0.0 AND rating <= 5.0),
    review TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_novel_rating (user_id, novel_id)
);

-- 9. 평점 테이블 (웹툰)
CREATE TABLE IF NOT EXISTS webtoon_ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    webtoon_id INT NOT NULL,
    rating DECIMAL(2,1) NOT NULL CHECK (rating >= 0.0 AND rating <= 5.0),
    review TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (webtoon_id) REFERENCES webtoons(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_webtoon_rating (user_id, webtoon_id)
);
"""
        
        print("SQL 스키마 실행 중...")
        execute_sql_file(cursor, schema_sql)
        
        # 커밋
        conn.commit()
        print("✓ 데이터베이스 스키마 생성 완료")
        
        # 연결 닫기
        cursor.close()
        conn.close()
        
        print("=== 데이터베이스 초기화 완료 ===")
        
    except mysql.connector.Error as err:
        print(f"데이터베이스 오류: {err}")
    except Exception as e:
        print(f"일반 오류: {e}")

def insert_sample_data():
    """샘플 데이터 삽입"""
    
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', '1234567890'),
        'database': os.getenv('DB_NAME', 'webtoon_novel_db')
    }
    
    try:
        conn = create_database_connection(**db_config)
        cursor = conn.cursor()
        
        # 샘플 소설 데이터
        sample_novels = [
            {
                'url': 'https://novelpia.com/novel/123456',
                'img': 'https://img.novelpia.com/covers/123456.jpg',
                'title': '마법사의 탑',
                'author': '김판타지',
                'recommend': 1250,
                'genre': '판타지',
                'serial': '연재중',
                'publisher': '노벨피아',
                'summary': '100층의 탑을 오르는 마법사의 모험을 그린 판타지 소설',
                'page_count': 150,
                'page_unit': '화',
                'age': '전체이용가',
                'platform': 'novelpia',
                'keywords': '["판타지", "모험", "마법"]',
                'viewers': 50000
            },
            {
                'url': 'https://novelpia.com/novel/789012',
                'img': 'https://img.novelpia.com/covers/789012.jpg',
                'title': '시간 여행자의 일기',
                'author': '이SF',
                'recommend': 980,
                'genre': 'SF',
                'serial': '완결',
                'publisher': '노벨피아',
                'summary': '시간을 넘나드는 여행자가 남긴 일기를 통해 펼쳐지는 SF 미스터리',
                'page_count': 200,
                'page_unit': '화',
                'age': '전체이용가',
                'platform': 'novelpia',
                'keywords': '["SF", "시간여행", "미스터리"]',
                'viewers': 35000
            }
        ]
        
        # 샘플 웹툰 데이터
        sample_webtoons = [
            {
                'url': 'https://webtoon.com/123',
                'img': 'https://img.webtoon.com/covers/123.jpg',
                'title': '용사의 귀환',
                'author': '박웹툰',
                'recommend': 1100,
                'genre': '판타지',
                'serial': '연재중',
                'publisher': '네이버웹툰',
                'summary': '15년 만에 현실 세계로 돌아온 용사의 이야기',
                'page_count': 85,
                'page_unit': '화',
                'age': '전체이용가',
                'platform': 'naver',
                'keywords': '["판타지", "액션", "용사"]',
                'viewers': 75000
            }
        ]
        
        # 소설 데이터 삽입
        novel_query = """
        INSERT INTO novels (url, img, title, author, recommend, genre, serial, publisher, 
                           summary, page_count, page_unit, age, platform, keywords, viewers)
        VALUES (%(url)s, %(img)s, %(title)s, %(author)s, %(recommend)s, %(genre)s, %(serial)s, 
                %(publisher)s, %(summary)s, %(page_count)s, %(page_unit)s, %(age)s, %(platform)s, 
                %(keywords)s, %(viewers)s)
        """
        
        cursor.executemany(novel_query, sample_novels)
        print(f"✓ {len(sample_novels)}개의 샘플 소설 데이터 삽입 완료")
        
        # 웹툰 데이터 삽입
        webtoon_query = """
        INSERT INTO webtoons (url, img, title, author, recommend, genre, serial, publisher, 
                             summary, page_count, page_unit, age, platform, keywords, viewers)
        VALUES (%(url)s, %(img)s, %(title)s, %(author)s, %(recommend)s, %(genre)s, %(serial)s, 
                %(publisher)s, %(summary)s, %(page_count)s, %(page_unit)s, %(age)s, %(platform)s, 
                %(keywords)s, %(viewers)s)
        """
        
        cursor.executemany(webtoon_query, sample_webtoons)
        print(f"✓ {len(sample_webtoons)}개의 샘플 웹툰 데이터 삽입 완료")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("=== 샘플 데이터 삽입 완료 ===")
        
    except mysql.connector.Error as err:
        print(f"샘플 데이터 삽입 오류: {err}")

def main():
    """메인 함수"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--with-sample':
        print("스키마 생성 및 샘플 데이터 삽입을 진행합니다.")
        initialize_database()
        insert_sample_data()
    else:
        print("데이터베이스 스키마만 생성합니다.")
        print("샘플 데이터를 포함하려면 --with-sample 옵션을 사용하세요.")
        initialize_database()

if __name__ == "__main__":
    main()
