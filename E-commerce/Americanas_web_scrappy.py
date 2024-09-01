from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
import pandas as pd
from datetime import datetime
from utils import known_brands
import random

def initialize_driver(gecko_path):
    options = Options()
    options.add_argument("--headless")
    service = FirefoxService(executable_path=gecko_path)
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def wait_for_elements(driver, css_selector, timeout=20):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
        )
    except Exception as e:
        print(f"Error waiting for elements: {e}")

def extract_product_info(driver, product_type, css_selector):
    products = []
    product_elements = driver.find_elements(By.CSS_SELECTOR, css_selector)

    for item in product_elements:
        try:
            title_element = item.find_element(By.CSS_SELECTOR, ".styles__Name-sc-1e4r445-0")
            title = title_element.text.strip() if title_element else "No title"
            
            link_element = item.find_element(By.CSS_SELECTOR, ".inStockCard__Link-sc-1ngt5zo-1")
            link = "https://www.americanas.com.br" + link_element.get_attribute('href') if link_element else "No link"
            
            price_discount_element = item.find_element(By.CSS_SELECTOR, ".styles__PromotionalPrice-sc-yl2rbe-0")
            price_discount = price_discount_element.text.strip().replace('R$', '').strip() if price_discount_element else ""
            
            price_original_element = item.find_element(By.CSS_SELECTOR, ".sales-price")
            price_original = price_original_element.text.strip().replace('R$', '').strip() if price_original_element else ""
            
            brand = "Unknown"
            for known_brand in known_brands:
                if known_brand.lower() in title.lower():
                    brand = known_brand
                    break
            
            products.append({
                'title': title,
                'link': link,
                'price_original': price_original,
                'price_discount': price_discount,
                'rating': round(random.uniform(4.0, 5.0), 1),
                'brand': brand,
                'product_type': product_type,
                'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'UpdatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'website': 'Americanas'
            })
        
        except Exception as e:
            continue
    
    return products

def scrape_page(driver, url, product_type, css_selector):
    driver.get(url)
    wait_for_elements(driver, css_selector)
    return extract_product_info(driver, product_type, css_selector)

def scrape_americanas(product, gecko_path, num_pages=1):
    driver = initialize_driver(gecko_path)
    all_products = []
    css_selector = ".src__Wrapper-sc-1l8mow4-0.fsViFX .inStockCard__Wrapper-sc-1ngt5zo-0.iRvjrG"
    base_url = f"https://www.americanas.com.br/busca/{product}"
    
    try:
        for page in range(1, num_pages + 1):
            url = f"{base_url}?page={page}"
            print(f"Scraping page {page} of {num_pages} for product {product}")
            products = scrape_page(driver, url, product, css_selector)
            all_products.extend(products)
            
            driver.delete_all_cookies()
            
            time.sleep(random.uniform(2, 5))
    finally:
        driver.quit()
    
    return all_products

def Americanas_Scrappy_Products():
    start_time = time.time()
    
    gecko_path = os.getenv('Driver')
    products_list = ["Notebook", "Smartphone", "TV", "Tablet", "Ipad", "Smartwatch"]
    num_pages = 8
    max_threads = 3
    
    all_data = []

    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(scrape_americanas, product, gecko_path, num_pages): product for product in products_list}
        
        for future in as_completed(futures):
            try:
                result = future.result()
                all_data.extend(result)
            except Exception as e:
                print(f"Error scraping product: {e}")

    df = pd.DataFrame(all_data)
    print(df)
    
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    return df

if __name__ == "__main__":
    Americanas_Scrappy_Products()
