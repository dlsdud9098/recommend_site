USE webtoon_novel_db;

-- 샘플 작품 데이터 삽입
INSERT INTO contents (title, author, type, cover_image, rating, episodes, description, views, genre, site_url) VALUES
('마법사의 탑', '김판타지', 'novel', '/placeholder.svg?height=400&width=300', 4.83, 120, '100층의 탑을 오르는 마법사의 모험을 그린 판타지 소설. 각 층마다 다른 시련이 기다리고 있다.', 125000, '판타지', 'https://example.com/novel/1'),
('용사의 귀환', '이웹툰', 'webtoon', '/placeholder.svg?height=400&width=300', 4.52, 85, '15년 만에 현실 세계로 돌아온 용사의 이야기. 평범한 일상과 과거의 기억 사이에서 갈등한다.', 98000, '판타지', 'https://example.com/webtoon/2'),
('그림자 암살자', '박스릴러', 'novel', '/placeholder.svg?height=400&width=300', 4.71, 95, '어둠 속에서 움직이는 암살자의 비밀 임무. 정체를 숨기며 살아가는 이중생활의 긴장감.', 87000, '스릴러', 'https://example.com/novel/3'),
('마법소녀 미라클', '최마법', 'webtoon', '/placeholder.svg?height=400&width=300', 4.64, 150, '평범한 고등학생이 마법소녀로 각성하며 벌어지는 일상과 모험의 이야기.', 156000, '판타지', 'https://example.com/webtoon/4'),
('로맨스 카페', '정로맨스', 'novel', '/placeholder.svg?height=400&width=300', 4.31, 78, '작은 카페에서 시작되는 달콤한 로맨스. 커피 향과 함께 피어나는 사랑 이야기.', 67000, '로맨스', 'https://example.com/novel/5'),
('좀비 아포칼립스', '한호러', 'webtoon', '/placeholder.svg?height=400&width=300', 4.42, 110, '좀비가 창궐한 세상에서 살아남기 위한 사람들의 처절한 생존기.', 134000, '호러', 'https://example.com/webtoon/6'),
('시간 여행자의 일기', '오SF', 'novel', '/placeholder.svg?height=400&width=300', 4.91, 200, '시간을 넘나드는 여행자가 남긴 일기를 통해 펼쳐지는 SF 미스터리.', 189000, 'SF', 'https://example.com/novel/7'),
('학원 액션 히어로', '강액션', 'webtoon', '/placeholder.svg?height=400&width=300', 4.23, 65, '평범한 학교에 숨겨진 비밀과 초능력을 가진 학생들의 액션 스토리.', 78000, '액션', 'https://example.com/webtoon/8'),
('미스터리 탐정', '윤미스터리', 'novel', '/placeholder.svg?height=400&width=300', 4.67, 88, '천재 탐정이 해결하는 기묘한 사건들. 매번 예상을 뒤엎는 반전이 기다린다.', 92000, '미스터리', 'https://example.com/novel/9'),
('요리왕의 모험', '서요리', 'webtoon', '/placeholder.svg?height=400&width=300', 4.15, 45, '최고의 요리사가 되기 위한 젊은 요리사의 모험과 성장 이야기.', 56000, '코미디', 'https://example.com/webtoon/10');

-- 태그 데이터 삽입
INSERT INTO tags (name) VALUES
('판타지'), ('모험'), ('마법'), ('액션'), ('용사'), ('암살자'), ('마법소녀'), ('학원'),
('로맨스'), ('일상'), ('카페'), ('호러'), ('좀비'), ('생존'), ('SF'), ('시간여행'),
('히어로'), ('미스터리'), ('추리'), ('탐정'), ('요리'), ('코미디'), ('치유'), ('성장'),
('복수'), ('전쟁'), ('우정'), ('가족');

-- 작품-태그 관계 데이터 삽입
INSERT INTO content_tags (content_id, tag_id) VALUES
-- 마법사의 탑
(1, 1), (1, 2), (1, 3),
-- 용사의 귀환
(2, 1), (2, 4), (2, 5),
-- 그림자 암살자
(3, 4), (3, 6),
-- 마법소녀 미라클
(4, 1), (4, 7), (4, 8),
-- 로맨스 카페
(5, 9), (5, 10), (5, 11),
-- 좀비 아포칼립스
(6, 12), (6, 13), (6, 14),
-- 시간 여행자의 일기
(7, 15), (7, 16), (7, 17),
-- 학원 액션 히어로
(8, 4), (8, 8), (8, 18),
-- 미스터리 탐정
(9, 17), (9, 19), (9, 20),
-- 요리왕의 모험
(10, 21), (10, 2), (10, 22);

-- 테스트 사용자 생성
INSERT INTO users (name, email, password_hash) VALUES
('테스트 사용자', 'test@example.com', '$2b$10$rQZ9QmSTnmc7Pj7FQmKOHOGJ8YrWpvllhp7IL.Vr8N8O8jVJmFQJG');
