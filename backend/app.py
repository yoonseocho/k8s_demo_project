from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler

import mysql.connector
from mysql.connector import errorcode

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

CORS(app)

def setup_logging():
    app.logger.setLevel(logging.INFO)
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    app.logger.addHandler(handler)
    app.logger.addHandler(logging.StreamHandler())

setup_logging()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='mysql-service', #10.0.20.62
            port='3306',
            user='root',
            password='1234',
            database='myappdb'
        )
        app.logger.info("데이터베이스 연결 성공")
        return connection
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            app.logger.error("데이터베이스 연결 실패: 잘못된 자격 증명")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            app.logger.error("데이터베이스 연결 실패: 데이터베이스가 존재하지 않습니다")
        else:
            app.logger.error(f"데이터베이스 연결 실패: {err}")
        return None

def create_tables():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) NOT NULL UNIQUE,
            password VARCHAR(120) NOT NULL,
            score INT DEFAULT 0
        )
        """)
        connection.commit()
        cursor.close()
        connection.close()
        app.logger.info("DB 테이블이 성공적으로 생성되었습니다.")
    else:
        app.logger.error("DB 테이블 생성 실패: 데이터베이스 연결 불가")

def test_db_connection():
    connection = get_db_connection()
    if connection:
        connection.close()
        app.logger.info("초기 데이터베이스 연결 테스트 성공")
    else:
        app.logger.error("초기 데이터베이스 연결 테스트 실패")

def initialize_app():
    app.logger.info("애플리케이션을 초기화합니다...")
    create_tables()
    test_db_connection()

# 애플리케이션 초기화 즉시 실행
initialize_app()

@app.route('/test-db')
def test_db():
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # 데이터베이스 연결 테스트
            cursor.execute("SELECT 1")
            connection_test = cursor.fetchone()
            
            # 모든 사용자 데이터 가져오기
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            app.logger.info("데이터베이스 연결 테스트 성공 및 사용자 데이터 조회 완료")
            return jsonify({
                "status": "success", 
                "message": "Database connection successful!",
                "connection_test": connection_test,
                "users": users
            }), 200
        else:
            app.logger.error("데이터베이스 연결 테스트 실패")
            return jsonify({"status": "error", "message": "Database connection failed"}), 500
    except Exception as e:
        app.logger.error(f"데이터베이스 연결 테스트 중 오류 발생: {str(e)}")
        return jsonify({"status": "error", "message": f"Error during database connection test: {str(e)}"}), 500

@app.route('/')
def hello_world():
    return jsonify({"message": "Hello, World!"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "아이디와 비밀번호를 모두 입력해주세요."}), 400

    app.logger.info(f"로그인 시도: 사용자 {username}")
    
    connection = get_db_connection()
    if connection:
        try:
            app.logger.info("로그인 함수에서 데이터베이스 연결 성공")
            cursor = connection.cursor(dictionary=True)
            app.logger.info("커서 생성 성공")
            
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            app.logger.info("SQL 쿼리 실행 성공")
            
            user = cursor.fetchone()
            app.logger.info(f"사용자 조회 결과: {user}")
            
            cursor.close()
            connection.close()
            app.logger.info("데이터베이스 연결 및 커서 정상 종료")

            if user is None:
                return jsonify({"success": False, "message": "존재하지 않는 사용자입니다."}), 401

            if user['password'] == password:
                app.logger.info(f"사용자 {username} 로그인 성공. 점수: {user['score']}")
                return jsonify({"success": True, "message": "로그인 성공!", "score": user['score']}), 200
            else:
                return jsonify({"success": False, "message": "비밀번호가 일치하지 않습니다."}), 401
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL 오류 발생: {err}")
            return jsonify({"success": False, "message": f"데이터베이스 오류: {err}"}), 500
        except Exception as e:
            app.logger.error(f"예상치 못한 오류 발생: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"서버 오류가 발생했습니다: {str(e)}"}), 500
    else:
        app.logger.error("로그인 함수에서 데이터베이스 연결 실패")
        return jsonify({"success": False, "message": "데이터베이스 연결 실패"}), 500
        
@app.route('/get_score/<username>', methods=['GET'])
def get_score(username):
    app.logger.info(f"사용자 점수 조회 시도: {username}")
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT score FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        app.logger.info(f"사용자 조회 결과: {user}")

        if user:
            return jsonify({"success": True, "score": user['score']}), 200
        else:
            return jsonify({"success": False, "message": "사용자를 찾을 수 없습니다."}), 404
    else:
        return jsonify({"success": False, "message": "서버 오류가 발생했습니다."}), 500

@app.route('/update_score', methods=['POST'])
def update_score():
    try:
        data = request.json
        new_score = data.get('score')
        username = data.get('username')

        app.logger.info(f"점수 업데이트 시도 - 사용자: {username}, 새 점수: {new_score}")

        if new_score is None:
            return jsonify({"success": False, "message": "점수가 제공되지 않았습니다."}), 400
        if username is None:
            return jsonify({"success": False, "message": "사용자 이름이 제공되지 않았습니다."}), 400

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT score FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()

            if not user:
                cursor.close()
                connection.close()
                return jsonify({"success": False, "message": "사용자를 찾을 수 없습니다."}), 404

            old_score = user[0]
            cursor.execute("UPDATE users SET score=%s WHERE username=%s", (new_score, username))
            connection.commit()
            cursor.close()
            connection.close()
            app.logger.info(f"사용자 {username}의 점수가 업데이트되었습니다: {old_score} -> {new_score}")
            return jsonify({"success": True, "message": "점수가 업데이트되었습니다.", "new_score": new_score}), 200
        else:
            return jsonify({"success": False, "message": "서버 오류가 발생했습니다."}), 500
    except Exception as e:
        app.logger.error(f"update_score 오류: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"서버 오류가 발생했습니다: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_PORT', 5000)), debug=True)