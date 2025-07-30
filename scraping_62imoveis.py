import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Cole aqui logo em seguida:
PADRONIZA_BAIRROS = {
    "FAZENDA VAU DAS POMBAS": "PORTAL DO SOL GREEN",
    "GOIANIA GOLFE CLUBE": "PORTAL DO SOL GREEN",
    "GOIÂNIA GOL CLUB": "PORTAL DO SOL GREEN",
    "RESIDENCIAL GOIÂNIA GOLFE CLUBE": "PORTAL DO SOL GREEN",
    "ALTO DA GLORIA": "ALTO DA GLÓRIA",
    "JARDIM AMERICA": "JARDIM AMÉRICA",
    "JARDINS ITALIA": "JARDINS ITÁLIA",
    "JARDINS VALENCIA": "JARDINS VALÊNCIA",
    "LOTEAMENTO PORTAL DO SOL 2": "CONDOMÍNIO PORTAL DO SOL 2",
    "LOTEAMENTO PORTAL DO SOL II": "CONDOMÍNIO PORTAL DO SOL 2",
    "PORTAL DO SOL 2": "CONDOMÍNIO PORTAL DO SOL 2",
    "PORTAL DO SOL II": "CONDOMÍNIO PORTAL DO SOL 2",
    "SERRINHA": "SETOR SERRINHA",
    "TERRAS ALPHA RESIDENCIAL 1": "CONDOMÍNIO TERRAS ALPHA 1",
    "TERRAS ALPHA 1": "CONDOMÍNIO TERRAS ALPHA 1",
    "TERRAS ALPHA I": "CONDOMÍNIO TERRAS ALPHA 1",
     "TERRAS ALPHA RESIDENCIAL 2": "CONDOMÍNIO TERRAS ALPHA 2",
    "TERRAS ALPHA 2": "CONDOMÍNIO TERRAS ALPHA 2",
    "TERRAS ALPHA II": "CONDOMÍNIO TERRAS ALPHA 2",
    "GOLF CLUB": "PORTAL DO SOL GREEN",
    "ST.BUENO": "SETOR BUENO",
    "ST. BUENO": "SETOR BUENO",
    # ...adicione outros se quiser...
}

def padronizar_bairro(bairro):
    b = str(bairro).strip().upper()
    return PADRONIZA_BAIRROS.get(b, b)

anuncios = []
for pagina in range(1, 70):
    url = f"https://www.62imoveis.com.br/venda/go/todos/imoveis?pagina={pagina}"
    print(f"Coletando página {pagina}...")
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    items = soup.find_all("a", class_="new-card")
    print(f"Encontrou {len(items)} blocos nesta página")

    if not items:
        break

    for item in items:
        # Pega só imóveis comuns ("/imovel/apartamento" ou "/imovel/casa" no href, etc)
        href = item.get("href", "")
        if not href.startswith("/imovel/"):
            continue
        try:
            link = "https://www.62imoveis.com.br" + href

            # Título
            titulo = item.find("h2", class_="new-title phrase")
            titulo = titulo.text.strip() if titulo else ""

            # Bairro e cidade (normalmente vem junto do título)
            bairro = ""
            if "SETOR" in titulo.upper():
                bairro = titulo.split(",")[1].strip() if "," in titulo else titulo.strip()

            # Descrição resumida (normalmente m²)
            descricao = item.find("h3", class_="new-desc phrase")
            descricao = descricao.text.strip() if descricao else ""

            # Preço
            preco_span = item.find("span")
            preco = preco_span.text.strip() if preco_span else ""

            # m², quartos, banheiros, garagem
            m2 = quartos = banheiros = garagem = ""
            detalhes_ul = item.find("ul", class_="new-details-ul")
            if detalhes_ul:
                for li in detalhes_ul.find_all("li"):
                    txt = li.text.lower()
                    if "m²" in txt or "m2" in txt:
                        m2 = re.sub(r"[^\d]", "", txt)
                    elif "quarto" in txt:
                        quartos = re.sub(r"[^\d]", "", txt)
                    elif "banheiro" in txt:
                        banheiros = re.sub(r"[^\d]", "", txt)
                    elif "garagem" in txt:
                        garagem = re.sub(r"[^\d]", "", txt)

            anuncios.append({
                "titulo": titulo,
                "bairro": bairro,
                "descricao": descricao,
                "m2": int(m2) if m2.isdigit() else None,
                "quartos": int(quartos) if quartos.isdigit() else None,
                "banheiros": int(banheiros) if banheiros.isdigit() else None,
                "garagem": int(garagem) if garagem.isdigit() else None,
                "valor": float(re.sub(r"[^\d]", "", preco)) if preco else None,
                "link": link
            })
        except Exception as erro:
            print("Erro ao coletar anúncio:", erro)

df_62 = pd.DataFrame(anuncios)
print(df_62.head())
df_62.to_csv("62imoveis_goiania.csv", index=False)
print("Arquivo 62imoveis_goiania.csv salvo com sucesso!")