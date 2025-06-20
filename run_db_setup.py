#!/usr/bin/env python3
import subprocess
import os
import sys

def run_command(command, cwd=None):
    """명령어 실행 및 결과 출력"""
    print(f"\n>>> 실행: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True
        )
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        print(f"Return code: {result.returncode}")
        return result.returncode == 0
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

def main():
    print("=== 홈페이지-DB 연결 자동 설정 시작 ===")
    
    # 작업 디렉토리 설정
    work_dir = "/home/apic/python/recommend_site/site/my-app"
    
    # 1단계: DB 연결 테스트
    print("\n🔍 1단계: 데이터베이스 연결 테스트")
    success = run_command("python test_db.py", work_dir)
    
    if not success:
        print("❌ 데이터베이스 연결 실패. MySQL 서비스를 확인하세요.")
        return
    
    # 2단계: 데이터베이스 초기화
    print("\n🔧 2단계: 데이터베이스 스키마 생성")
    success = run_command("python scripts/init_database.py", work_dir)
    
    if not success:
        print("❌ 데이터베이스 초기화 실패")
        return
    
    # 3단계: Node.js 패키지 확인
    print("\n📦 3단계: Node.js 패키지 설치 확인")
    success = run_command("npm list --depth=0", work_dir)
    
    # 4단계: Next.js 개발 서버 실행 준비
    print("\n🚀 4단계: Next.js 빌드 확인")
    success = run_command("npm run build", work_dir)
    
    if success:
        print("\n✅ 모든 설정이 완료되었습니다!")
        print("\n다음 단계:")
        print("1. 터미널에서 다음 명령어 실행:")
        print(f"   cd {work_dir}")
        print("   npm run dev")
        print("\n2. 브라우저에서 http://localhost:3000 접속")
        print("\n3. 데이터 삽입 (새 터미널에서):")
        print(f"   cd {work_dir}")
        print("   python scripts/insert_data.py novel ../../../data/all_data.json")
    else:
        print("\n❌ 설정 중 문제가 발생했습니다.")

if __name__ == "__main__":
    main()
