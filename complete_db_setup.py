#!/usr/bin/env python3
"""
데이터베이스 연결 및 크롤링 데이터 삽입 통합 스크립트
"""

import mysql.connector
import json
import os
from typing import Dict, List, Any, Optional

def test_mysql_connection():
    """MySQL 연결 테스트"""
    print("=== MySQL 연결 테스트 ===")
    
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234567890',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        
        print("✅ MySQL 연결 성공!")
        print("데이터베이스 목록:")
        for db in databases:
            print(f"  - {db[0]}")
        
        # webtoon_novel_db 확인
        db_exists = any('webtoon_novel_db' in db for db in databases)
        if db_exists:
            print("✅ webtoon_novel_db 존재함")
            cursor.execute("USE webtoon_novel_db")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"테이블 개수: {len(tables)}")
        else:
            print("❌ webtoon_novel_db 없음 - 생성 필요")
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ MySQL 연결 실패: {err}")
        return False

def create_database_and_tables():
    """데이터베이스 및 테이블 생성"""
    print("\n=== 데이터베이스 생성 ===")
    
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234567890',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # 데이터베이스 생성
        cursor.execute("CREATE DATABASE IF NOT EXISTS webtoon_novel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE webtoon_novel_db")
        print("✅ 데이터베이스 생성/선택 완료")
        
        # 테이블 생성 SQL들
        table_sqls = [
            # 사용자 테이블
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP NULL,
                blocked_tags JSON DEFAULT NULL,
                preferences JSON DEFAULT NULL
            )
            """,
            
            # 소설 테이블
            """
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
                keywords JSON DEFAULT NULL,
                viewers INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_title (title),
                INDEX idx_author (author),
                INDEX idx_genre (genre),
                INDEX idx_platform (platform)
            )
            """,
            
            # 웹툰 테이블
            """
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
                keywords JSON DEFAULT NULL,
                viewers INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_title (title),
                INDEX idx_author (author),
                INDEX idx_genre (genre),
                INDEX idx_platform (platform)
            )
            """
        ]
        
        for sql in table_sqls:
            cursor.execute(sql)
            
        conn.commit()
        print("✅ 모든 테이블 생성 완료")
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ 테이블 생성 실패: {err}")
        return False

def load_and_insert_data():
    """크롤링 데이터 로드 및 삽입"""
    print("\n=== 크롤링 데이터 삽입 ===")
    
    # 데이터 파일 경로들
    data_files = [
        "/home/apic/python/recommend_site/data/all_data.json",
        "/home/apic/python/recommend_site/data/asd.json"
    ]
    
    # 사용할 데이터 파일 찾기
    data_file = None
    for file_path in data_files:
        if os.path.exists(file_path):
            data_file = file_path
            break
    
    if not data_file:
        print("❌ 데이터 파일을 찾을 수 없습니다")
        return False
    
    print(f"📁 데이터 파일: {data_file}")
    
    try:
        # 파일 크기 확인
        file_size = os.path.getsize(data_file)
        print(f"파일 크기: {file_size / (1024*1024):.1f} MB")
        
        # JSON 데이터 로드 (큰 파일이므로 스트리밍 방식 사용)
        print("📖 데이터 로딩 중...")
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("❌ 데이터가 리스트 형태가 아닙니다")
            return False
        
        print(f"✅ {len(data)}개의 데이터 로드 완료")
        
        # 데이터베이스 연결
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234567890',
            database='webtoon_novel_db',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # 데이터 삽입
        novel_count = 0
        webtoon_count = 0
        error_count = 0
        
        insert_novel_sql = """
        INSERT INTO novels (url, img, title, author, recommend, genre, serial, publisher, 
                           summary, page_count, page_unit, age, platform, keywords, viewers)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        insert_webtoon_sql = """
        INSERT INTO webtoons (url, img, title, author, recommend, genre, serial, publisher, 
                             summary, page_count, page_unit, age, platform, keywords, viewers)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for i, item in enumerate(data):
            try:
                # 필수 필드 검증
                if not item.get('title') or not item.get('author'):
                    continue
                
                # 데이터 준비
                values = (
                    item.get('url', ''),
                    item.get('img', ''),
                    item.get('title', ''),
                    item.get('author', ''),
                    int(item.get('recommend', 0)),
                    item.get('genre', ''),
                    item.get('serial', ''),
                    item.get('publisher', ''),
                    item.get('summary', ''),
                    int(item.get('page_count', 0)),
                    item.get('page_unit', '화'),
                    item.get('age', ''),
                    item.get('platform', 'unknown'),
                    json.dumps(item.get('keywords', []), ensure_ascii=False) if item.get('keywords') else None,
                    int(item.get('viewers', 0))
                )
                
                # 플랫폼 기반으로 소설/웹툰 구분
                platform = item.get('platform', '').lower()
                
                if 'novel' in platform or 'novelpia' in platform or platform == 'naver' and '소설' in item.get('genre', ''):
                    cursor.execute(insert_novel_sql, values)
                    novel_count += 1
                else:
                    cursor.execute(insert_webtoon_sql, values)
                    webtoon_count += 1
                
                # 진행상황 출력
                if (i + 1) % 100 == 0:
                    print(f"진행: {i+1}/{len(data)} (소설: {novel_count}, 웹툰: {webtoon_count})")
                
            except Exception as e:
                error_count += 1
                if error_count <= 5:  # 처음 5개 오류만 출력
                    print(f"데이터 삽입 오류: {e} - {item.get('title', 'Unknown')}")
        
        conn.commit()
        print(f"\n✅ 데이터 삽입 완료!")
        print(f"  - 소설: {novel_count}개")
        print(f"  - 웹툰: {webtoon_count}개")
        print(f"  - 오류: {error_count}개")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 데이터 삽입 실패: {e}")
        return False

def check_data_status():
    """삽입된 데이터 상태 확인"""
    print("\n=== 데이터 상태 확인 ===")
    
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234567890',
            database='webtoon_novel_db',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # 테이블별 데이터 개수 확인
        cursor.execute("SELECT COUNT(*) FROM novels")
        novel_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM webtoons")
        webtoon_count = cursor.fetchone()[0]
        
        print(f"📊 데이터 현황:")
        print(f"  - 소설: {novel_count:,}개")
        print(f"  - 웹툰: {webtoon_count:,}개")
        print(f"  - 총합: {novel_count + webtoon_count:,}개")
        
        # 샘플 데이터 확인
        if novel_count > 0:
            cursor.execute("SELECT title, author, genre FROM novels LIMIT 3")
            novels = cursor.fetchall()
            print("\n📚 소설 샘플:")
            for title, author, genre in novels:
                print(f"  - {title} ({author}) - {genre}")
        
        if webtoon_count > 0:
            cursor.execute("SELECT title, author, genre FROM webtoons LIMIT 3")
            webtoons = cursor.fetchall()
            print("\n🎨 웹툰 샘플:")
            for title, author, genre in webtoons:
                print(f"  - {title} ({author}) - {genre}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 데이터 확인 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 홈페이지-DB 연결 자동 설정 시작")
    print("=" * 50)
    
    # 1단계: MySQL 연결 테스트
    if not test_mysql_connection():
        print("\n❌ MySQL 연결에 실패했습니다. 다음을 확인하세요:")
        print("  1. MySQL 서비스 실행: sudo systemctl start mysql")
        print("  2. 비밀번호 확인: 현재 설정된 비밀번호는 '1234567890'")
        print("  3. MySQL 사용자 권한 확인")
        return
    
    # 2단계: 데이터베이스 및 테이블 생성
    if not create_database_and_tables():
        print("\n❌ 데이터베이스 생성에 실패했습니다.")
        return
    
    # 3단계: 크롤링 데이터 삽입
    if not load_and_insert_data():
        print("\n❌ 데이터 삽입에 실패했습니다.")
        return
    
    # 4단계: 데이터 상태 확인
    check_data_status()
    
    print("\n" + "=" * 50)
    print("🎉 모든 설정이 완료되었습니다!")
    print("\n📋 다음 단계:")
    print("  1. Next.js 서버 실행:")
    print("     cd /home/apic/python/recommend_site/site/my-app")
    print("     npm run dev")
    print("\n  2. 브라우저에서 접속:")
    print("     http://localhost:3000")
    print("\n  3. API 테스트:")
    print("     curl 'http://localhost:3000/api/contents?type=novel&limit=5'")
    print("\n✨ 웹사이트에서 크롤링한 데이터를 확인할 수 있습니다!")

if __name__ == "__main__":
    main()
