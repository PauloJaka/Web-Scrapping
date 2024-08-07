import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from utils import known_brands

# URLs base para as categorias
category_urls = {
   # "Celular & Smartphone": "https://www.kabum.com.br/celular-smartphone/smartphones"
    #"TV": "https://www.kabum.com.br/tv",
   # "Tablets, iPads e E-readers": "https://www.kabum.com.br/tablets-ipads-e-readers",
   "Computador": "https://www.kabum.com.br/computadores/notebooks"
}

def collect_data_from_page(url, current_product):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    products = []
    product_elements = soup.select(".productCard")
    
    if not product_elements:
        print("No product elements found.")
    
    for item in product_elements:
        try:
            title_element = item.select_one(".nameCard")
            price_element = item.select_one(".priceCard")
            rating_element = item.select_one(".estrelaAvaliacao")
            free_freight_element = item.select_one(".productCard-freeFreight")

            title = title_element.text.strip() if title_element else "No title"
            price = price_element.text.strip() if price_element else "No price"
            rating = rating_element.text.strip() if rating_element else 'No rating'
            free_freight = free_freight_element and "Frete grátis" in free_freight_element.text

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
                'free_freight': free_freight,
                'category': current_product,
                'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'UpdatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'website': 'Kabum'
            })
        except Exception as e:
            print(f"Error: {e}")
            continue
    return products

def scrape_kabum(base_url, current_product, num_pages=1):
    all_products = []
    
    for page in range(1, num_pages + 1):
        url = f"{base_url}?page_number={page}"
        products = collect_data_from_page(url, current_product)
        all_products.extend(products)
    
    return pd.DataFrame(all_products)

def main(categories):
    all_data = pd.DataFrame()
    num_pages = 1  

    for category, base_url in categories.items():
        df = scrape_kabum(base_url, category, num_pages)
        all_data = pd.concat([all_data, df], ignore_index=True)

    if all_data.empty:
        print("Empty data")
    else:
        print(all_data.to_string(index=False))

if __name__ == "__main__":
    main(category_urls)
