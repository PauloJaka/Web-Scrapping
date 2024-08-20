from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
import pandas as pd
import time
from datetime import datetime
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
    product_elements = driver.find_elements(By.CSS_SELECTOR, "article.sc-9d1f1537-7.hxuzLm.productCard")
    
    for item in product_elements:
        try:
            descount_price_element = item.find_element(By.CSS_SELECTOR, "span.priceCard")
            name_element = item.find_element(By.CSS_SELECTOR, "span.nameCard")
            link_element = item.find_element(By.CSS_SELECTOR, "a")
            original_price__element = item.find_element(By.CSS_SELECTOR, "span.oldPriceCard")

            try:
                star_div = item.find_element(By.CSS_SELECTOR, "div.sc-e32b6973-3.dlFNar.estrelasAvaliacao")
                star = star_div.find_elements(By.CSS_SELECTOR, "div.sc-e32b6973-2.iYjzAb.estrelaAvaliacao")
                star_quantity = len(star)
            except:
                star_quantity = 3

            descount_price = descount_price_element.text
            name = name_element.text
            link = link_element.get_attribute("href")
            original_price = original_price__element.text

            brand = "Unknown"
            for known_brand in known_brands:
                if known_brand.lower() in name.lower():
                    brand = known_brand
                    break

            products.append({
                'name': name,
                'price_original': original_price,
                'price_discount': descount_price,
                'brand': brand,
                'link': link,
                'rating': star_quantity,  
                'product_type': product_type,
                'free_freight': False,
                'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'UpdatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'website': 'KaBuM'
            })
        except Exception as e:
            continue
    return products

def scrape_product_category(gecko_path, base_url, product_type, num_pages=3, headless=True):
    driver = initialize_driver(gecko_path, headless)
    all_products = []

    try:
        for page in range(1, num_pages + 1):
            url = f"{base_url}?page_number={page}&page_size=100"
            print(f"Buscando a página {page} para {product_type}...")
            driver.get(url)
            time.sleep(5)
            all_products.extend(collect_data_from_page(driver, product_type))
    finally:
        driver.quit()

    return pd.DataFrame(all_products)

def main():
    gecko_path = os.getenv('Driver')
    category_urls = {
        "Smartphone": "https://www.kabum.com.br/celular-smartphone/smartphones",
        "TV": "https://www.kabum.com.br/tv",
        "Tablets, iPads e E-readers": "https://www.kabum.com.br/tablets-ipads-e-e-readers",
        "Notebook": "https://www.kabum.com.br/computadores/notebooks"
    }
    num_pages = 3

    all_data = pd.DataFrame()

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(category_urls)) as executor:
        futures = [
            executor.submit(scrape_product_category, gecko_path, base_url, product_type, num_pages, headless=True)
            for product_type, base_url in category_urls.items()
        ]
        for future in concurrent.futures.as_completed(futures):
            df = future.result()
            all_data = pd.concat([all_data, df], ignore_index=True)
            print(f"Tamanho do DataFrame após {df['product_type'].iloc[0]}: {len(df)} registros")

    print(f"Tamanho final do DataFrame: {len(all_data)} registros")
    print(all_data.to_string(index=False))

if __name__ == "__main__":
    main()
