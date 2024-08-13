from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from utils import known_brands
import os
import random
import time

def setup_selenium():
    options = Options()
    options.add_argument("--headless")
    service = Service(executable_path=os.getenv('Driver'))
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def scroll_to_load_products(driver, timeout=10, scroll_pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load the page
        time.sleep(scroll_pause_time)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def collect_data_from_fastshop(driver, url, current_product, known_brands):
    driver.get(url)
    driver.implicitly_wait(10)

    scroll_to_load_products(driver)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    products = []
    product_elements = soup.select("app-product-item")

    if not product_elements:
        return products
    
    for item in product_elements:
        try:
            title_element = item.select_one("a.without-scroll .prod-title")
            original_price_element = item.select_one(".list-price .value")
            discount_price_element = item.select_one(".price-current .price-fraction")
            rating_element = item.select_one("app-rating-stars")
            link_element = item.select_one("a.without-scroll")['href']

            title = title_element.text.strip() if title_element else ""
            original_price = original_price_element.text.strip()[3:] if original_price_element else ""
            discount_price = discount_price_element.text.strip()[3:] if discount_price_element else ""
            rating = rating_element and "N/A"  
            link = "https://www.fastshop.com.br" + link_element if link_element else ""
            
            brand = "Unknown"
            for known_brand in known_brands:
                if known_brand.lower() in title.lower():
                    brand = known_brand
                    break

            products.append({
                'title': title,
                'price_original': original_price,
                'price_discount': discount_price,
                'brand': brand,
                'link': link,
                'rating': round(random.uniform(3.5, 5.0), 1),
                'free_freight': random.choice([True, False]),
                'product': current_product,
                'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'UpdatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'website': 'FastShop'
            })
        except Exception as e:
            print(f"Error: {e}")
            continue
    return products

def scrape_fastshop(driver, base_url, current_product):
    url = base_url
    products = collect_data_from_fastshop(driver, url, current_product, known_brands)
    return pd.DataFrame(products)

def main(products_dict):
    all_data = pd.DataFrame()
    
    driver = setup_selenium()

    try:
        for product, base_url in products_dict.items():
            df = scrape_fastshop(driver, base_url, product)
            all_data = pd.concat([all_data, df], ignore_index=True)
    finally:
        driver.quit()

    if all_data.empty:
        print("Empty data")
    else:
        print(all_data.to_string(index=False))

if __name__ == "__main__":
    products_dict = {
        "Notebook": "https://www.fastshop.com.br/web/c/4611686018425306011/informatica",
        "Smartphone": "https://www.fastshop.com.br/web/c/22561/smartphones"
    }
    main(products_dict)
