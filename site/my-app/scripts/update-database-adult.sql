USE webtoon_novel_db;

-- contents 테이블에 성인 작품 여부 컬럼 추가
ALTER TABLE contents ADD COLUMN is_adult BOOLEAN DEFAULT FALSE;

-- users 테이블에 성인 인증 관련 컬럼 추가
ALTER TABLE users ADD COLUMN is_adult_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN show_adult_content BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN adult_verification_date TIMESTAMP NULL;

-- 성인 작품 샘플 데이터 추가
INSERT INTO contents (title, author, type, cover_image, rating, episodes, description, views, genre, site_url, is_adult) VALUES
('성인 로맨스 소설', '성인작가1', 'novel', '/placeholder.svg?height=400&width=300', 4.25, 45, '성인을 위한 로맨스 소설입니다.', 89000, '로맨스', 'https://example.com/adult/novel/1', TRUE),
('성인 웹툰', '성인작가2', 'webtoon', '/placeholder.svg?height=400&width=300', 4.18, 32, '성인을 위한 웹툰입니다.', 76000, '로맨스', 'https://example.com/adult/webtoon/1', TRUE),
('성인 판타지', '성인작가3', 'novel', '/placeholder.svg?height=400&width=300', 4.33, 67, '성인을 위한 판타지 소설입니다.', 95000, '판타지', 'https://example.com/adult/novel/2', TRUE);

-- 성인 작품 태그 추가
INSERT INTO tags (name) VALUES ('성인'), ('19금'), ('성인로맨스');

-- 성인 작품에 태그 연결
INSERT INTO content_tags (content_id, tag_id) VALUES
((SELECT id FROM contents WHERE title = '성인 로맨스 소설'), (SELECT id FROM tags WHERE name = '성인')),
((SELECT id FROM contents WHERE title = '성인 로맨스 소설'), (SELECT id FROM tags WHERE name = '19금')),
((SELECT id FROM contents WHERE title = '성인 로맨스 소설'), (SELECT id FROM tags WHERE name = '성인로맨스')),
((SELECT id FROM contents WHERE title = '성인 웹툰'), (SELECT id FROM tags WHERE name = '성인')),
((SELECT id FROM contents WHERE title = '성인 웹툰'), (SELECT id FROM tags WHERE name = '19금')),
((SELECT id FROM contents WHERE title = '성인 판타지'), (SELECT id FROM tags WHERE name = '성인')),
((SELECT id FROM contents WHERE title = '성인 판타지'), (SELECT id FROM tags WHERE name = '19금'));
