from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import re

# Configuração manual dos campos fixos:
ESTADO = "GO"
CIDADE = "GOIANIA"
BAIRRO = "Alphaville Araguaia"  # Troque para o bairro do condomínio certo!
TIPO_PADRAO = ""  # Deixe em branco; será detectado para cada imóvel

# URL do Alphaville desejado
url = "https://www.vivareal.com.br/venda/goias/goiania/bairros/alphaville-araguaia/casa_residencial/?onde=%2CGoi%C3%A1s%2CGoi%C3%A2nia%2CBairros%2CAlphaville+Araguaia%2C%2C%2Cneighborhood%2CBR%3EGoias%3ENULL%3EGoiania%3EBarrios%3EAlphaville+Araguaia%2C-16.714311%2C-49.201187%2C%3B%2CGoi%C3%A1s%2CGoi%C3%A2nia%2CBairros%2CAlphaville+Flamboyant+Araguaia%2C%2C%2Cneighborhood%2CBR%3EGoias%3ENULL%3EGoiania%3EBarrios%3EAlphaville+Flamboyant+Araguaia%2C-16.714311%2C-49.201187%2C%3B%2CGoi%C3%A1s%2CGoi%C3%A2nia%2CBairros%2CAlphaville+Flamboyant+Residencial+Araguaia%2C%2C%2Cneighborhood%2CBR%3EGoias%3ENULL%3EGoiania%3EBarrios%3EAlphaville+Flamboyant+Residencial+Araguaia%2C-16.714311%2C-49.201187%2C&tipos=casa_residencial%2Ccondominio_residencial%2Csobrado_residencial&transacao=venda"

options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1200,800")
options.add_argument('--disable-gpu')
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)

def extrai_imoveis_pagina():
    imoveis = []
    cards = driver.find_elements(By.CSS_SELECTOR, 'div.flex.flex-col.grow.min-w-0.content-stretch.border-neutral-90')
    for card in cards:
        # tipo do imóvel (p.ex. Casa, Lote/Terreno, Sobrado)
        try:
            tipo_str = card.find_element(By.CSS_SELECTOR, 'span.block.font-secondary').text.strip()
            if "Casa" in tipo_str:
                tipo = "Casa"
            elif "Lote" in tipo_str or "Terreno" in tipo_str:
                tipo = "Lote/Terreno"
            elif "Sobrado" in tipo_str:
                tipo = "Sobrado"
            else:
                tipo = "Outro"
        except:
            tipo = ""

        # quartos
        try:
            quartos_str = card.find_element(By.CSS_SELECTOR, '[data-cy="rp-cardProperty-bedroomQuantity-txt"]').text
            quartos = int(re.sub(r'\D', '', quartos_str))
        except:
            quartos = ""

        # área (m²)
        try:
            area_str = card.find_element(By.CSS_SELECTOR, '[data-cy="rp-cardProperty-propertyArea-txt"]').text
            area = int(re.sub(r'\D', '', area_str))
        except:
            area = ""

        # preço
        try:
            preco_str = card.find_element(By.CSS_SELECTOR, '[data-cy="rp-cardProperty-price-txt"]').text
            preco_search = re.search(r'R\$\s?([\d\.]+)', preco_str)
            preco = int(preco_search.group(1).replace('.', '')) if preco_search else ""
        except:
            preco = ""

        imoveis.append({
            "estado": ESTADO,
            "cidade": CIDADE,
            "bairro": BAIRRO,
            "tipo": tipo,
            "quartos": quartos,
            "m2": area,
            "valor": preco,
        })
    return imoveis

todos_imoveis = []
driver.get(url)
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="rp-cardProperty-price-txt"]'))
    )
except:
    print("Nenhum imóvel encontrado ou página não carregou (timeout)!")
    driver.quit()
    exit()

pagina = 1
while True:
    print(f"Página {pagina}...", end="")
    imoveis = extrai_imoveis_pagina()
    if not imoveis:
        print("Nenhum imóvel encontrado, fim!")
        break
    todos_imoveis.extend(imoveis)
    print(f" {len(imoveis)} imóveis coletados.")

    # Tenta clicar no botão "Próxima página"
    try:
        botao_proxima = driver.find_element(By.CSS_SELECTOR, 'a[title="Próxima página"]')
        if "disabled" in botao_proxima.get_attribute("class"):
            print("Fim das páginas.")
            break
        botao_proxima.click()
        pagina += 1
        time.sleep(2)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="rp-cardProperty-price-txt"]'))
        )
    except Exception:
        print("Sem próxima página. Fim!")
        break

driver.quit()

# Salva CSV
csvfile = "viva_alp_araguaia.csv"
campos = ["estado", "cidade", "bairro", "tipo", "quartos", "m2", "valor"]
with open(csvfile, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=campos)
    writer.writeheader()
    for imovel in todos_imoveis:
        writer.writerow(imovel)

print(f"\nColeta finalizada! {len(todos_imoveis)} imóveis salvos em {csvfile}")
