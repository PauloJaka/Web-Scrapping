from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
import pandas as pd
import time
from datetime import datetime, timedelta
import os
from utils import known_brands
import concurrent.futures

def initialize_driver(gecko_path, headless=True):
    print("Iniciando o driver...")
    firefox_options = Options()
    if headless:
        firefox_options.add_argument("--headless")
    
    service = FirefoxService(executable_path=gecko_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver

def collect_data_from_page(driver, product_type):
    products = []
    product_elements = driver.find_elements(By.CSS_SELECTOR, "article.productCard")
    print(f"Found {len(product_elements)} product elements on the page")
    
    for index, item in enumerate(product_elements):
        try:
            name_element = item.find_element(By.CSS_SELECTOR, "span.nameCard")
            link_element = item.find_element(By.CSS_SELECTOR, "a.productLink")
            original_price_element = item.find_element(By.CSS_SELECTOR, "span.oldPriceCard")
            discount_price_element = item.find_element(By.CSS_SELECTOR, "span.priceCard")

            name = name_element.text
            link = link_element.get_attribute("href")
            original_price = original_price_element.text
            discount_price = discount_price_element.text

            try:
                star_div = item.find_element(By.CSS_SELECTOR, "div.sc-e32b6973-3.dlFNar.estrelasAvaliacao")
                star = star_div.find_elements(By.CSS_SELECTOR, "div.sc-e32b6973-2.iYjzAb.estrelaAvaliacao")
                star_quantity = len(star)
            except:
                star_quantity = 0

            brand = "Unknown"
            for known_brand in known_brands:
                if known_brand.lower() in name.lower():
                    brand = known_brand
                    break
            
            original_price = original_price_element.text.strip()[3:] if original_price_element else ""
            discount_price = discount_price_element.text.strip()[3:] if discount_price_element else ""
                
            discount_price = discount_price.replace('.', '').replace(',', '.') if discount_price else None
            original_price = original_price.replace('.', '').replace(',', '.') if original_price else None

            products.append({
                'name': name,
                'original_price': original_price,
                'discount_price': discount_price,
                'brand': brand,
                'link': link,
                'rating': star_quantity,  
                'category': product_type,
                'free_freight': 'Frete grátis' in item.text,
                'created_at': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
                'website': 'KaBuM'
            })
        except Exception as e:
            print(f"Error processing product {index + 1}: {str(e)}")
            continue
    
    return products

def scrape_product_category(gecko_path, base_url, product_type, num_pages=3, headless=True):
    driver = initialize_driver(gecko_path, headless)
    all_products = []

    try:
        for page in range(1, num_pages + 1):
            url = f"{base_url}?page_number={page}&page_size=100"
            print(f"Accessing URL: {url}")
            driver.get(url)
            time.sleep(10) 
            print(f"Current page title: {driver.title}")
            page_products = collect_data_from_page(driver, product_type)
            all_products.extend(page_products)
    finally:
        driver.quit()

    df = pd.DataFrame(all_products)
    print(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
    return df

def KaBum_Scrappy_Products():
    gecko_path = os.getenv('Driver')
    category_urls = {
        "Smartphone": "https://www.kabum.com.br/celular-smartphone/smartphones",
        "TV": "https://www.kabum.com.br/tv",
        "Tablet": "https://www.kabum.com.br/tablets-ipads-e-e-readers",
        "Notebook": "https://www.kabum.com.br/computadores/notebooks",
        "Smartwatch": "https://www.kabum.com.br/busca/Smartwatch"
    }
    num_pages = 3

    all_data = pd.DataFrame()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(scrape_product_category, gecko_path, base_url, product_type, num_pages, headless=True)
            for product_type, base_url in category_urls.items()
        ]
        for future in concurrent.futures.as_completed(futures):
            df = future.result()
            if not df.empty and 'product_type' in df.columns:
                product_type = df['product_type'].iloc[0]
                print(f"Tamanho do DataFrame após {product_type}: {len(df)} registros")
            else:
                print("DataFrame vazio ou sem coluna 'product_type'")
            all_data = pd.concat([all_data, df], ignore_index=True)

    print(f"Tamanho final do DataFrame: {len(all_data)} registros")
    if not all_data.empty:
        print(all_data.to_string(index=False))
        return all_data
    else:
        print("O DataFrame final está vazio")
        

if __name__ == "__main__":
    KaBum_Scrappy_Products()