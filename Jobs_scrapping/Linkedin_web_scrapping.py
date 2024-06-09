from bs4 import BeautifulSoup
import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

# get the user agent of you .env arquive
# to get the user agent just put "my user agent" on your browser.
user_agent = os.getenv('USER_AGENT')

def scrapper(page, title, location):
    headers = {'User-Agent': user_agent}
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&start={page}"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    return soup

def main_scraper(soup):
    jobs = soup.find_all('div', class_='base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card')
    for item in jobs:
        title = item.find('a').text.strip()
        company = item.find('h4').text.strip()
        link = item.a['href']
        location = item.find('span', class_='job-search-card__location').text.strip()
        job_posted = item.find('time', class_='job-search-card__listdate')
        if job_posted is not None:
            time = job_posted.text.strip()
            job = {
                'Title': title,
                'Link': link,
                'Company': company,
                'Location': location,
                'Job_posted': time
            }
            joblist.append(job)
    return


def scrape_jobs(title, location):
    global joblist
    joblist = []
    page = 0

    # Feel free to change the number of job list you want to scrape
    for i in range(0, 20, 20):
        print(f'Getting Page, {i}')
        soup = scrapper(page, title, location)
        main_scraper(soup)

    df = pd.DataFrame(joblist)
    return df

# Scrape jobs for different titles
df_dados = scrape_jobs('Dados', 'Brasil')
print(df_dados)

df_engenheiro = scrape_jobs('Python', 'Brasil')
print(df_engenheiro)