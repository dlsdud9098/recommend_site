-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS webtoon_novel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE webtoon_novel_db;

-- 작품 테이블
CREATE TABLE IF NOT EXISTS contents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    type ENUM('webtoon', 'novel') NOT NULL,
    cover_image VARCHAR(500),
    rating DECIMAL(3,2) DEFAULT 0.00,
    episodes INT DEFAULT 0,
    description TEXT,
    views INT DEFAULT 0,
    genre VARCHAR(100),
    site_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_type (type),
    INDEX idx_genre (genre),
    INDEX idx_rating (rating),
    INDEX idx_views (views)
);

-- 태그 테이블
CREATE TABLE IF NOT EXISTS tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 작품-태그 관계 테이블
CREATE TABLE IF NOT EXISTS content_tags (
    content_id INT,
    tag_id INT,
    PRIMARY KEY (content_id, tag_id),
    FOREIGN KEY (content_id) REFERENCES contents(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    avatar VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 사용자 선호작 테이블
CREATE TABLE IF NOT EXISTS user_favorites (
    user_id INT,
    content_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, content_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (content_id) REFERENCES contents(id) ON DELETE CASCADE
);

-- 사용자 차단 장르 테이블
CREATE TABLE IF NOT EXISTS user_blocked_genres (
    user_id INT,
    genre VARCHAR(100),
    PRIMARY KEY (user_id, genre),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 사용자 차단 태그 테이블
CREATE TABLE IF NOT EXISTS user_blocked_tags (
    user_id INT,
    tag_id INT,
    PRIMARY KEY (user_id, tag_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
