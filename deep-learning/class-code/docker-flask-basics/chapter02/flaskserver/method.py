# 4. 라우팅 : HTTP 메서드 지정

from flask import Flask 
app = Flask(__name__)

 # 라우팅 설정
@app.route('/') 
def main():
    return "This is for POST requests!"

# Flask는 기본적으로 GET 요청만 허용하나, methods 매개변수를 사용하여 POST, PUT, DELETE 등 다른 HTTP 메서드도 사용 가능
@app.route('/submit', methods=['POST']) # 라우팅 설정 : URL 경로('/submit')에 대한 POST 메서드 라우팅 설정
def submit():
    return "Form submitted successfully!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 