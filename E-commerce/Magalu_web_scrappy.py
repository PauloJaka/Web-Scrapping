from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re
from utils import known_brands
from datetime import datetime 

def initialize_driver(gecko_path, headless=True):
    firefox_options = Options()
    if headless:
        firefox_options.add_argument("--headless")  
    
    service = FirefoxService(executable_path=gecko_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver

def extract_product_info(soup, product_type):
    products = []
    ul_element = soup.find('ul', class_='sc-hknOHE RHqaG sc-kMribo kyNLGC sc-cGNDeh jUKQOs')
    
    if ul_element:
        product_elements = ul_element.find_all('li', recursive=False)


    for item in product_elements:
        try:
            title_element = item.select_one('h2[data-testid="product-title"]')
            title = title_element.text.strip() if title_element else "Título não encontrado"
            
            link_element = item.select_one('a[data-testid="product-card-container"]')
            link = link_element['href'] if link_element else "Link não encontrado"
            link = f"https://www.magazineluiza.com.br{link}" 
            
            price_original_element = item.select_one('p[data-testid="price-original"]')
            price_original = price_original_element.text.strip().replace('R$', '').strip() if price_original_element else ""
            
            price_discount_element = item.select_one('p[data-testid="price-value"]')
            price_discount = price_discount_element.text.strip().replace('R$', '').strip() if price_discount_element else ""
            
            review_element = item.select_one('span[format="score-count"]')
            review_text = review_element.text.strip() if review_element else ""
            review_match = re.match(r'([\d\.]+)', review_text)
            review = review_match.group(1) if review_match else ""
            
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
                'rating': review,
                'free_freight': False,  
                'brand': brand,
                'product_type': product_type,
                'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'UpdatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'website': 'Magalu'
            })
        
        except Exception as e:
            print(f"Erro ao processar o produto: {e}")
            continue
    
    return products

def scrape_magalu(gecko_path, base_url, product_type, num_pages=1, headless=True):
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
    products_list = ["Notebook", "Smartphone"] 
    num_pages = 1

    all_data = pd.DataFrame()

    for product in products_list:
        base_url = f"https://www.magazineluiza.com.br/busca/{product}/"
        products = scrape_magalu(gecko_path, base_url, product, num_pages, headless=False)
        df = pd.DataFrame(products)
        all_data = pd.concat([all_data, df], ignore_index=True)
    
    print(all_data.to_string(index=False))

if __name__ == "__main__":
    main()
