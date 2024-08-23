from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
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

def collect_data_from_casas_bahia(driver, url, current_product, known_brands):
    driver.get(url)
    time.sleep(random.uniform(3, 6))  

    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = []
        product_elements = soup.select(".dsvia-product-card")

        if not product_elements:
            print(f"No products found on {url}")
            return products
        
        for item in product_elements:
            try:
                title_element = item.select_one(".product-card__title a")
                original_price_element = item.select_one(".product-card__price-value")
                discount_price_element = item.select_one(".product-card__discount-price")
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

                products.append({
                    'title': title,
                    'price_original': original_price,
                    'price_discount': discount_price,
                    'brand': brand,
                    'link': link,
                    'rating': round(random.uniform(3.5, 5.0), 1),
                    'free_freight': False,
                    'product': current_product,
                    'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'UpdatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'website': 'Casas Bahia'
                })
            except Exception as e:
                print(f"Error processing item: {e}")
                continue
    except Exception as e:
        print(f"Error loading page {url}: {e}")
    
    return products

def scrape_casas_bahia(driver, base_url, current_product, num_pages=1):
    all_products = []
    
    for page in range(1, num_pages + 1):
        url = f"{base_url}?&page={page}"
        print(f"Scraping page {page}: {url}")
        products = collect_data_from_casas_bahia(driver, url, current_product, known_brands)
        all_products.extend(products)
        
        driver.delete_all_cookies()
    
    return pd.DataFrame(all_products)

def main(products_dict):
    all_data = pd.DataFrame()
    num_pages = 2
    driver = setup_selenium()
    time.sleep(5)
    
    try: 
        for product, base_url in products_dict.items():
            df = scrape_casas_bahia(driver, base_url, product, num_pages)
            all_data = pd.concat([all_data, df], ignore_index=True)
    finally:
        driver.quit()

    if all_data.empty:
        print("Empty data")
    else:
        print(all_data.to_string(index=False))

if __name__ == "__main__":
    products_dict = {
        "Notebook": "https://www.casasbahia.com.br/Notebook/b?origem=topterms",
        #"Smartphones": "https://www.casasbahia.com.br/Smartphones/b?origem=topterms",
        #"TV": "https://www.casasbahia.com.br/TV/b",
        #"Tablet": "https://www.casasbahia.com.br/tablet/b"
    }
    main(products_dict)
