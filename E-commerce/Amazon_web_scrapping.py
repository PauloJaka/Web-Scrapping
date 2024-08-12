from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
import pandas as pd
import time
from datetime import datetime
import os
from utils import known_brands
import re

def initialize_driver(gecko_path, headless=True):
    firefox_options = Options()
    if headless:
        firefox_options.add_argument("--headless")  
    
    service = FirefoxService(executable_path=gecko_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver

def collect_data_from_page(driver, product_type):
    products = []
    product_elements = driver.find_elements(By.CSS_SELECTOR, ".s-main-slot .s-result-item")
    
    for item in product_elements:
        try:
            title_element = item.find_element(By.CSS_SELECTOR, "h2 a span")
            price_element_original = item.find_element(By.CSS_SELECTOR, ".a-price-whole")  
            rating_element = item.find_element(By.CSS_SELECTOR, ".a-icon-alt")
            link_element = item.find_element(By.CSS_SELECTOR, "a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal")
            
            title = title_element.text
            original_price = price_element_original.text 
            rating = rating_element.get_attribute("innerHTML").split()[0] if rating_element else "No rating"
            link = link_element.get_attribute("href") if link_element else "No link"
            
            try:
                free_freight = item.find_element(By.CSS_SELECTOR, "span[aria-label='Opção de frete GRÁTIS disponível']")
                free_freight = True
            except:
                free_freight = False
            
            brand = "Unknown"
            for known_brand in known_brands:
                if known_brand.lower() in title.lower():
                    brand = known_brand
                    break

            products.append({
                'title': title,
                'price_original': original_price,   
                'brand': brand,
                'rating': rating,
                'free_freight': free_freight,
                'link': link,
                'product_type': product_type,
                'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'UpdatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'website': 'Amazon'
            })
        except Exception as e:
            continue
    return products


def scrape_amazon(gecko_path, base_url, product_type, num_pages=1, headless=True):
    driver = initialize_driver(gecko_path, headless)
    
    all_products = []
    
    for page in range(1, num_pages + 1):
        url = f"{base_url}&page={page}"
        driver.get(url)
        
        time.sleep(5)
        
        products = collect_data_from_page(driver, product_type)
        all_products.extend(products)
    
    
    driver.quit()
    
    return pd.DataFrame(all_products)

def main():
    gecko_path = os.getenv('Driver')
    products_list = ["Notebook", "Smartphone"] 
    num_pages = 1  

    all_data = pd.DataFrame()

    for product in products_list:
        base_url = f"https://www.amazon.com.br/s?k={product}"
        df = scrape_amazon(gecko_path, base_url, product, num_pages, headless=True)
        all_data = pd.concat([all_data, df], ignore_index=True)

    
    print(all_data.to_string(index=False))

if __name__ == "__main__":
    main()
