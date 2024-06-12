import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv('load.env')
user_agent = os.getenv('USER_AGENT')

def scrap_extract(job_title, location, page):
    # Configurar a URL de busca
    url = f"https://br.indeed.com/jobs?q={job_title}&l={location}&start={page}"
    
    headers = { 
        "User-Agent": user_agent
    }
    r = requests.get(url, headers= headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    print(soup)
    return soup

def transform(soup):
    jobs = soup.find_all('div', class_= 'jobsearch-SerpJobCard')
    print(jobs)
    for item in jobs:
        title = item.find('a').text.strip()
        print(title)
    return 

c = scrap_extract('Dados', 'Brasil', 0)

transform(c)
    