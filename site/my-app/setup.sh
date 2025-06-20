#!/bin/bash

echo "=== 웹툰/소설 추천 사이트 빠른 설정 ==="

# 환경 변수 확인
if [ ! -f .env.local ]; then
    echo "❌ .env.local 파일이 없습니다. 먼저 데이터베이스 설정을 완료해주세요."
    exit 1
fi

# Python 패키지 설치
echo "📦 Python 패키지 설치 중..."
pip install -r requirements.txt

# 데이터베이스 초기화
echo "🗄️  데이터베이스 초기화 중..."
python scripts/init_database.py --with-sample

# 샘플 데이터 추가 삽입
echo "📚 추가 샘플 데이터 삽입 중..."

# Next.js 서버 시작 (백그라운드)
echo "🚀 Next.js 서버 시작 중..."
npm run dev &
SERVER_PID=$!

# 서버 시작 대기
echo "⏳ 서버 시작 대기 중... (10초)"
sleep 10

# 샘플 소설 데이터 삽입
echo "📖 샘플 소설 데이터 삽입 중..."
python scripts/insert_data.py novel scripts/sample_novels.json

# 샘플 웹툰 데이터 삽입
echo "🎨 샘플 웹툰 데이터 삽입 중..."
python scripts/insert_data.py webtoon scripts/sample_webtoons.json

echo ""
echo "✅ 설정 완료!"
echo "🌐 웹사이트: http://localhost:3000"
echo "📊 API 테스트: http://localhost:3000/api/contents"
echo ""
echo "💡 서버를 중지하려면 Ctrl+C를 누르세요."
echo ""

# 서버가 계속 실행되도록 대기
wait $SERVER_PID
