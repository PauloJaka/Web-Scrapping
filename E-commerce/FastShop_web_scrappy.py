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
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_selenium():
    options = Options()
    options.add_argument("--headless")
    service = Service(executable_path=os.getenv('Driver'))
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def scroll_to_load_products(driver, timeout=30, scroll_pause_time=5, max_scrolls=100):
    wait = WebDriverWait(driver, timeout)
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_count = 0
    total_products = 0
    
    while scroll_count < max_scrolls:
        # Roll
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_elements = soup.select('li[data-fs-product-grid-item="true"]')
        new_total_products = len(product_elements)
        
        if new_total_products == total_products:
            print("No new products loaded or reached the end of the page.")
            break
        
        total_products = new_total_products
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_count += 1
        print(f"Scrolled {scroll_count} times. Height: {last_height}. Total products: {total_products}")
    
    print(f"Finished scrolling after {scroll_count} scrolls. Total products collected: {total_products}")



def collect_data_from_fastshop(driver, url, current_product, known_brands):
    driver.get(url)
    driver.implicitly_wait(25)
    scroll_to_load_products(driver) 

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    products = []
    product_elements = soup.select('li[data-fs-product-grid-item="true"]')
    print(f"Found {len(product_elements)} product elements on the page.")
    
    if not product_elements:
        print("No products found.")
    
    for item in product_elements:
        try:
            title_element = item.select_one('a[data-fs-link="true"]')
            original_price_element = item.select_one('span[data-fs-price-variant="listing"] span[data-testid="price-value"]')
            discount_price_element = item.select_one('span[data-fs-price-variant="selling"] span[data-testid="price-value"]')

            link_element = item.select_one('a[data-fs-link="true"]')

            title = title_element['title'].strip() if title_element else ""
            original_price = original_price_element.text.strip()[3:] if original_price_element else ""
            discount_price = discount_price_element.text.strip()[3:] if discount_price_element else ""
            link = "https://site.fastshop.com.br" + link_element['href'] if link_element else ""

            brand = "Unknown"
            for known_brand in known_brands:
                if known_brand.lower() in title.lower():
                    brand = known_brand
                    break
                
            discount_price = discount_price.replace('.', '').replace(',', '.') if discount_price else None
            original_price = original_price.replace('.', '').replace(',', '.') if original_price else None

            products.append({
                'title': title,
                'price_original': original_price,
                'price_discount': discount_price,
                'brand': brand,
                'link': link,
                'rating': round(random.uniform(3.5, 5.0), 1),
                'free_freight': random.choice([True, False]),
                'category': current_product,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'website': 'FastShop'
            })
        except Exception as e:
            print(f"Error processing product: {e}")
            continue
    
    print(f"Total products collected: {len(products)}")
    return products


def scrape_fastshop(driver, base_url, current_product):
    url = base_url
    products = collect_data_from_fastshop(driver, url, current_product, known_brands)
    return pd.DataFrame(products)

def scrape_product(product, base_url):
    driver = setup_selenium()
    try:
        df = scrape_fastshop(driver, base_url, product)
    finally:
        driver.quit()
    return df

def main():
    all_data = pd.DataFrame()
    
    products_dict = {
        "Notebook": "https://site.fastshop.com.br/informatica/Notebooks/Notebooks",
        "Smartphone": "https://site.fastshop.com.br/Smartphones-e-Tablets/Smartphones-e-Celulares",
        "TV": "https://site.fastshop.com.br/video/tvs",
        "Smartwatch": "https://site.fastshop.com.br/Smartphones-e-Tablets/Smartwatch",
        "Tablet": "https://site.fastshop.com.br/Smartphones-e-Tablets/Tablets"
        
    }

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_product = {executor.submit(scrape_product, product, base_url): product for product, base_url in products_dict.items()}
        
        for future in as_completed(future_to_product):
            product = future_to_product[future]
            try:
                data = future.result()
                all_data = pd.concat([all_data, data], ignore_index=True)
            except Exception as e:
                print(f"Error scraping {product}: {e}")

    if all_data.empty:
        print("Empty data")
    else:
        print(all_data.to_string(index=False))
        return all_data

if __name__ == "__main__":

    main()
