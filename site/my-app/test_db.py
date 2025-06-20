#!/usr/bin/env python3
import mysql.connector

def test_connection():
    """MySQL 연결 테스트"""
    try:
        # 데이터베이스 연결
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234567890',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # 데이터베이스 목록 확인
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        
        print("✓ MySQL 연결 성공!")
        print("존재하는 데이터베이스:")
        for db in databases:
            print(f"  - {db[0]}")
        
        # webtoon_novel_db 데이터베이스 확인
        db_exists = any('webtoon_novel_db' in db for db in databases)
        
        if db_exists:
            print("\n✓ webtoon_novel_db 데이터베이스가 존재합니다.")
            
            # 데이터베이스 선택 후 테이블 확인
            cursor.execute("USE webtoon_novel_db")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print("존재하는 테이블:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("테이블이 없습니다.")
        else:
            print("\n✗ webtoon_novel_db 데이터베이스가 존재하지 않습니다.")
            print("데이터베이스를 생성해야 합니다.")
        
        cursor.close()
        conn.close()
        
        return True
        
    except mysql.connector.Error as err:
        print(f"✗ MySQL 연결 실패: {err}")
        return False
    except Exception as e:
        print(f"✗ 일반 오류: {e}")
        return False

if __name__ == "__main__":
    test_connection()
