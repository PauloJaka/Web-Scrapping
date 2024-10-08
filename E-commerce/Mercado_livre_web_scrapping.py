import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from utils import known_brands
import re
from concurrent.futures import ThreadPoolExecutor

def collect_data_from_page(url, current_product, known_brands):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    products = []
    product_elements = soup.select(".ui-search-result__wrapper")
    
    if not product_elements:
        print("No product elements found.")
    
    for item in product_elements:
        try:
            link_elementText = item.select_one('a')
            original_price_element = item.select_one(".andes-money-amount__fraction")  
            rating_element = item.select_one(".ui-search-reviews__rating-number")
            free_freight_element = item.select_one(".ui-pb-highlight-content .ui-pb-highlight")
            link_element = item.select_one("a.ui-search-link")
            discount_price_element = item.select_one(".ui-search-installments-prefix span") 
            
            title = link_elementText.text.strip()if link_elementText else "No title"
            original_price = original_price_element.text.strip() if original_price_element else "No original price"  
            rating = rating_element.text.strip() if rating_element else 'No rating'
            free_freight = free_freight_element and "Frete grátis" in free_freight_element.text

            link_element = item.select_one("a.ui-search-link")
            if not link_element:
                link_element = item.select_one("h2.poly-box.poly-component__title a")
            link = link_element['href'] if link_element else None

            if discount_price_element:  
                discount_price_text = discount_price_element.text.strip()  
                discount_price = re.findall(r'\d+\.?\d*', discount_price_text)
                discount_price = discount_price[0] if discount_price else ""
            else:
                discount_price = ""

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
                'rating': rating,
                'free_freight': free_freight,
                'product': current_product,
                'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'UpdatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'website': 'Mercado Livre'
            })
        except Exception as e:
            print(f"Error: {e}")
            continue
    return products

def scrape_mercado_livre(base_url, current_product, num_pages=1):
    all_products = []
    
    with ThreadPoolExecutor(max_workers=4) as executor:  
        futures = []
        for page in range(1, num_pages + 1):
            url = f"{base_url}_Desde_{(page-1)*50 + 1}"
            futures.append(executor.submit(collect_data_from_page, url, current_product, known_brands))
        
        for future in futures:
            all_products.extend(future.result())
    
    return pd.DataFrame(all_products)

def main(products):
    all_data = pd.DataFrame()
    num_pages = 10

    for product in products:
        base_url = f"https://lista.mercadolivre.com.br/{product}"
        df = scrape_mercado_livre(base_url, product, num_pages)
        all_data = pd.concat([all_data, df], ignore_index=True)

    if all_data.empty:
        print("Empty data")
    else:
        print(all_data.to_string(index=False))

if __name__ == "__main__":
    products_list = ["notebook"]#, "smartphone", "TV", "tablet"]  
    main(products_list)
