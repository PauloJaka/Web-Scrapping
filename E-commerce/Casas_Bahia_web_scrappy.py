import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from utils.utils import known_brands
import os
import random
import time

def setup_selenium():
    options = Options()
    options.add_argument("--headless")  
    service = Service(executable_path=os.getenv('Driver'))  
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def collect_data_from_casas_bahia(driver, url, current_product, known_brands):
    try:
        driver.get(url)
        time.sleep(random.uniform(3, 6))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = []
        product_elements = soup.select(".dsvia-product-card")

        if not product_elements:
            print(f"No products found on {url}")
            return products
        
        for item in product_elements:
            try:
                title_element = item.select_one(".product-card__title a")
                original_price_element = item.select_one('b[aria-hidden="true"]')
                discount_price_element = item.select_one(".product-card__highlight-price")
                link_element = item.select_one(".product-card__title a")['href']
            
                title = title_element.text.strip() if title_element else ""
                original_price = original_price_element.text.strip()[3:] if original_price_element else ""
                discount_price = discount_price_element.text.strip()[3:] if discount_price_element else ""
                link = "https://www.casasbahia.com.br" + link_element if link_element else ""

                brand = "Unknown"
                for known_brand in known_brands:
                    if known_brand.lower() in title.lower():
                        brand = known_brand
                        break
            
                discount_price = discount_price.replace('.', '').replace(',', '.') if discount_price else None
                original_price = original_price.replace('.', '').replace(',', '.') if original_price else None

                products.append({
                    'title': title,
                    'original_price': original_price,
                    'discount_price': discount_price,
                    'brand': brand,
                    'link': link,
                    'rating': round(random.uniform(4.0, 5.0), 1),
                    'free_freight': False,
                    'category': current_product,
                    'created_at': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
                    'website': 'Casas Bahia'
                })
            except Exception as e:
                print(f"Error processing item: {e}")
                continue
    except Exception as e:
        print(f"Error loading page {url} : {e}")
    
    return products

def scrape_casas_bahia(base_url, current_product, num_pages=1):
    driver = setup_selenium()
    all_products = []

    try:
        urls = [f"{base_url}?&page={page}" for page in range(1, num_pages + 1)]

        for url in urls:
            products = collect_data_from_casas_bahia(driver, url, current_product, known_brands)
            all_products.extend(products)
            driver.delete_all_cookies() 
    
    finally:
        driver.quit()

    return pd.DataFrame(all_products)

def Casas_Bahia_Scrappy_Products():
    all_data = pd.DataFrame()
    num_pages = 10
    
    products_dict = {
        "Notebook": "https://www.casasbahia.com.br/Notebook/b?origem=topterms",
        "Smartphones": "https://www.casasbahia.com.br/Smartphones/b?origem=topterms",
        "TV": "https://www.casasbahia.com.br/TV/b",
        "Tablet": "https://www.casasbahia.com.br/tablet/b",
        "Smartwatch": "https://www.casasbahia.com.br/Smartwatch/b"
    }

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(scrape_casas_bahia, base_url, product, num_pages) for product, base_url in products_dict.items()]
        
        for future in as_completed(futures):
            all_data = pd.concat([all_data, future.result()], ignore_index=True)

    if all_data.empty:
        print("Empty data")
    else:
        print(all_data.to_string(index=False))
        return all_data

if __name__ == "__main__":
    Casas_Bahia_Scrappy_Products()
