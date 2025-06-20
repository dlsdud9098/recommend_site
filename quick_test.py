#!/usr/bin/env python3
"""
MySQL 연결 빠른 테스트
"""

try:
    import mysql.connector
    
    print("🔍 MySQL 연결 테스트 중...")
    
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='1234567890',
        charset='utf8mb4'
    )
    
    print("✅ MySQL 연결 성공!")
    
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    databases = [db[0] for db in cursor.fetchall()]
    
    if 'webtoon_novel_db' in databases:
        print("✅ webtoon_novel_db 데이터베이스 존재")
        
        cursor.execute("USE webtoon_novel_db")
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        if 'novels' in tables and 'webtoons' in tables:
            print("✅ 필요한 테이블들 존재")
            
            cursor.execute("SELECT COUNT(*) FROM novels")
            novel_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM webtoons")
            webtoon_count = cursor.fetchone()[0]
            
            print(f"📊 현재 데이터: 소설 {novel_count}개, 웹툰 {webtoon_count}개")
            
            if novel_count > 0 or webtoon_count > 0:
                print("🎉 데이터베이스 연결 완료! 웹서버를 실행하세요:")
                print("   cd /home/apic/python/recommend_site/site/my-app")
                print("   npm run dev")
            else:
                print("⚠️ 데이터가 없습니다. 데이터 삽입을 실행하세요:")
                print("   python complete_db_setup.py")
        else:
            print("❌ 테이블이 없습니다. 데이터베이스 설정을 실행하세요:")
            print("   python complete_db_setup.py")
    else:
        print("❌ webtoon_novel_db 없습니다. 데이터베이스 설정을 실행하세요:")
        print("   python complete_db_setup.py")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"❌ MySQL 연결 실패: {err}")
    print("해결 방법:")
    print("1. MySQL 서비스 시작: sudo systemctl start mysql")
    print("2. 비밀번호 확인 (현재: 1234567890)")
    print("3. MySQL 사용자 권한 확인")
    
except ImportError:
    print("❌ mysql-connector-python 패키지가 설치되지 않았습니다.")
    print("설치 명령어: pip install mysql-connector-python")
