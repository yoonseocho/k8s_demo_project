-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS myappdb;

-- 사용할 데이터베이스 선택
USE myappdb;

-- 테이블 생성
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    score INT DEFAULT 0
);

-- 초기 데이터 삽입
INSERT INTO users (username, password, score) VALUES ('jessicadbstj', '12345', 100);
INSERT INTO users (username, password, score) VALUES ('yoonseok', '1113', 90);
