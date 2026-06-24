# 1. flask app 개발 첫 예제

from flask import Flask #Flask 프레임워크 사용 import

# Flask 객체 생성
app = Flask(__name__)

# 라우팅 설정
@app.route('/') # 루트 URL('/')에 대한 라우팅 설정 : URL 경로와 해당 경로에 대한 처리 함수를 연결
def hello():
    return 'Hello, World!' # 사용자가 접속했을 떄 브라우저에 전달할 응답 값

# 스크립트가 직접 실행 될 때만 서버를 구동하도록 설정
if __name__ == '__main__':
    # host='0.0.0.0' : 모든 네트워크 인터페이스에서 접속 허용
    # port=5000 : 서버가 사용할 포트 번호
    app.run(host='0.0.0.0', port=5000)
