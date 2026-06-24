# Jena Timeseries Dataset And Keras Model Note

The old local folder `D:\DeepLearning_Class2` contained these files:

```text
jena.ipynb
jena_climate_2009_2016.csv
jena_dense.keras
jena_lstm.keras
```

Only `jena.ipynb` was kept in this repository under:

```text
D:\ML_DL_Class\deep-learning\class-code\time-series\jena.ipynb
```

The raw dataset and trained `.keras` model artifacts are intentionally not
committed. They can be downloaded or regenerated when needed.

## Jena Climate Dataset

The dataset used by the Keras weather forecasting example is the Jena Climate
dataset recorded by the Max Planck Institute for Biogeochemistry in Jena,
Germany. It contains weather observations from January 10, 2009 to December 31,
2016.

Keras example page:

```text
https://keras.io/examples/timeseries/timeseries_weather_forecasting/
```

Direct dataset URL used in the Keras example:

```text
https://storage.googleapis.com/tensorflow/tf-keras-datasets/jena_climate_2009_2016.csv.zip
```

## Download With Python

```python
from zipfile import ZipFile
import keras

uri = "https://storage.googleapis.com/tensorflow/tf-keras-datasets/jena_climate_2009_2016.csv.zip"
zip_path = keras.utils.get_file(
    origin=uri,
    fname="jena_climate_2009_2016.csv.zip",
)

with ZipFile(zip_path) as zip_file:
    zip_file.extractall("D:/ML_DL_Class/deep-learning/class-code/time-series")
```

Expected output file:

```text
D:\ML_DL_Class\deep-learning\class-code\time-series\jena_climate_2009_2016.csv
```

## Keras Model Files

The old local files below were trained artifacts:

```text
jena_dense.keras
jena_lstm.keras
```

These are not usually downloaded from a public source. Recreate them by running
the notebook/script after downloading the Jena CSV, then save the trained models
again.

Example save calls:

```python
dense_model.save("jena_dense.keras")
lstm_model.save("jena_lstm.keras")
```

Place regenerated models next to the notebook if needed:

```text
D:\ML_DL_Class\deep-learning\class-code\time-series\jena_dense.keras
D:\ML_DL_Class\deep-learning\class-code\time-series\jena_lstm.keras
```

## Git Policy

The repository `.gitignore` excludes large dataset/model artifacts:

```text
*.keras
*.h5
*.ckpt
*.safetensors
*.pt
*.pth
*.onnx
```

Keep generated models and large raw datasets local unless there is a specific
reason to publish them elsewhere.
