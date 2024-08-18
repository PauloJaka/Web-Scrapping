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
from datetime import datetime, timedelta
from utils import known_brands

def create_driver(gecko_path):
    options = Options()
    options.add_argument("--headless")
    service = FirefoxService(executable_path=gecko_path)
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def wait_for_elements(driver, css_selector, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
    )

def collect_data(driver, url, product_type):
    driver.get(url)
    wait_for_elements(driver, ".s-main-slot .s-result-item")
    
    products = []
    for item in driver.find_elements(By.CSS_SELECTOR, ".s-main-slot .s-result-item"):
        try:
            title_element = item.find_element(By.CSS_SELECTOR, "h2 a span")
            price_element = item.find_element(By.CSS_SELECTOR, ".a-price-whole")
            rating_element = item.find_element(By.CSS_SELECTOR, ".a-icon-alt")
            link_element = item.find_element(By.CSS_SELECTOR, "a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal")
            original_price_element = item.find_element(By.CSS_SELECTOR, ".a-price.a-text-price .a-offscreen")
                
            try:
                free_freight = item.find_element(By.CSS_SELECTOR, "span[aria-label='Opção de frete GRÁTIS disponível']")
                free_freight = True
            except:
                free_freight = False
            link = link_element.get_attribute("href") if link_element else "No link"
            title = title_element.text
            discount_price = price_element.text
            rating = rating_element.get_attribute("innerHTML").split()[0] if rating_element else "No rating"
            original_price = original_price_element.text if original_price_element else ""
            
            discount_price = discount_price.replace('.', '').replace(',', '.') if discount_price else None
            original_price = original_price.replace('.', '').replace(',', '.') if original_price else None
            rating = rating.replace('.', '').replace(',', '.') if discount_price else None
            brand = next((b for b in known_brands if b.lower() in title.lower()), "Unknown")
            products.append({
                'title': title,
                'discount_price': discount_price,
                    'original_price': original_price,
                    'brand': brand,
                    'rating': rating,
                    'link': link,
                    'free_freight': free_freight,
                    'category': product_type,
                    'created_at': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
                    'website': 'Amazon'
                })
        except Exception as e:
            continue
    
    return products

def get_max_pages(driver, base_url):
    driver.get(base_url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".s-pagination-strip"))
        )
        
        page_elements = driver.find_elements(By.CSS_SELECTOR, ".s-pagination-item")
        
        page_numbers = []
        for elem in page_elements:
            text = elem.text
            if text.isdigit():
                page_numbers.append(int(text))
        
        if page_numbers:
            return max(page_numbers)  
    except Exception as e:
        print(f"Error finding max pages: {e}")
    return 1 

def scrape_product_pages(product, gecko_path):
    driver = create_driver(gecko_path)
    base_url = f"https://www.amazon.com.br/s?k={product}"
    all_products = []
    
    try:
        max_pages = get_max_pages(driver, base_url)
        
        for page in range(1, max_pages + 1):
            url = f"{base_url}&page={page}"
            print(f"Scraping page {page} of {max_pages}")
            all_products.extend(collect_data(driver, url, product))
    finally:
        driver.quit()
    
    return all_products

def main():
    start_time = time.time()
    
    gecko_path = os.getenv('Driver')
    products_list = ["Notebook", "Smartphone", "TV", "Tablet", "Ipad", "Smartwatch"] 
    max_threads = 3 # change the value of the threads or just default max
    
    all_data = []
    
    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(scrape_product_pages, product, gecko_path): product for product in products_list}
        
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

if __name__ == "__main__":
    main()
