#!/bin/bash

echo "🔧 홈페이지-DB 연결 환경 설정 시작"
echo "================================================"

# 현재 위치 확인
echo "📍 현재 디렉토리: $(pwd)"

# Python 가상환경 확인 및 생성
echo "🐍 Python 환경 설정 중..."

# 가상환경이 있는지 확인
if [ -d "/home/apic/python/recommend_site/.venv" ]; then
    echo "✅ 가상환경 발견됨"
    source /home/apic/python/recommend_site/.venv/bin/activate
else
    echo "🆕 가상환경 생성 중..."
    cd /home/apic/python/recommend_site
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Python 패키지 설치
echo "📦 Python 패키지 설치 중..."
cd /home/apic/python/recommend_site/site/my-app
pip install -r requirements.txt

# Node.js 패키지 확인
echo "🟨 Node.js 패키지 확인 중..."
if [ ! -d "node_modules" ]; then
    echo "📥 npm 패키지 설치 중..."
    npm install
else
    echo "✅ Node.js 패키지 이미 설치됨"
fi

# MySQL 서비스 상태 확인
echo "🗄️ MySQL 서비스 상태 확인..."
if systemctl is-active --quiet mysql; then
    echo "✅ MySQL 서비스 실행 중"
else
    echo "⚠️ MySQL 서비스 중지됨 - 시작 시도 중..."
    sudo systemctl start mysql
    if systemctl is-active --quiet mysql; then
        echo "✅ MySQL 서비스 시작 완료"
    else
        echo "❌ MySQL 서비스 시작 실패"
        exit 1
    fi
fi

# 데이터베이스 설정 실행
echo "🚀 데이터베이스 설정 실행..."
cd /home/apic/python/recommend_site
python complete_db_setup.py

echo ""
echo "================================================"
echo "🎉 환경 설정 완료!"
echo ""
echo "📋 다음 단계:"
echo "  1. 새 터미널에서 Next.js 서버 실행:"
echo "     cd /home/apic/python/recommend_site/site/my-app"
echo "     npm run dev"
echo ""
echo "  2. 브라우저에서 접속:"
echo "     http://localhost:3000"
echo ""
echo "✨ 홈페이지에서 크롤링 데이터를 확인할 수 있습니다!"
