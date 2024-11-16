from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# WebDriverの設定
service = Service(ChromeDriverManager().install())  # webdriver_managerで自動的にドライバを取得
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # ヘッドレスモードで実行
driver = webdriver.Chrome(service=service, options=options)

# URLを指定
url = 'https://house.ocn.ne.jp/toshi/nisshou/13/'
driver.get(url)

# テーブルが表示されるまで待機
try:
    wait = WebDriverWait(driver, 10)
    tables = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'cmnTable2')))
    print(f"Found {len(tables)} tables!")
except Exception as e:
    print("Tables not found!", e)
    driver.quit()
    exit()

# テーブルデータをすべて取得
data = []
for table in tables:
    rows = table.find_elements(By.TAG_NAME, 'tr')
    for row in rows[1:]:  # ヘッダーをスキップ
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells:
            city_name = row.find_element(By.TAG_NAME, 'th').text.strip()
            sunshine = cells[0].text.strip()
            rank_city = cells[1].text.strip()
            rank_national = cells[2].text.strip()
            data.append([city_name, sunshine, rank_city, rank_national])

# pandasデータフレームに変換
headers = ['市区名', '日照時間', '都内順位', '全国順位']
df = pd.DataFrame(data, columns=headers)

# CSVファイルに保存
csv_file = 'sunshine_hours.csv'
df.to_csv(csv_file, index=False, encoding='utf-8-sig')

print(f"Data has been saved to {csv_file}.")

# ブラウザを閉じる
driver.quit()

