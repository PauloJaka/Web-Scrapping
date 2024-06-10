import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

user_agent = os.getenv('USER_AGENT')

def scrape_indeed_jobs(job_title, location):
    # Configurar a URL de busca
    url = f"https://www.indeed.com/jobs?q={job_title}&l={location}"
    
    headers = {
        "User-Agent": user_agent
    }
    
    # Enviar uma requisição HTTP para o Indeed
    response = requests.get(url, headers=headers)
    # Enviar uma requisição HTTP para o Indeed
    response = requests.get(url)
    
    # Verificar se a requisição foi bem-sucedida
    if response.status_code != 200:
        print("Falha ao acessar o Indeed")
        return []

    # Criar objeto BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontrar todas as divs de vaga
    job_cards = soup.find_all('div', class_='jobsearch-SerpJobCard')
    
    # Lista para armazenar informações das vagas
    jobs = []
    
    # Extrair informações de cada vaga
    for job_card in job_cards:
        title = job_card.find('h2', class_='title').text.strip()
        company = job_card.find('span', class_='company').text.strip()
        location = job_card.find('div', class_='location').text.strip() if job_card.find('div', class_='location') else 'N/A'
        summary = job_card.find('div', class_='summary').text.strip()
        salary = job_card.find('span', class_='salaryText').text.strip() if job_card.find('span', class_='salaryText') else 'N/A'
        
        # Inferir a senioridade a partir do título da vaga
        seniority = 'N/A'
        if 'junior' in title.lower():
            seniority = 'Junior'
        elif 'senior' in title.lower():
            seniority = 'Senior'
        elif 'intern' in title.lower() or 'trainee' in title.lower():
            seniority = 'Intern/Trainee'
        elif 'lead' in title.lower() or 'manager' in title.lower():
            seniority = 'Lead/Manager'
        
        # Armazenar informações da vaga em um dicionário
        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'summary': summary,
            'salary': salary,
            'seniority': seniority
        })
    
    return jobs

# Exemplo de uso
job_title = "Dados"
location = "Brasil"
jobs = scrape_indeed_jobs(job_title, location)

for job in jobs:
    print(f"Title: {job['title']}")
    print(f"Company: {job['company']}")
    print(f"Location: {job['location']}")
    print(f"Summary: {job['summary']}")
    print(f"Salary: {job['salary']}")
    print(f"Seniority: {job['seniority']}")
    print("-" * 40)
