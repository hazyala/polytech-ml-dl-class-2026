# 저장된 분류 모델을 Flask 폼에 연결

브라우저에서 두 숫자를 받아 scaler와 모델의 예측 결과를 HTML에 표시하는 분류 추론 실습.

`GET /`는 입력 폼, `POST /predict`는 `v1`·`v2`를 float로 읽는다. `app.py`는 30개 feature 배열을 만들고 첫 두 값에 mean radius·mean texture를 넣으며 나머지 28개는 0으로 채운다. `scaler.transform` → `model.predict`를 호출하고 0/1 결과를 악성/양성 문자열로 표시한다. 이 입력 구성은 분류 모델 호출을 배우는 예제이며 의료 판단용 모델 입력을 구성한 앱은 아니다.

## 파일과 실행

`breast_cancer_model.joblib`·`scaler.joblib`는 시작 시 현재 작업 폴더에서 읽는다. `templates/index.html`이 입력과 결과를 표시한다. 이 폴더에서 실행한다.

```bash
python -m pip install -r requirements.txt
python app.py
```

개별 Python 실행은 기본 Flask 주소 localhost:5000을 사용한다. Docker는 저장소 루트에서 `cd lab/docker` 후 `docker compose up --build ml-breast-cancer-flask`로 시작하며 host 포트는 5001이다.

이 폴더에는 학습 entry가 없고 저장된 모델을 읽는 추론 코드가 있다. [다른 ML 과제](../README.md)
