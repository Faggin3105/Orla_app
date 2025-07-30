import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

CIDADES = [
    ("goiania", "go"),
    ("senador-canedo", "go")
]

CAMPOS = [
    "cidade", "estado", "bairro", "tipo", "m2", "quartos", "banheiros", "garagem", "valor", "endereco", "link"
]

def extrai_info_anuncio(card):
    try:
        a_tag = card.find("a", href=True)
        link = ""
        if a_tag and a_tag["href"]:
            link = "https://www.chavesnamao.com.br" + a_tag["href"] if not a_tag["href"].startswith("http") else a_tag["href"]
        titulo = a_tag.get("title", "") if a_tag else ""

        endereco = ""
        bairro = ""
        address_tag = card.find("address", class_=lambda c: c and "address" in c)
        if address_tag:
            ps = address_tag.find_all("p")
            if len(ps) > 0:
                endereco = ps[0].get_text(strip=True)
            if len(ps) > 1:
                bairro = ps[1].get_text(strip=True).split(",")[0]

        tipo = ""
        if titulo:
            tipo = titulo.split()[0].strip().upper()

        m2 = quartos = banheiros = garagem = ""
        p_tags = card.find_all("p")
        for p in p_tags:
            txt = p.get_text(strip=True).lower()
            if ("m²" in txt or "m2" in txt) and not m2:
                m2 = "".join(filter(str.isdigit, txt))
            elif "quarto" in txt and not quartos:
                quartos = "".join(filter(str.isdigit, txt))
            elif "banheiro" in txt and not banheiros:
                banheiros = "".join(filter(str.isdigit, txt))
            elif ("vaga" in txt or "garagem" in txt) and not garagem:
                garagem = "".join(filter(str.isdigit, txt))

        valor = ""
        valor_tag = card.find("p", class_=lambda c: c and "price" in c)
        if valor_tag:
            valor_texto = valor_tag.get_text(strip=True).replace("R$", "").replace(".", "").replace(",", ".")
            try:
                valor = float(valor_texto)
            except Exception:
                valor = valor_texto

        return {
            "bairro": bairro,
            "tipo": tipo,
            "m2": m2,
            "quartos": quartos,
            "banheiros": banheiros,
            "garagem": garagem,
            "valor": valor,
            "endereco": endereco,
            "link": link
        }
    except Exception as e:
        print("Erro ao extrair card:", e)
        return None

def scrape_cidade_selenium(driver, cidade, estado, max_paginas=100, delay=2):
    imoveis = []
    for pagina in range(1, max_paginas+1):
        url = f"https://www.chavesnamao.com.br/imoveis-residenciais/go-{cidade}/?pagina={pagina}&pg={pagina}"
        print(f"Scraping {url}")
        driver.get(url)
        time.sleep(delay)  # Espera o JS carregar

        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = soup.find_all("div", attrs={"data-template": "list"})
        if not cards:
            print("Nenhum imóvel encontrado, fim da paginação.")
            break

        for card in cards:
            dados = extrai_info_anuncio(card)
            if dados:
                dados["cidade"] = cidade.replace("-", " ").title()
                dados["estado"] = estado.upper()
                imoveis.append([dados.get(campo, "") for campo in CAMPOS])

        if len(cards) < 10:
            break
    return imoveis

def main():
    options = Options()
    options.add_argument("--headless")  # Remove esta linha para ver o navegador
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    with open("base_chaves.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CAMPOS)
        total = 0
        for cidade, estado in CIDADES:
            imoveis = scrape_cidade_selenium(driver, cidade, estado, max_paginas=100)
            for item in imoveis:
                writer.writerow(item)
            print(f"Cidade {cidade} adicionada: {len(imoveis)} imóveis.")
            total += len(imoveis)
        print(f"Total geral extraído: {total} imóveis.")
    driver.quit()

if __name__ == "__main__":
    main()
