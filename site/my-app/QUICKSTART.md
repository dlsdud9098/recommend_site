# 🚀 빠른 시작 가이드

## 1. 환경 설정

### 데이터베이스 비밀번호 설정
`.env.local` 파일에서 실제 MySQL 비밀번호를 설정하세요:

```env
DB_PASSWORD=your_actual_mysql_password
```

### 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

## 2. 데이터베이스 초기화

```bash
# 스키마 생성 + 샘플 데이터
python scripts/init_database.py --with-sample
```

## 3. 웹 서버 실행

```bash
npm run dev
```

## 4. 크롤링 데이터 삽입

### 소설 데이터
```bash
python scripts/insert_data.py novel scripts/sample_novels.json
```

### 웹툰 데이터
```bash
python scripts/insert_data.py webtoon scripts/sample_webtoons.json
```

## 5. API 테스트

```bash
# 모든 컨텐츠 조회
curl http://localhost:3000/api/contents

# 소설만 조회
curl "http://localhost:3000/api/contents?type=novel"

# 웹툰만 조회
curl "http://localhost:3000/api/contents?type=webtoon"
```

## 📊 주요 API 엔드포인트

- `GET /api/contents` - 컨텐츠 목록 (필터링 지원)
- `POST /api/contents` - 새 컨텐츠 추가
- `GET /api/contents/[id]?type=novel|webtoon` - 특정 컨텐츠 조회
- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인
- `GET /api/favorites` - 즐겨찾기 목록

## 🛠 자동 설정 (Linux/Mac)

모든 설정을 자동으로 실행하려면:

```bash
chmod +x setup.sh
./setup.sh
```

이제 크롤링한 데이터를 웹페이지에서 확인할 수 있습니다! 🎉
