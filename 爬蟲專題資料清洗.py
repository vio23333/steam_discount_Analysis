import pandas as pd
from datetime import datetime
import re

# ✅ 讀取你爬蟲的 Excel（自己改檔名）
df = pd.read_excel("steam_specials_selenium_pages.xlsx")

# ===============================
# 折扣欄位："-50%" → 50
# ===============================
df["Discount_Num"] = (
    df["Discount"]
    .astype(str)
    .str.replace("-", "")
    .str.replace("%", "")
    .replace("", "0")
    .astype(float)
)

# 加入折扣等級：每 10% 一個等級
# 1–10% → 1
# 11–20% → 2
# ...
# 91–100% → 10

def to_discount_level(x):
    if pd.isna(x):
        return None
    x = float(x)
    if x <= 0:
        return None
    return int((x - 1) // 10 + 1)

df["Discount_Level"] = df["Discount_Num"].apply(to_discount_level)
# ===============================
# 原價欄位：去掉 NT$、逗號
# ===============================
def price_to_float(x):
    if pd.isna(x):
        return None
    x = str(x)
    x = x.replace("NT$", "").replace(",", "").strip()
    return float(x) if x.replace(".", "", 1).isdigit() else None

df["Original_Price_Num"] = df["Original_Price"].apply(price_to_float)


def price_to_level(price):
    if pd.isna(price):
        return None
    price = float(price)
    if price >= 2000:
        return 11
    else:
        # 每200元一級，1~200 -> 1, 201~400 -> 2, ...
        level = int((price - 1) // 200) + 1
        return level

df["Original_Price_Level"] = df["Original_Price_Num"].apply(price_to_level)


# ===============================
# 折扣後價格欄位：去掉 NT$、逗號
# ===============================
def price_to_float(x):
    if pd.isna(x):
        return None
    x = str(x)
    x = x.replace("NT$", "").replace(",", "").strip()
    return float(x) if x.replace(".", "", 1).isdigit() else None

df["Final_Price_Num"] = df["Final_Price"].apply(price_to_float)

# ===============================
# 轉換發售日期資料為年份差/季度/季度差
# 解析年份與月份
# ===============================
def parse_year(date_str):
    if pd.isna(date_str):
        return None
    year_match = re.search(r"(\d{4})", str(date_str))
    return int(year_match.group(1)) if year_match else None


def parse_month(date_str):
    if pd.isna(date_str):
        return None

    # 找到數字月份（1–12）
    month_match = re.search(r"(\d{1,2}) 月", str(date_str))
    if month_match:
        month = int(month_match.group(1))
        return month if 1 <= month <= 12 else None

    return None


df["Release_Year"] = df["Release_Date"].apply(parse_year)
df["Release_Month"] = df["Release_Date"].apply(parse_month)

# ===============================
# 轉換成季度（Q1~Q4 對應 1~4）
# ===============================

def month_to_quarter(m):
    if m is None:
        return None
    return (m - 1) // 3 + 1

df["Release_Quarter"] = df["Release_Month"].apply(month_to_quarter)

# ===============================
# 距今幾年
# ===============================

current_year = datetime.now().year
df["Years_Since_Release"] = df["Release_Year"].apply(
    lambda y: current_year - y if y is not None else None
)

# ===============================
# 距今幾季度
# ===============================

today = datetime.now()
current_absolute_q = today.year * 4 + ((today.month - 1) // 3 + 1)

def absolute_quarter(row):
    y = row["Release_Year"]
    q = row["Release_Quarter"]
    if pd.isna(y) or pd.isna(q):
        return None
    return y * 4 + q

df["Release_Absolute_Quarter"] = df.apply(absolute_quarter, axis=1)

df["Quarters_Since_Release"] = df["Release_Absolute_Quarter"].apply(
    lambda x: current_absolute_q - x if x is not None else None
)
# ===============================
# 評價等級（中文）→ 數字
# ===============================
review_map = {
    "壓倒性好評": 5,
    "極度好評": 4,
    "大多好評": 3,
    "好評": 2,
    "褒貶不一": 1,
    "負評": 0,
}

def map_review(x):
    if pd.isna(x):
        return None
    for key in review_map:
        if key in str(x):
            return review_map[key]
    return None

df["Review_Score"] = df["Review_Level"].apply(map_review)

# ===============================
# 輸出成 Excel,重新排序
# ===============================
desired_order = [
    "Name",
    "Original_Price_Num",
    "Original_Price_Level",
    "Final_Price_Num",
    "Discount_Num",
    "Discount_Level",
    "Release_Quarter",
    "Years_Since_Release",
    "Quarters_Since_Release",         
    "Review_Score",
]

column_zh_map = {
    "Name": "遊戲名稱",
    "Original_Price_Num": "原價(NT$)",
    "Original_Price_Level": "原價等級",
    "Final_Price_Num": "特價(NT$)",
    "Discount_Num": "折扣(%)",
    "Discount_Level":"折扣等級",
    "Release_Quarter": "發布季度",
    "Years_Since_Release": "上市年數",
    "Quarters_Since_Release": "上市季度數",
    "Review_Score": "評價分數",
}

# 希望的順序排序欄位
df = df[desired_order]

# 替換成中文欄位名稱
df = df.rename(columns=column_zh_map)

df.to_excel("steam_specials_cleaned data.xlsx", index=False)

print("\n🎉 完成！已輸出 steam_specials_cleaned data.xlsx")
print(f"共 {len(df)} 筆資料，更改完成")
