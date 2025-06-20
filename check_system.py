#!/usr/bin/env python3
"""
시스템 상태 및 MySQL 연결 간단 체크 스크립트
"""

import os
import subprocess
import sys

def check_mysql_service():
    """MySQL 서비스 상태 확인"""
    print("🔍 MySQL 서비스 상태 확인...")
    
    try:
        # systemctl 명령어로 MySQL 상태 확인
        result = subprocess.run(['systemctl', 'is-active', 'mysql'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip() == 'active':
            print("✅ MySQL 서비스 실행 중")
            return True
        else:
            print("❌ MySQL 서비스 중지됨")
            print("다음 명령어로 시작하세요: sudo systemctl start mysql")
            return False
            
    except Exception as e:
        print(f"⚠️ 서비스 상태 확인 중 오류: {e}")
        return False

def check_python_packages():
    """필요한 Python 패키지 확인"""
    print("\n🐍 Python 패키지 확인...")
    
    required_packages = ['mysql.connector', 'json', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'mysql.connector':
                import mysql.connector
            elif package == 'json':
                import json
            elif package == 'requests':
                import requests
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 설치 필요")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n설치 명령어:")
        if 'mysql.connector' in missing_packages:
            print("pip install mysql-connector-python")
        if 'requests' in missing_packages:
            print("pip install requests")
        return False
    
    return True

def check_node_setup():
    """Node.js 설정 확인"""
    print("\n🟨 Node.js 환경 확인...")
    
    app_path = "/home/apic/python/recommend_site/site/my-app"
    
    # package.json 확인
    if os.path.exists(f"{app_path}/package.json"):
        print("✅ package.json 존재")
    else:
        print("❌ package.json 없음")
        return False
    
    # node_modules 확인
    if os.path.exists(f"{app_path}/node_modules"):
        print("✅ node_modules 존재")
    else:
        print("❌ node_modules 없음 - npm install 필요")
        return False
    
    # .env.local 확인
    if os.path.exists(f"{app_path}/.env.local"):
        print("✅ .env.local 존재")
    else:
        print("❌ .env.local 없음")
        return False
    
    return True

def check_data_files():
    """크롤링 데이터 파일 확인"""
    print("\n📁 데이터 파일 확인...")
    
    data_files = [
        "/home/apic/python/recommend_site/data/all_data.json",
        "/home/apic/python/recommend_site/data/asd.json"
    ]
    
    found_files = []
    for file_path in data_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            print(f"✅ {os.path.basename(file_path)} ({file_size:.1f} MB)")
            found_files.append(file_path)
        else:
            print(f"❌ {os.path.basename(file_path)} 없음")
    
    return len(found_files) > 0

def main():
    """메인 함수"""
    print("🔧 홈페이지-DB 연결 사전 점검")
    print("=" * 40)
    
    all_checks_passed = True
    
    # 각 항목 체크
    checks = [
        ("MySQL 서비스", check_mysql_service),
        ("Python 패키지", check_python_packages),
        ("Node.js 환경", check_node_setup),
        ("데이터 파일", check_data_files)
    ]
    
    for check_name, check_func in checks:
        if not check_func():
            all_checks_passed = False
    
    print("\n" + "=" * 40)
    
    if all_checks_passed:
        print("🎉 모든 사전 점검 통과!")
        print("\n다음 단계:")
        print("1. python complete_db_setup.py (데이터베이스 설정)")
        print("2. cd site/my-app && npm run dev (웹서버 실행)")
    else:
        print("⚠️ 일부 항목에 문제가 있습니다.")
        print("위의 오류들을 해결한 후 다시 시도하세요.")
    
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
