# Consumption-Analysis
[所得房價消費分析-鄉鎮市區電子發票B2C開立資料集](https://data.gov.tw/dataset/36862)是由政府資料開方平台所提供的資料集。由於對全台的B2C電子發票發票發布狀況感到好奇，進而想對此資料進行分析。原始資料集的時間從2021/01記錄到2024/12，本專案在機器學習訓練階段時只使用2021年的資料。

The Income and Housing Price Consumption Analysis -B2C E-Invoice Dataset for Townships and Districts is provided by the Government Open Data Platform. Out of curiosity about the issuance of B2C e-invoices across Taiwan, I decided to analyze this dataset.The original dataset is from 2021/01 to 2024/12, but this model is trained by the data from 2021.

## 資料型態(Data Structure)
此資料集共記錄了發票年月、縣市代碼、縣市名稱、鄉鎮市區代碼、鄉鎮市區名稱、行業名稱、平均開立張數、平均開立金額、平均客單價九個欄位。其中需要特別注意

* 平均開立張數 = 開立總張數 \ 該維度下營業人的家數
* 平均開立金額 = 開立總金額 \ 該維度下營業人的家數
* 平均客單價 = 開立客單價 \ 該維度下營業人的家數

This dataset records nine fields: invoice year-month, county/city code, county/city name, township/district code, township/district name, industry name, average number of invoices issued, average issued amount, and average transaction price.

Some key points to note:

* Average number of invoices issued = Total number of invoices issued / Number of businesses in that category
* Average issued amount = Total issued amount / Number of businesses in that category
* Average transaction price = Total transaction price / Number of businesses in that category



## EDA
|                | mean         | std          | var          | min   | max       |
|----------------|--------------|--------------|--------------|-------|-----------|
| 平均開立張數(Avg. invoices issued)   | 1.389867e+04 | 1.381884e+04 | 1.909603e+08 | 16    | 309155    |
| 平均開立金額(Avg. issued amount)   | 4.881683e+06 | 1.797752e+07 | 3.231912e+14 | 33590 | 542486725 |
| 平均客單價(Avg. transaction price)     | 4.279705e+02 | 9.122108e+02 | 8.321416e+05 | 61    | 48869     |


### 清理 (Data Cleaning)
---
* 發票年月：格視為年月合併，如202406。拆分成year和month
* 丟棄 縣市代碼 和 鄉鎮市區代碼
* 將 縣市名稱 和 鄉鎮市區名稱 兩欄位合併成 「縣鄉鎮市區」，並進行經緯度轉換
* 針對「行業名稱」進行one-hot encoding

* Invoice year-month: Initially stored as a combined "YYYYMM" format (e.g., 202406), split into year and month.
* Dropped fields: county/city code and township/district code.
* Merged location fields: Combined county/city name and township/district name into a single "county-township-district" field and converted them into latitude and longitude coordinates.
* Industry name encoding: Applied one-hot encoding to the industry name field.

### Pipeline
---
使用Catboost作為模型訓練資料並使用grid search調參
最後使用MAPE判斷訓練結果。訓練完成後 MAPE = 0.2
CatBoost was used as the model for training, and hyperparameter tuning was performed using grid search.
The final model was evaluated using Mean Absolute Percentage Error (MAPE), achieving a MAPE of 0.2.

### 結論 Conclude
這是我第一次將自己的訓練開源，我知道預測結果不盡理想
我會繼續學習的
This is my first time open-sourcing my training process. I know the prediction results are not perfect, but I will keep learning and improving!
