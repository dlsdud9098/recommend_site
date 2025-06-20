# 웹툰/소설 추천 사이트 데이터베이스 연동

이 프로젝트는 웹툰과 소설 데이터를 관리하고 추천하는 웹 애플리케이션입니다.

## 🚀 설정 및 실행

### 1. 환경 변수 설정

`.env.local` 파일에서 데이터베이스 설정을 수정하세요:

```env
# MySQL Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_actual_password
DB_NAME=webtoon_novel_db

# 보안을 위한 JWT 시크릿
JWT_SECRET=your_jwt_secret_here

# 비밀번호 해싱용 솔트
PASSWORD_SALT=your_salt_here
```

### 2. 데이터베이스 초기화

```bash
# 기본 스키마만 생성
python scripts/init_database.py

# 스키마 + 샘플 데이터 생성
python scripts/init_database.py --with-sample
```

### 3. 웹 애플리케이션 실행

```bash
npm run dev
```

## 📊 데이터베이스 구조

### 핵심 테이블

1. **users** - 사용자 정보
   - 기본 인증 정보 (username, email, password_hash)
   - 차단 태그 목록 (JSON)
   - 사용자 선호 설정 (JSON)

2. **novels** - 소설 데이터
   - 크롤링된 소설 정보
   - JSON 키워드 저장
   - 전문 검색 인덱스

3. **webtoons** - 웹툰 데이터
   - 크롤링된 웹툰 정보
   - JSON 키워드 저장
   - 전문 검색 인덱스

### 기능 테이블

4. **user_novel_favorites** / **user_webtoon_favorites** - 즐겨찾기
5. **user_novel_reading_history** / **user_webtoon_reading_history** - 읽기 기록
6. **novel_ratings** / **webtoon_ratings** - 평점 및 리뷰

## 🔌 API 엔드포인트

### 컨텐츠 관련

- `GET /api/contents` - 컨텐츠 목록 조회 (필터링 지원)
- `POST /api/contents` - 새 컨텐츠 추가 (크롤링 데이터 삽입)
- `GET /api/contents/[id]?type=novel|webtoon` - 특정 컨텐츠 조회
- `PUT /api/contents/[id]` - 컨텐츠 업데이트
- `DELETE /api/contents/[id]?type=novel|webtoon` - 컨텐츠 삭제

### 사용자 인증

- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인

### 즐겨찾기

- `GET /api/favorites?userId=123&type=all|novel|webtoon` - 즐겨찾기 목록
- `POST /api/favorites` - 즐겨찾기 추가
- `DELETE /api/favorites?userId=123&contentId=456&type=novel|webtoon` - 즐겨찾기 제거

## 📥 크롤링 데이터 삽입

### 크롤링 데이터 형식

```python
# 크롤링 데이터 예시
novel_data = {
    'url': 'https://novelpia.com/novel/123456',
    'img': 'https://img.novelpia.com/covers/123456.jpg',
    'title': '소설 제목',
    'author': '작가명',
    'recommend': 1250,  # 추천수
    'genre': '판타지',
    'serial': '연재중',  # 연재중, 완결, 휴재, 단편
    'publisher': '출판사',
    'summary': '작품 줄거리',
    'page_count': 150,
    'page_unit': '화',
    'age': '전체이용가',
    'platform': 'novelpia',
    'keywords': ['판타지', '모험', '마법'],  # 키워드 배열
    'viewers': 50000
}
```

### Python 스크립트로 데이터 삽입

```bash
# 소설 데이터 삽입
python scripts/insert_data.py novel novels_data.json

# 웹툰 데이터 삽입
python scripts/insert_data.py webtoon webtoons_data.json
```

### API로 직접 삽입

```bash
curl -X POST http://localhost:3000/api/contents \
  -H "Content-Type: application/json" \
  -d '{
    "type": "novel",
    "data": {
      "url": "https://example.com/novel/123",
      "title": "테스트 소설",
      "author": "테스트 작가",
      "genre": "판타지",
      "summary": "테스트 줄거리",
      "platform": "test",
      "keywords": ["테스트", "판타지"]
    }
  }'
```

## 🔍 API 사용 예시

### 컨텐츠 검색

```bash
# 모든 컨텐츠 조회
curl "http://localhost:3000/api/contents"

# 소설만 조회
curl "http://localhost:3000/api/contents?type=novel"

# 제목으로 검색
curl "http://localhost:3000/api/contents?title=마법사"

# 장르 필터링
curl "http://localhost:3000/api/contents?genre=판타지"

# 키워드 검색
curl "http://localhost:3000/api/contents?keywords=모험,마법"

# 복합 필터링
curl "http://localhost:3000/api/contents?type=novel&genre=판타지&sortBy=viewers&limit=10"
```

### 사용자 기능

```bash
# 회원가입
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "blockedTags": ["성인", "폭력"]
  }'

# 로그인
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

## 🔧 필터링 옵션

API 요청 시 사용할 수 있는 필터링 옵션들:

- `type`: all, novel, webtoon
- `title`: 제목 검색 (LIKE 검색)
- `author`: 작가명 검색 (LIKE 검색)
- `genre`: 장르 필터
- `platform`: 플랫폼 필터
- `serial`: 연재 상태 (연재중, 완결, 휴재, 단편)
- `age`: 연령 등급
- `keywords`: 키워드 검색 (콤마로 구분)
- `minViewers`, `maxViewers`: 조회수 범위
- `minEpisodes`, `maxEpisodes`: 화수 범위
- `blockedGenres`: 차단할 장르들
- `blockedTags`: 차단할 태그들
- `sortBy`: 정렬 방식 (popularity, rating, views, recommend, newest, viewers)
- `limit`: 결과 개수 제한
- `offset`: 페이지네이션 오프셋

## 🛠 개발 정보

### 기술 스택

- **Frontend**: Next.js 15, React 19, TypeScript
- **Styling**: Tailwind CSS
- **Database**: MySQL 8.0+
- **ORM**: mysql2
- **UI Components**: Radix UI

### 프로젝트 구조

```
my-app/
├── app/
│   ├── api/
│   │   ├── contents/         # 컨텐츠 API
│   │   ├── auth/            # 인증 API
│   │   └── favorites/       # 즐겨찾기 API
│   ├── novels/              # 소설 페이지
│   ├── webtoons/            # 웹툰 페이지
│   └── ...
├── lib/
│   ├── database.ts          # 데이터베이스 연결 및 쿼리
│   └── ...
├── scripts/
│   ├── init_database.py     # DB 초기화
│   └── insert_data.py       # 데이터 삽입
└── ...
```

## 📝 TODO

- [ ] JWT 기반 인증 시스템 구현
- [ ] 사용자별 추천 알고리즘 개발
- [ ] 읽기 기록 추적 기능
- [ ] 평점 및 리뷰 시스템
- [ ] 실시간 검색 자동완성
- [ ] 이미지 최적화 및 CDN 연동
- [ ] 캐싱 시스템 구현
- [ ] API 레이트 리미팅
- [ ] 데이터 백업 및 복구 시스템
