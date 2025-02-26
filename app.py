import streamlit as st
import pandas as pd
import plotly.express as px
from catboost import CatBoostRegressor
import sqlite3

#streamlit run app.py

#頁面標題
st.set_page_config(page_title="台灣鄉鎮市區消費分析", layout="wide")

#連接 SQLite DB：加速加載方式
def load_data_sql(query="SELECT * FROM consumption"):
    conn = sqlite3.connect("data.db")  
    df = pd.read_sql(query, conn) 
    conn.close() 
    return df

df = load_data_sql()

#讀取機器學習模型
@st.cache_data
def load_model():
    model = CatBoostRegressor()
    model.load_model("catboost_model_ALL_grid.cbm")
    return model

model = load_model()

st.title("📊 台灣鄉鎮市區消費分析 - 以電子發票為例")
st.markdown("""
本專案使用政府開放數據 [所得房價消費分析-鄉鎮市區電子發票B2C開立資料集](https://data.gov.tw/dataset/36862) 進行台灣各鄉鎮市區消費狀況分析。
            
原始資料集中含2021-2024年資料，在此只取2021年的資料進行分析。  
**我們將探討：**
            
✅ 各縣市的 **平均開立金額** 和 **平均客單價** 分布  
✅ 2021 年各月份內的電子發票 B2C 數據變化  
✅ 使用機器學習進行 消費金額預測，並分析其誤差與特徵重要性  
""")

# 使用者選擇篩選side bar
st.sidebar.header("📌 互動篩選條件")
selected_city = st.sidebar.selectbox("選擇縣市", ["全部"] + sorted(df["縣市名稱"].unique()))
selected_industry = st.sidebar.selectbox("選擇行業", ["全部"] + sorted(df["行業名稱"].unique()))
selected_month = st.sidebar.slider("選擇月份", min_value=1, max_value=12, value=6)

# 根據篩選條件產生 SQL 查詢
query = "SELECT * FROM consumption WHERE 1=1"
if selected_city != "全部":
    query += f" AND 縣市名稱 = '{selected_city}'"
if selected_industry != "全部":
    query += f" AND 行業名稱 = '{selected_industry}'"
query += f" AND month = {selected_month}"

filtered_df = load_data_sql(query)
st.header("📊 **查詢結果(前五筆)**")
st.write(filtered_df.head())

# EDA
st.header("📈 數據探索分析 (EDA)")
st.markdown("""
|                | mean         | std          | var          | min   | max       |
|----------------|--------------|--------------|--------------|-------|-----------|
| 平均開立張數(Avg. invoices issued)   | 1.389867e+04 | 1.381884e+04 | 1.909603e+08 | 16    | 309155    |
| 平均開立金額(Avg. issued amount)   | 4.881683e+06 | 1.797752e+07 | 3.231912e+14 | 33590 | 542486725 |
| 平均客單價(Avg. transaction price)     | 4.279705e+02 | 9.122108e+02 | 8.321416e+05 | 61    | 48869     |
""")



# 全台消費地圖
st.header("📍 全台灣消費平均開立金額 (視覺化地圖)")
if "lat" in filtered_df.columns and "lng" in filtered_df.columns:
    # 移除 lat/lng 欄位中的 NaN 避免錯誤
    filtered_df = filtered_df.dropna(subset=["lat", "lng"])
    st.write(f"✅ 共有 {len(filtered_df)} 比資料點")
 
    fig = px.scatter_map(
        filtered_df,
        lat="lat", lon="lng",
        size="平均開立金額",
        color="平均開立金額",
        hover_name="鄉鎮市區名稱",
        title="全台消費平均開立金額",
        color_continuous_scale="plasma",
        zoom=7,
        center={"lat": 23.5, "lon": 121},  #地圖中心對準台灣
    )
    
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("無法顯示地圖，未偵測到經緯度座標（lat, lng）。")

