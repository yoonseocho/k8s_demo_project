FROM ubuntu

# 필수 패키지 업데이트 및 설치
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    libmysqlclient-dev \
    pkg-config \
    build-essential

# Python 라이브러리 설치
RUN pip3 install Flask flask-cors flask_mysqldb --break-system-packages
RUN pip install Flask Flask_SQLAlchemy --break-system-packages
RUN pip install mysql-connector-python --break-system-packages

# 작업 디렉터리 설정
WORKDIR /app

# 애플리케이션 파일 복사
COPY . /app

# 포트 5000 노출
EXPOSE 5000

# 애플리케이션 실행
CMD ["python3", "app.py"]

