#!/usr/bin/env python3
"""
성인 콘텐츠 데이터 확인 스크립트
"""

import mysql.connector

def check_adult_content():
    """데이터베이스에서 성인 콘텐츠 관련 데이터 확인"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234567890',
            database='webtoon_novel_db',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        print("=== 전체 연령 등급 분포 ===")
        cursor.execute("SELECT age, COUNT(*) FROM novels GROUP BY age ORDER BY COUNT(*) DESC")
        age_distribution = cursor.fetchall()
        
        for age, count in age_distribution:
            print(f"{age}: {count}개")
        
        print("\n=== 성인 콘텐츠 샘플 ===")
        cursor.execute("SELECT title, age FROM novels WHERE age LIKE '%19%' OR age = '성인' LIMIT 10")
        adult_samples = cursor.fetchall()
        
        for title, age in adult_samples:
            print(f"제목: {title} | 연령: {age}")
        
        print(f"\n성인 콘텐츠 총 개수: {len(adult_samples)}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    check_adult_content()
