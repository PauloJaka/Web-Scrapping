from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
import pandas as pd
import time
from datetime import datetime
import os

# Lista de marcas conhecidas
known_brands = [
    "ACER", "ASUS", "SAMSUNG", "Dell", "Positivo", "Lenovo", "VAIO",
    "HP", "Apple", "Multilaser", "Anvazise", "ASHATA", "Santino", "MSI",
    "Marca Fácil", "Microsoft", "AWOW", "Gateway", "Compaq", "DAUERHAFT",
    "SGIN", "Luqeeg", "Kiboule", "LG", "Panasonic", "Focket", "Toughbook",
    "LTI", "GIGABYTE", "Octoo", "Chip7 Informática", "GLOGLOW", "GOLDENTEC",
    "KUU", "HEEPDD", "Adamantiun", "Naroote", "Jectse", "Heayzoki",
    "Motorola", "Xiaomi", "Nokia", "Poco", "realme", "Infinix", "Blu",
    "Gshield", "Geonav", "Redmi", "Gorila Shield", "intelbras", "TCL",
    "Tecno", "Vbestlife", "MaiJin", "SZAMBIT", "Otterbox", "Sony"
]

def initialize_driver(gecko_path, headless=True):
    firefox_options = Options()
    if headless:
        firefox_options.add_argument("--headless")
    
    service = FirefoxService(executable_path=gecko_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver

def collect_data_from_page(driver):
    products = []
    product_elements = driver.find_elements(By.CSS_SELECTOR, "article.sc-9d1f1537-7.hxuzLm.productCard")
    
    for item in product_elements:
        try:
            price_element = item.find_element(By.CSS_SELECTOR, "span.priceCard")
            name_element = item.find_element(By.CSS_SELECTOR, "span.nameCard")
            link_element = item.find_element(By.CSS_SELECTOR, "a")

            price = price_element.text
            name = name_element.text
            link = link_element.get_attribute("href")

            brand = "Unknown"
            for known_brand in known_brands:
                if known_brand.lower() in name.lower():
                    brand = known_brand
                    break

            products.append({
                'name': name,
                'price': price,
                'brand': brand,
                'link': link,
                'free_freight': False,  
                'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'UpdatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'website': 'KaBuM'
            })
        except Exception as e:
            continue
    return products

def scrape_kabum(gecko_path, base_url, num_pages=1, headless=True):
    driver = initialize_driver(gecko_path, headless)
    
    all_products = []
    
    for page in range(1, num_pages + 1):
        url = f"{base_url}?page_number={page}"
        driver.get(url)
        
        time.sleep(5)
        
        products = collect_data_from_page(driver)
        all_products.extend(products)
    
    driver.quit()
    
    return pd.DataFrame(all_products)

def main():
    gecko_path = os.getenv('Driver')
    category_urls = {
        # "Celular & Smartphone": "https://www.kabum.com.br/celular-smartphone/smartphones",
        # "TV": "https://www.kabum.com.br/tv",
        # "Tablets, iPads e E-readers": "https://www.kabum.com.br/tablets-ipads-e-readers",
        "Computador": "https://www.kabum.com.br/computadores/notebooks"
    }
    num_pages = 1

    all_data = pd.DataFrame()

    for category, base_url in category_urls.items():
        df = scrape_kabum(gecko_path, base_url, num_pages, headless=True)
        all_data = pd.concat([all_data, df], ignore_index=True)

    
    print(all_data.to_string(index=False))

if __name__ == "__main__":
    main()
