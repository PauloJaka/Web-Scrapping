import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

known_brands = [
    "ACER", "ASUS", "SAMSUNG", "Dell", "Positivo", "Lenovo", "VAIO",
    "HP", "Apple", "Multilaser", "Anvazise", "ASHATA", "Santino", "MSI",
    "Marca Fácil", "Microsoft", "AWOW", "Gateway", "Compaq", "DAUERHAFT",
    "SGIN", "Luqeeg", "Kiboule", "LG", "Panasonic", "Focket", "Toughbook",
    "LTI", "GIGABYTE", "Octoo", "Chip7 Informática", "GLOGLOW", "GOLDENTEC",
    "KUU", "HEEPDD", "Adamantiun", "Naroote", "Jectse", "Heayzoki"
]

def collect_data_from_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    products = []
    product_elements = soup.select(".ui-search-result__wrapper")
    
    if not product_elements:
        print("Nenhum elemento de produto encontrado. Verifique os seletores de CSS.")
    
    for item in product_elements:
        try:
            title_element = item.select_one(".ui-search-item__title")
            price_element = item.select_one(".price-tag-fraction")
            rating_element = item.select_one(".ui-search-reviews__rating-number")
            
            title = title_element.text.strip() if title_element else "No title"
            price = price_element.text.strip() if price_element else "No price"
            rating = rating_element.text.strip() if rating_element else ' '
            
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
                'CreatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'UpdatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'website': 'Mercado Livre'
            })
        except Exception as e:
            print(f"Erro ao processar item: {e}")
            continue
    return products

def scrape_mercado_livre(base_url, num_pages=1):
    all_products = []
    
    for page in range(1, num_pages + 1):
        url = f"{base_url}_Desde_{(page-1)*50 + 1}"
        products = collect_data_from_page(url)
        all_products.extend(products)
    
    return pd.DataFrame(all_products)

def main():
    base_url = "https://lista.mercadolivre.com.br/notebook"  
    num_pages = 1  

    df = scrape_mercado_livre(base_url, num_pages)

    if df.empty:
        print("Nenhum dado foi coletado. Verifique os seletores de CSS e a estrutura da página.")
    else:
        print(df.to_string(index=False))

if __name__ == "__main__":
    main()
