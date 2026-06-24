# 3. 기본 라우팅 : 하나의 함수에 여러 URL 경로를 매핑하여 웹 페이지를 구성하는 방법

from flask import Flask 
app = Flask(__name__)

 # 라우팅 설정
@app.route('/') 
@app.route('/index') # 라우팅 설정 : URL 경로('/index')에 대한 라우팅 설정
@app.route('/home') # 라우팅 설정 : URL 경로('/home')에 대한 라우팅 설정

def main():
    return "Hello, this is the main page!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 