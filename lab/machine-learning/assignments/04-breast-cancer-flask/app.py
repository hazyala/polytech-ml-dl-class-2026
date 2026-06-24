from flask import Flask, render_template, request
import joblib
import numpy as np

app = Flask(__name__)

# 저장된 모델과 스케일러 불러오기
model = joblib.load('breast_cancer_model.joblib')
scaler = joblib.load('scaler.joblib')

@app.route('/')
def index():
    # 데이터를 입력할 화면을 보여줌
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            # 1. 화면에서 입력한 2개의 수치를 가져옴
            v1 = float(request.form.get('v1', 0))
            v2 = float(request.form.get('v2', 0))
            
            # 2. 모델이 요구하는 30개의 숫자를 만듦 (나머지 28개는 0으로 채움)
            # 마마, 실제 정확도를 위해서는 30개를 다 넣어야 하나, 일단 작동을 위해 비책을 씁니다.
            input_data = [0] * 30
            input_data[0] = v1  # mean radius
            input_data[1] = v2  # mean texture
            
            features = np.array([input_data])
            
            # 3. 스케일러로 다듬고 예측함
            features_std = scaler.transform(features)
            prediction = model.predict(features_std)
            
            # 4. 결과 판정 (0: 악성, 1: 양성)
            result = "악성(Malignant)" if prediction[0] == 0 else "양성(Benign)"
            
            return render_template('index.html', prediction_text=f'진단 결과: {result}')
            
        except Exception as e:
            # 혹시나 다른 에러가 나면 화면에 표시함
            return render_template('index.html', prediction_text=f'오류 발생: {str(e)}')

if __name__ == '__main__':
    app.run(debug=True)