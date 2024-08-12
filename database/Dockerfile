# 사용할 기본 이미지 설정
FROM mysql:latest

# 환경 변수 설정(루트 비밀번호 및 초기 데이터베이스 이름)
ENV MYSQL_ROOT_PASSWORD=1234
ENV MYSQL_DATABASE=myappdb

# SQL 초기화 스크립트 복사
COPY init.sql /docker-entrypoint-initdb.d/

# 포트 노출(기본 MySQL 포트)
EXPOSE 3306
