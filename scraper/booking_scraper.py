import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options

def iniciar_driver():
    """Configura e inicia o navegador Microsoft Edge"""
    edge_options = Options()
    edge_options.add_argument("--disable-blink-features=AutomationControlled")
    
    servico = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=servico, options=edge_options)
    driver.maximize_window()
    return driver

def extrair_dados_booking():
    cidades = ["Porto de Galinhas", "Maragogi", "Pipa", "Joao Pessoa", "Natal"]
    dados_imoveis = []
    
    driver = iniciar_driver()
    
    for cidade in cidades:
        print(f"\n--- Iniciando coleta em: {cidade} ---")
        cidade_url = cidade.replace(" ", "+")
        
        # Paginação: range(0, 125, 25) vai rodar os offsets 0, 25, 50, 75 e 100
        # Isso dá 5 páginas por cidade = ~125 imóveis/cidade = ~625 no total
        # Injetando datas (ex: 15 a 20 de outubro) para forçar a exibição do preço
        for offset in range(0, 125, 25):
            print(f"Carregando página com offset {offset}...")
            
            # URL atualizada com parâmetros checkin e checkout
            url = f"https://www.booking.com/searchresults.pt-br.html?ss={cidade_url}&checkin=2026-10-15&checkout=2026-10-20&offset={offset}"
            driver.get(url)
            
            time.sleep(random.uniform(5.0, 8.0))
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            cards = soup.find_all('div', attrs={"data-testid": "property-card"})
            
            if not cards:
                print("Nenhum imóvel encontrado nesta página. Indo para a próxima cidade...")
                break
            
            for card in cards:
                imovel = {'cidade': cidade}
                
                titulo = card.find('div', attrs={"data-testid": "title"})
                imovel['titulo'] = titulo.text.strip() if titulo else None
                
                preco = card.find('span', attrs={"data-testid": "price-and-discounted-price"})
                if not preco:
                    preco = card.find('div', attrs={"data-testid": "price-and-discounted-price"})
                imovel['preco'] = preco.text.strip() if preco else None
                
                nota = card.find('div', attrs={"data-testid": "review-score"})
                imovel['nota'] = nota.text.strip().split()[0] if nota else None
                
                # Fallback de distância já corrigido
                distancia = card.find(attrs={"data-testid": "distance"})
                if not distancia:
                    elementos_texto = card.find_all(['span', 'div', 'p'])
                    for elemento in elementos_texto:
                        texto_elemento = elemento.text.lower()
                        if 'centro' in texto_elemento or 'praia' in texto_elemento or 'beira-mar' in texto_elemento:
                            distancia = elemento
                            break
                imovel['distancia'] = distancia.text.strip() if distancia else None
                
                config = card.find('div', attrs={"data-testid": "recommended-units"})
                imovel['configuracao'] = config.text.strip() if config else None

                # NOVAS VARIÁVEIS: Mineração de texto para Comodidades e Tipo
                texto_completo = card.text.lower()
                
                imovel['tem_piscina'] = 1 if 'piscina' in texto_completo else 0
                imovel['tem_ar_condicionado'] = 1 if 'ar-condicionado' in texto_completo or 'ar condicionado' in texto_completo else 0
                imovel['tem_wifi'] = 1 if 'wi-fi' in texto_completo or 'wifi' in texto_completo or 'internet' in texto_completo else 0
                
                if 'resort' in texto_completo:
                    imovel['tipo_imovel'] = 'Resort'
                elif 'pousada' in texto_completo:
                    imovel['tipo_imovel'] = 'Pousada'
                elif 'apartamento' in texto_completo or 'flat' in texto_completo or 'studio' in texto_completo:
                    imovel['tipo_imovel'] = 'Flat'
                else:
                    imovel['tipo_imovel'] = 'Outro'

                dados_imoveis.append(imovel)
                
    driver.quit()
    
    df = pd.DataFrame(dados_imoveis)
    caminho_arquivo = '../data/raw/flats_nordeste_bruto.csv'
    df.to_csv(caminho_arquivo, index=False, encoding='utf-8')
    print(f"\nExtração concluída com sucesso! {len(df)} registros salvos em {caminho_arquivo}")

if __name__ == "__main__":
    extrair_dados_booking()