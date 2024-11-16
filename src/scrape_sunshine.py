from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import os

# 都道府県コードリスト（01: 北海道, 13: 東京など）
prefecture_codes = [f"{i:02}" for i in range(1, 48)]
base_url = "https://house.ocn.ne.jp/toshi/nisshou/"

# 保存先ディレクトリ
output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

# WebDriverの設定
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # ヘッドレスモードで実行
driver = webdriver.Chrome(service=service, options=options)

# データを格納するリスト
data = []

# 全都道府県のデータを収集
for code in prefecture_codes:
    url = f"{base_url}{code}/"
    print(f"Processing {url}...")  # 進行状況を出力

    try:
        driver.get(url)

        # テーブルが表示されるまで待機
        wait = WebDriverWait(driver, 10)
        tables = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'cmnTable2')))
        print(f"Found {len(tables)} tables!")

        # 各テーブルを解析
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, 'tr')
            for row in rows[1:]:  # ヘッダーをスキップ
                cells = row.find_elements(By.TAG_NAME, 'td')
                if cells:
                    city_name = row.find_element(By.TAG_NAME, 'th').text.strip()
                    sunlight_hours = cells[0].text.strip().replace('時間', '').replace(',', '')  # '時間'と','を削除
                    rank_within_pref = cells[1].text.strip()
                    rank_national = cells[2].text.strip()
                    try:
                        # 数値に変換してデータに追加
                        data.append([city_name, float(sunlight_hours), rank_within_pref, rank_national, code])
                    except ValueError:
                        print(f"数値に変換できなかった値: {sunlight_hours}（{city_name}）")

    except Exception as e:
        print(f"Error processing {url}: {e}")

# WebDriverを閉じる
driver.quit()

# データをDataFrameに変換
columns = ["市区名", "日照時間", "都道府県内順位", "全国順位", "都道府県コード"]
df = pd.DataFrame(data, columns=columns)

# 日照時間の降順にソート
df.sort_values(by="日照時間", ascending=False, inplace=True)

# データをCSVとして保存
output_file = os.path.join(output_dir, "日照時間ランキング_Selenium.csv")
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"データの収集が完了しました！保存先: {output_file}")
