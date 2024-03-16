from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymysql
import datetime

# 设置 Chrome WebDriver 路径
webdriver_path = "./chromedriver.exe"

# 创建 Chrome WebDriver
service = Service(webdriver_path)
driver = webdriver.Chrome(service=service)

# 打开网页
url = 'https://www.woolworths.com.au/shop/browse/fruit-veg'  # 替换为目标网站的URL
driver.get(url)

# 等待页面加载完成
wait = WebDriverWait(driver, 10)  # 等待10秒

# 等待特定元素加载完成
target_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'wc-product-tile.ng-star-inserted')))

# 输出找到的元素数量
print("找到的元素数量:", len(target_elements))

productArr = []
# 遍历每个元素
for element in target_elements:
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", element)
    if shadow_root:
        # 定位元素下的class为primary的div
        primary_div = shadow_root.find_element(By.CSS_SELECTOR, '.primary')
        primary_text = primary_div.text

        # 定位元素下的class为price-per-cup的span
        price_per_cup_span = shadow_root.find_element(By.CSS_SELECTOR, '.price-per-cup')
        price_per_cup_text = price_per_cup_span.text

        # 定位元素下的class为title的div
        title_div = shadow_root.find_element(By.CSS_SELECTOR, '.title')
        title_text = title_div.text

        # 定位元素下的class为product-tile-image的div的子元素image的src
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
    # 等待元素下的class为primary的div加载完成
    # element_text = element.text
    # print("元素文本内容:", element_text)
    # # 找到元素下的img元素
    # img_element = element.find_element(By.TAG_NAME, 'img')
    # # 获取图片的src属性值
    # img_src = img_element.get_attribute('src')
    # print(img_src)
# 关闭 WebDriver
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
# # 准备要执行的SQL语句
sql = "INSERT INTO goods (name, provider, price, special, unit, image, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)"
#
try:
    # 执行SQL语句
    cursor.executemany(sql, productArr)

    # 提交事务
    conn.commit()
    print("数据插入成功！")

except Exception as e:
    # 发生异常时回滚事务
    conn.rollback()
    print("数据插入失败:", e)

finally:
    # 关闭游标和连接
    cursor.close()
    conn.close()

