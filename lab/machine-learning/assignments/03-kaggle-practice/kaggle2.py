from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import normalize
from sklearn.metrics import mean_squared_error
from matplotlib import pyplot as plt
import pandas as pd

idx_train, idx_test = train_test_split(range(len(X)), test_size=0.2, random_state=42)

x_train, x_test = X.iloc[idx_train], X.iloc[idx_test]
y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]

n_X = normalize(X, axis=0)
nX_train, nX_test = n_X[idx_train], n_X[idx_test]

lin_model1 = LinearRegression()
lin_model1.fit(x_train, y_train)

lin_model2 = LinearRegression()
lin_model2.fit(nX_train, y_train)

y1_hat_test = lin_model1.predict(x_test)
y2_hat_test = lin_model2.predict(nX_test)

print('lin_model1 (원본 X) MSE test:', mean_squared_error(y_test, y1_hat_test))
print('lin_model2 (정규화된 X) MSE test:', mean_squared_error(y_test, y2_hat_test))

compare_df = pd.DataFrame({
'actual': y_test,
'pred_orig': y1_hat_test,
'pred_norm': y2_hat_test,
})
print(compare_df.head())

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.scatter(y_test, y1_hat_test, alpha=0.6)
plt.plot([40, 100], [40, 100], color='k')
plt.title('lin_model1: 원본 X 예측')
plt.xlabel('Actual')
plt.ylabel('Predicted')

plt.subplot(1, 2, 2)
plt.scatter(y_test, y2_hat_test, alpha=0.6, color='orange')
plt.plot([40, 100], [40, 100], color='k')
plt.title('lin_model2: 정규화된 X 예측')
plt.xlabel('Actual')
plt.ylabel('Predicted')
plt.tight_layout()