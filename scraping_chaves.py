import requests
from bs4 import BeautifulSoup
import csv
import time

CIDADES = [
    ("goiania", "go"),
    ("senador-canedo", "go")
]

BASE_URL = "https://www.chavesnamao.com.br/imoveis-residenciais-a-venda/go-{cidade}/?pg={pagina}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

CAMPOS = [
    "cidade", "estado", "bairro", "tipo", "m2", "quartos", "banheiros", "garagem", "valor", "endereco", "link"
]

def extrai_info_anuncio(card):
    try:
        # Link do imóvel
        a_tag = card.find("a", href=True)
        link = ""
        if a_tag and a_tag["href"]:
            if a_tag["href"].startswith("http"):
                link = a_tag["href"]
            else:
                link = "https://www.chavesnamao.com.br" + a_tag["href"]

        # Título (debug)
        titulo = a_tag.get("title", "") if a_tag else ""
        # print(f"Card: {titulo} | {link}")

        # Endereço completo e bairro (novo)
        endereco = ""
        bairro = ""
        address_tag = card.find("address", class_=lambda c: c and "address" in c)
        if address_tag:
            ps = address_tag.find_all("p")
            if len(ps) > 0:
                endereco = ps[0].get_text(strip=True)
            if len(ps) > 1:
                bairro = ps[1].get_text(strip=True).split(",")[0]  # Só o bairro

        # Tipo: no título, primeira palavra
        tipo = ""
        if titulo:
            tipo = titulo.split()[0].strip().upper()
        else:
            tipo = ""

        # Área, quartos, banheiros, garagem
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

        # Valor
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

def scrape_cidade(cidade, estado, max_paginas=10, delay=1):
    imoveis = []
    for pagina in range(1, max_paginas+1):
        url = BASE_URL.format(cidade=cidade, pagina=pagina)
        print(f"Scraping {url}")
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            print(f"Falha ao acessar página {pagina}, status {resp.status_code}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
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

        if len(cards) < 20:
            break
        time.sleep(delay)
    return imoveis

def main():
    with open("base_chaves.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CAMPOS)
        total = 0
        for cidade, estado in CIDADES:
            imoveis = scrape_cidade(cidade, estado)
            for item in imoveis:
                writer.writerow(item)
            print(f"Cidade {cidade} adicionada: {len(imoveis)} imóveis.")
            total += len(imoveis)
        print(f"Total geral extraído: {total} imóveis.")

if __name__ == "__main__":
    main()