# 各縣市的消費金額趨勢
st.header("📊 各縣市消費金額趨勢 (堆疊長條圖)")
# 資料處理
grouped = df.groupby(["縣市名稱", "month"])["平均開立金額"].sum().unstack()
grouped_sorted = grouped.sum(axis=1).sort_values().index
grouped = grouped.loc[grouped_sorted]
# 將資料轉換為長格式以適應 Plotly Express
grouped_reset = grouped.reset_index()
grouped_melted = grouped_reset.melt(id_vars=["縣市名稱"], var_name="month", value_name="平均開立金額")
# 使用 Plotly Express 繪製堆疊長條圖
fig = px.bar(grouped_melted, x="縣市名稱", y="平均開立金額", color="month", 
             title="各縣市歷月 B2C 電子發票平均開立金額", 
             labels={"縣市名稱": "縣市名稱", "平均開立金額": "平均開立金額"}, 
             barmode="stack", color_continuous_scale="coolwarm")
st.plotly_chart(fig)

# 縣市與行業的熱力圖
st.header("🔥 各縣市 & 行業的消費行為熱力圖")
heatmap_data = df.groupby(["縣市名稱", "行業名稱"])["平均開立金額"].sum().unstack().fillna(0)
fig = px.imshow(
    heatmap_data,  # 熱力圖數據
    labels=dict(x="行業名稱", y="縣市名稱", color="平均開立金額"),  
    x=heatmap_data.columns,  # X 軸：行業名稱
    y=heatmap_data.index,    # Y 軸：縣市名稱
    color_continuous_scale="RdBu_r",  # 色彩：紅藍對比
    aspect="auto"  # 保持長寬比
)

st.plotly_chart(fig, use_container_width=True)


#預測分析
st.header("📈 機器學習預測分析")
X = df.drop(columns=['平均開立金額', 'year','縣市代碼','縣市名稱','鄉鎮市區代碼','鄉鎮市區名稱','縣鄉鎮市區']) 
y_true = df['平均開立金額'] 

# 進行預測
y_pred = model.predict(X)
df['預測開立金額'] = y_pred
st.markdown("""
使用Catboost作為模型訓練資料並使用grid search調參
最後使用MAPE判斷訓練結果。訓練完成後 MAPE = 0.2
""")

# 預測 vs 實際繪圖
st.subheader("📉 實際 vs 預測開立金額")
comparison_df = pd.DataFrame({"實際值": y_true, "預測值": y_pred})

# 使用 Plotly Express 繪製散布圖並加上回歸直線
fig = px.scatter(comparison_df, x="實際值", y="預測值",
                  title="機器學習預測表現對比", labels={"實際值": "實際開立金額", "預測值": "預測開立金額"})
st.plotly_chart(fig)

# 各縣市預測與實際金額比較
st.header("🏙各縣市預測金額 vs 實際金額")
city_comparison = df.groupby("縣市名稱").agg({"平均開立金額": "sum", "預測開立金額": "sum"}).reset_index()

fig = px.bar(
    city_comparison,
    x="縣市名稱",
    y=["平均開立金額", "預測開立金額"],
    title="各縣市的預測金額 vs 實際金額",
    labels={"value": "金額", "variable": "金額種類"},
    barmode="group",  # 讓兩個數據條放在一起比較
    height=500
)
st.plotly_chart(fig, use_container_width=True)


# 各行業預測與實際金額比較
st.header("🏢 各行業預測金額 vs 實際金額")
industry_comparison = df.groupby("行業名稱").agg({"平均開立金額": "sum", "預測開立金額": "sum"}).reset_index()
fig = px.bar(
    industry_comparison,
    x="行業名稱",
    y=["平均開立金額", "預測開立金額"],
    title="各行業的預測金額 vs 實際金額",
    labels={"value": "金額", "variable": "金額種類"},
    barmode="group",
    height=600
)

st.plotly_chart(fig, use_container_width=True)


# 📌 **尾段**
st.markdown("---")
st.markdown("📌 **專案開源於 GitHub，數據來源自政府資料開放平台，歡迎大家一起優化分析！**")