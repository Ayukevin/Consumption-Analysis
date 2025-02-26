import pandas as pd
import sqlite3

# 讀取 CSV 檔
csv_file = "所得房價消費分析_處理後_2021.csv"
df = pd.read_csv(csv_file, encoding="utf-8-sig")

# 連接到 SQLite 資料庫 (若無此 DB，會自動建立)
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

# 刪除舊表（如果已經存在，避免重複載入）
cursor.execute("DROP TABLE IF EXISTS consumption")

# 將 DataFrame 存入 SQLite
df.to_sql("consumption", conn, if_exists="replace", index=False)

print("successfully to transfer csv to  data.db")

# 關閉連線
conn.close()

#python csv_2_sql.py