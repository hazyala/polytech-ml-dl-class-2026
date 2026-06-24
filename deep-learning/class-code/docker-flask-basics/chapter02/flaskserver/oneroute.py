# 2. 기본 라우팅 : URL 경로와 함수를 1:1 매핑하여 웹 페이지를 구성하는 방법

from flask import Flask 
app = Flask(__name__)

 # 라우팅 설정
@app.route('/') 
def home():
    return "Welcome to the Home Page!"

@app.route('/about') # 라우팅 설정 : URL 경로('/about')에 대한 라우팅 설정
def about():
    return "This is the About Page."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 