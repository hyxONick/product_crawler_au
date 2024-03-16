import os
import requests
from lxml import html, etree
import pymysql
import datetime
productArr = []
for i in range(1, 3):
    # Set the URL of the target website
    url = "https://www.coles.com.au/browse/fruit-vegetables?pid=homepage_cat_explorer_fruit_vege&page=" + str(i)

    # Send an HTTP request and get the page content
    response = requests.get(url)

    # Check whether the request is successful
    if response.status_code == 200:
        # Parse page content using lxml
        page_content = html.fromstring(response.content)
        # Select all product sections
        elements_with = page_content.xpath('//section[@data-testid="product-tile"]')

        # Positioning product price
        for product in elements_with:
            info = product.find('.//span[@class="price__value"]')
            infoWas = product.find('.//span[@class="price__was"]')
            infoWasText = ''
            print(infoWas, 'infoWas')
            infoCurrent = product.find('.//div[@class="price__calculation_method"]')
            print(info)
            if info is not None:
                infoText = info.text.strip()
                infoCurrentText = infoCurrent.text.strip() if infoCurrent is not None else None
                infoWasText = infoWas.text.strip() if infoWasText else ''
                # print(infoWasText, 'infoWasText')
                # Locate product details page links
                childrenUrl = product.find('.//a[@class="product__link"]').get('href')
                responseChild = requests.get('https://www.coles.com.au' + childrenUrl)
                childPage_content = html.fromstring(responseChild.content)
                # Locate product pictures
                image_elements = childPage_content.xpath('//img[@data-testid="product-image-0"]')
                image = image_elements[0] if image_elements else None
                image_src = image.get('src') if image is not None else None
                productName = image.get('alt').split('|')[0] if image is not None else None
                # Regular image link, fetch the image1
                productArr.append((
                    productName,
                    "Coles",
                    infoText,
                    infoWasText,
                    infoCurrentText,
                    image_src,
                    datetime.datetime.now()
                ))
                print((
                    productName,
                    "Coles",
                    infoWasText,
                    infoText,
                    infoCurrentText,
                    image_src,
                    datetime.datetime.now()
                ))
                if image_src:
                    image_response = requests.get(image_src)
                    image_data = image_response.content
                    # Generate the save path based on image alt and price info
                    save_path = f"G:/colesImgFolder/{productName}_{infoText}.jpg"
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    # Open the folder to save the picture
                    with open(save_path, "wb") as f:
                        f.write(image_data)
print(productArr)

conn = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="root",
    database="price-store"
)
cursor = conn.cursor()

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

