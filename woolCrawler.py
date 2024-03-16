from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymysql
import datetime

# Chrome WebDriver
webdriver_path = "./chromedriver.exe"

# Chrome WebDriver
service = Service(webdriver_path)
driver = webdriver.Chrome(service=service)

url = 'https://www.woolworths.com.au/shop/browse/fruit-veg'  # 替换为目标网站的URL
driver.get(url)

wait = WebDriverWait(driver, 10)  # 等待10秒

target_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'wc-product-tile.ng-star-inserted')))

print("找到的元素数量:", len(target_elements))

productArr = []

for element in target_elements:
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", element)
    if shadow_root:
        primary_div = shadow_root.find_element(By.CSS_SELECTOR, '.primary')
        primary_text = primary_div.text

        price_per_cup_span = shadow_root.find_element(By.CSS_SELECTOR, '.price-per-cup')
        price_per_cup_text = price_per_cup_span.text

        title_div = shadow_root.find_element(By.CSS_SELECTOR, '.title')
        title_text = title_div.text

        image_div = shadow_root.find_element(By.CSS_SELECTOR, '.product-tile-image img')
        image_src = image_div.get_attribute('src')
        print("Primary:", primary_text)
        print("Price Per Cup:", price_per_cup_text)
        print("Title:", title_text)
        print("Image Source:", image_src)
        productArr.append((
            title_text,
            "Woolworths",
            primary_text,
            '',
            price_per_cup_text,
            image_src,
            datetime.datetime.now()
        ))

# close WebDriver
driver.quit()

conn = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="root",
    database="price-store"
)
cursor = conn.cursor()
#
# SQL
sql = "INSERT INTO goods (name, provider, price, special, unit, image, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)"
#
try:
    # execute SQL
    cursor.executemany(sql, productArr)

    # commit
    conn.commit()
    print("insert success!")

except Exception as e:
    # rollback
    conn.rollback()
    print("insert failed:", e)

finally:
    # close
    cursor.close()
    conn.close()

