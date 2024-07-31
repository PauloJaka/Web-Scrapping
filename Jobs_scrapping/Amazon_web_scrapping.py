from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
import pandas as pd
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import os

known_brands = [
    "ACER", "ASUS", "SAMSUNG", "Dell", "Positivo", "Lenovo", "VAIO",
    "HP", "Apple", "Multilaser", "Anvazise", "ASHATA", "Santino", "MSI",
    "Marca Fácil", "Microsoft", "AWOW", "Gateway", "Compaq", "DAUERHAFT",
    "SGIN", "Luqeeg", "Kiboule", "LG", "Panasonic", "Focket", "Toughbook",
    "LTI", "GIGABYTE", "Octoo", "Chip7 Informática", "GLOGLOW", "GOLDENTEC",
    "KUU", "HEEPDD", "Adamantiun", "Naroote", "Jectse", "Heayzoki"
]

def initialize_driver(gecko_path, headless=True):
    firefox_options = Options()
    if headless:
        firefox_options.add_argument("--headless")  # No interface
    
    service = FirefoxService(executable_path=gecko_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver

def collect_data_from_page(driver, product_type):
    products = []
    product_elements = driver.find_elements(By.CSS_SELECTOR, ".s-main-slot .s-result-item")
    
    for item in product_elements:
        try:
            title_element = item.find_element(By.CSS_SELECTOR, "h2 a span")
            price_element = item.find_element(By.CSS_SELECTOR, ".a-price-whole")
            rating_element = item.find_element(By.CSS_SELECTOR, ".a-icon-alt")
            
            title = title_element.text
            price = price_element.text
            rating = rating_element.get_attribute("innerHTML").split()[0] if rating_element else "No rating"
            
            brand = "Unknown"
            for known_brand in known_brands:
                if known_brand.lower() in title.lower():
                    brand = known_brand
                    break

            products.append({
                'title': title,
                'price': price,
                'brand': brand,
                'rating': rating,
                'product_type': product_type,
                'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'UpdatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'website': 'Amazon'
            })
        except Exception as e:
            continue
    return products

def get_product_type_from_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    product_type = query_params.get('k', [''])[0]
    return product_type

def scrape_amazon(gecko_path, base_url, num_pages=1, headless=True):
    product_type = get_product_type_from_url(base_url)
    driver = initialize_driver(gecko_path, headless)
    
    all_products = []
    
    for page in range(1, num_pages + 1):
        url = f"{base_url}&page={page}"
        driver.get(url)
        
        time.sleep(5)
        
        products = collect_data_from_page(driver, product_type)
        all_products.extend(products)
    
    # Fechar o driver
    driver.quit()
    
    return pd.DataFrame(all_products)

def main():
    gecko_path = os.getenv('Driver')
    base_url = "https://www.amazon.com.br/s?k=notebook"
    num_pages = 1  

    df = scrape_amazon(gecko_path, base_url, num_pages, headless=True)

    # Printar os dados
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
