import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

def format_price(price_text):
    price = re.findall(r'\d{1,3}(?:\.\d{3})*,\d{2}', price_text)
    return price[0] if price else ""

def format_rating(rating_text):
    rating = re.findall(r'\d+', rating_text)
    return rating[0] if rating else ""

def collect_data_from_kalunga_page(url, current_product):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    print(response)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    products = []
    product_elements = soup.select(".blocoproduto__row")
    
    if not product_elements:
        print("No product elements found.")
    
    for item in product_elements:
        try:
            title_element = item.select_one(".blocoproduto__title")
            original_price_element = item.select_one("p.blocoproduto__text--bold.blocoproduto__text--small.blocoproduto__prazo.mb-0 span")
            discount_price_element = item.select_one(".blocoproduto__price")
            rating_element = item.select_one(".reviews__star_text")
            free_freight_element = item.select_one(".seloslot__list--fretegratismunicipios")
            link_element = item.select_one(".blocoproduto__link")
            
            title = title_element.text.strip() if title_element else "No title"
            
            original_price = original_price_element.text.strip() if original_price_element else ""
            original_price = format_price(original_price)

            discount_price = discount_price_element.text.strip() if discount_price_element else ""
            discount_price = format_price(discount_price)

            rating = rating_element.text.strip() if rating_element else ""
            rating = format_rating(rating)

            free_freight = free_freight_element and "Frete grátis" in free_freight_element.text
            link = "https://www.kalunga.com.br" + link_element['href'] if link_element else ""

            products.append({
                'title': title,
                'price_original': original_price,
                'price_discount': discount_price,
                'rating': rating,
                'free_freight': free_freight,
                'link': link,
                'product': current_product,
                'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'UpdatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'website': 'Kalunga'
            })
        except Exception as e:
            print(f"Error: {e}")
            continue
    return products

def scrape_kalunga(base_url, current_product, num_pages=1):
    all_products = []
    
    for page in range(1, num_pages + 1):
        url = f"{base_url}?p={page}"
        products = collect_data_from_kalunga_page(url, current_product)
        all_products.extend(products)
    
    return pd.DataFrame(all_products)

def main(products):
    all_data = pd.DataFrame()
    num_pages = 1  

    for product in products:
        base_url = f"https://www.kalunga.com.br/busca/{product}"
        df = scrape_kalunga(base_url, product, num_pages)
        all_data = pd.concat([all_data, df], ignore_index=True)

    if all_data.empty:
        print("Empty data")
    else:
        print(all_data.to_string(index=False))

if __name__ == "__main__":
    products_list = ["notebook", "smartphone", "tv", "tablets"]  
    main(products_list)
