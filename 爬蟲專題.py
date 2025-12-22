from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import random

def crawl_page(driver, page_num):
    url = f"https://store.steampowered.com/search/?specials=1&page={page_num}"
    driver.get(url)
    time.sleep(2 + random.random())

    rows = driver.find_elements(By.CLASS_NAME, "search_result_row")
    result = []

    # 如果這一頁沒有任何遊戲 → 回傳空陣列，主程式會自動 break
    if len(rows) == 0:
        return result

    for row in rows:
        try:
            name = row.find_element(By.CLASS_NAME, "title").text.strip()
        except:
            name = None

        try:
            release = row.find_element(By.CLASS_NAME, "search_released").text.strip()
        except:
            release = None

        try:
            review = row.find_element(By.CLASS_NAME, "search_review_summary")
            review_level = review.get_attribute("data-tooltip-html")
            if review_level:
                review_level = review_level.split("<br>")[0].strip()
        except:
            review_level = None

        try:
            original_price = row.find_element(By.CLASS_NAME, "discount_original_price").text.strip()
            final_price = row.find_element(By.CLASS_NAME, "discount_final_price").text.strip()
        except:
            original_price = None
            final_price = None

        try:
            discount = row.find_element(By.CLASS_NAME, "discount_pct").text.strip()
        except:
            discount = None

        result.append({
            "Name": name,
            "Original_Price": original_price,
            "Final_Price": final_price,
            "Discount": discount,
            "Release_Date": release,
            "Review_Level": review_level
        })

    return result


if __name__ == "__main__":
    print("🚀 開始爬取 Steam 特價資料（Selenium 分頁版，自動停止）\n")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    all_data = []
    page = 1

    while True:
        print(f"📄 正在抓第 {page} 頁...")

        page_data = crawl_page(driver, page)

        #自動偵測最後一頁：沒資料就停止
        if len(page_data) == 0:
            print("✅ 已無更多頁面，資料爬取完成！")
            break

        all_data.extend(page_data)

        page += 1
        time.sleep(1 + random.random())

    driver.quit()

    df = pd.DataFrame(all_data)
    df.to_excel("steam_specials_selenium_pages.xlsx", index=False)

    print("\n✅ 完成！已輸出 steam_specials_selenium_pages.xlsx")
    print(f"✅ 共抓取 {len(df)} 筆資料。")
