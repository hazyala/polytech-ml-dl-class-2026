# Gas Leak Dataset Sample

`machine-learning/term-projects/gas-leak-prediction` 프로젝트가 기대하는 센서별 데이터셋 구조에 맞춘 샘플입니다.

원본 전체 데이터는 로컬 기준 `D:\ML_DL_Lab\dataset`에 있으며, 6개 센서 폴더와 약 12,000개 파일,
총 약 776MB 규모입니다. Git 저장소가 지나치게 커지는 것을 피하기 위해 여기에는 각 센서별 앞 10개
실험의 CSV/PNG 파일만 넣었습니다.

## Included Sensors

- `Accelerometer/`
- `Gas_Leak/`
- `Pressure_1/`
- `Pressure_2/`
- `Temperature_1/`
- `Temperature_2/`

전체 데이터로 학습하려면 `GAS_LEAK_DATASET_DIR` 환경 변수로 원본 데이터 위치를 지정할 수 있습니다.

```powershell
$env:GAS_LEAK_DATASET_DIR = "D:\ML_DL_Lab\dataset"
```

