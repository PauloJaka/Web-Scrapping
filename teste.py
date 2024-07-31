import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_html(url):
    """
    Realiza a requisição HTTP e retorna o HTML da página.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_html(html):
    """
    Parseia o HTML usando BeautifulSoup e retorna as tabelas encontradas.
    """
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all('table', class_='container-uf')

def process_first_table(tabela):
    """
    Processa a primeira tabela, retornando um DataFrame.
    """
    header = tabela.find('thead')
    if header:
        colunas = [th.get_text(strip=True) for th in header.find_all('th')]
        linhas = [[td.get_text(strip=True) for td in tr.find_all('td')] for tr in tabela.find('tbody').find_all('tr')]
    else:
        linhas = [[td.get_text(strip=True) for td in tr.find_all('td')] for tr in tabela.find_all('tr')]
        colunas = [f'Coluna {i+1}' for i in range(len(linhas[0]))]
    
    df = pd.DataFrame(linhas, columns=colunas)
    return df

def process_other_tables(tabelas, uf_codigos):
    """
    Processa as outras tabelas, retornando uma lista de DataFrames.
    """
    dfs = []
    for idx, tabela in enumerate(tabelas, 1):
        header = tabela.find('thead')
        if header:
            linhas = [[td.get_text(strip=True) for td in tr.find_all('td')] for tr in tabela.find('tbody').find_all('tr')]
        else:
            linhas = [[td.get_text(strip=True) for td in tr.find_all('td')] for tr in tabela.find_all('tr')]
        
        uf = list(uf_codigos.keys())[idx-1]
        codigo_uf = uf_codigos[uf]
        
        linhas = [[linha[0], codigo_uf, linha[1]] for linha in linhas]
        df = pd.DataFrame(linhas, columns=['Município', 'Código UF', 'Código Município'])
        dfs.append(df)
    
    return dfs

def print_dfs(dfs, label):
    """
    Imprime os DataFrames na lista com um rótulo.
    """
    if dfs:
        df_final = pd.concat(dfs, ignore_index=True)
        print(f"{label} (total de {len(df_final)} linhas):")
        print(df_final)
    else:
        print(f"Nenhum dado encontrado para {label}.")

def main():
    url = "https://www.ibge.gov.br/explica/codigos-dos-municipios.php#AC"
    html = fetch_html(url)
    tabelas = parse_html(html)
    
    dfs_primeira_tabela = []
    dfs_outros = []

    if tabelas:
        df_principal = process_first_table(tabelas[0])
        dfs_primeira_tabela.append(df_principal)
        tabelas = tabelas[1:]

    uf_codigos = {
        "AC": 12, "AL": 27, "AP": 16, "AM": 13, "BA": 29, "CE": 23, "DF": 53,
        "ES": 32, "GO": 52, "MA": 21, "MT": 51, "MS": 50, "MG": 31, "PA": 15,
        "PB": 25, "PR": 41, "PE": 26, "PI": 22, "RJ": 33, "RN": 24, "RS": 43,
        "RO": 11, "RR": 14, "SC": 42, "SP": 35, "SE": 28, "TO": 17
    }

    dfs_outros = process_other_tables(tabelas, uf_codigos)

    print_dfs(dfs_primeira_tabela, 'Primeira Tabela')
    print_dfs(dfs_outros, 'Outras Tabelas')

if __name__ == "__main__":
    main()