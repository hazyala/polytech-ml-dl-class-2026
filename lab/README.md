# Lab

과제와 텀프로젝트 산출물을 수업 구분과 제출물 성격에 맞춰 정리한 폴더입니다.

## Structure

```text
lab/
  deep-learning/
    assignments/
      01-missionaries-cannibals-gm/
      02-comfyui-translate-image/
      03-cookie-sse-chat/
    term-projects/
      chat-image-generator/
  machine-learning/
    assignments/
      01-iris-knn-kmeans-pca/
      02-cannibals-missionaries.py
      03-kaggle-practice/
      04-breast-cancer-flask/
    term-projects/
      gas-leak-prediction/
  datasets/
    gas-leak-sample/
  docs/
    PROJECT_DOCS.md
  shared/
    apps-common/
```

## Deep Learning

| Path | Description |
| --- | --- |
| `deep-learning/assignments/01-missionaries-cannibals-gm/` | DL 과제1 - 식인종/선교사 LLM GM 웹앱 |
| `deep-learning/assignments/02-comfyui-translate-image/` | DL 과제2 - 한글 프롬프트 번역 + ComfyUI 이미지 생성 |
| `deep-learning/assignments/03-cookie-sse-chat/` | DL 과제3 - 쿠키 세션 + SSE 스트리밍 챗봇 |
| `deep-learning/term-projects/chat-image-generator/` | DL 텀프로젝트 - 대화형 이미지 생성 앱 |

## Machine Learning

| Path | Description |
| --- | --- |
| `machine-learning/assignments/01-iris-knn-kmeans-pca/` | Iris KNN, KMeans, PCA 비교 과제 |
| `machine-learning/assignments/02-cannibals-missionaries.py` | 식인종-선교사 문제 풀이 과제 |
| `machine-learning/assignments/03-kaggle-practice/` | Kaggle 기반 실습/과제 후보 |
| `machine-learning/assignments/04-breast-cancer-flask/` | 유방암 진단 모델 Flask 응용 과제 |
| `machine-learning/term-projects/gas-leak-prediction/` | ML 기초 텀프로젝트 - 가스 누출 예측 |

## Dataset

`datasets/gas-leak-sample/`에는 가스 누출 프로젝트용 샘플 데이터만 들어 있습니다. 전체 원본 데이터는
로컬 `D:\ML_DL_Lab\dataset`에 있으며 약 776MB입니다. 전체 데이터로 학습하려면 `GAS_LEAK_DATASET_DIR`
환경 변수로 데이터 위치를 지정하거나 전체 센서 폴더를 `datasets/gas-leak-sample/` 위치에 맞춰 교체하면 됩니다.

