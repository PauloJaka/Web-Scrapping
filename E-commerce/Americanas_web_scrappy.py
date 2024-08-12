from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re
from datetime import datetime
from utils import known_brands
import random

def initialize_driver(gecko_path, headless=True):
    firefox_options = Options()
    if headless:
        firefox_options.add_argument("--headless")
    
    service = FirefoxService(executable_path=gecko_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver

def extract_product_info(soup, product_type):
    products = []
    product_elements = soup.select(".src__Wrapper-sc-1l8mow4-0.fsViFX .inStockCard__Wrapper-sc-1ngt5zo-0.iRvjrG")

    for item in product_elements:
        try:
            title_element = item.select_one(".styles__Name-sc-1e4r445-0")
            title = title_element.text.strip() if title_element else "No title"
            
            link_element = item.select_one(".inStockCard__Link-sc-1ngt5zo-1")
            link = "https://www.americanas.com.br" + link_element['href'] if link_element else "No link"
            
            price_discount_element = item.select_one(".styles__PromotionalPrice-sc-yl2rbe-0")
            price_discount = price_discount_element.text.strip().replace('R$', '').strip() if price_discount_element else ""
            
            price_original_element = item.select_one(".sales-price")
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
            print(f"Error processing product: {e}")
            continue
    
    return products

def scrape_americanas(gecko_path, base_url, product_type, num_pages=1, headless=True):
    driver = initialize_driver(gecko_path, headless)
    all_products = []

    for page in range(1, num_pages + 1):
        url = f"{base_url}?page={page}"
        driver.get(url)
        time.sleep(5)  
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        products = extract_product_info(soup, product_type)
        all_products.extend(products)
    
    driver.quit()
    return all_products

def main():
    gecko_path = os.getenv('Driver')
    products_list = ["notebook", "smartphone"]
    num_pages = 1

    all_data = pd.DataFrame()

    for product in products_list:
        base_url = f"https://www.americanas.com.br/busca/{product}"
        products = scrape_americanas(gecko_path, base_url, product, num_pages, headless=True)
        df = pd.DataFrame(products)
        all_data = pd.concat([all_data, df], ignore_index=True)
    
    if all_data.empty:
        print("No data collected")
    else:
        print(all_data.to_string(index=False))

if __name__ == "__main__":
    main()
