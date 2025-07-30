import pandas as pd
import requests
import xml.etree.ElementTree as ET

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

def carregar_imoveis_portal(atualizar=False, arquivo_csv='meuportal_base.csv'):
    """
    Se atualizar=True, busca do XML online, gera e salva CSV atualizado.
    Se atualizar=False, lê do CSV local.
    Retorna DataFrame padronizado.
    """
    if atualizar:
        print("Baixando XML do portal...")
        url = "https://integracao.arboimoveis.com/api/custom-xml/imobiliaria/b13d33183002d16470691a3fa052c08fb527b62743ac71834be7788fc84736acpfFv4ptPWLl3kr2Lwj8NyDfZhNYSYyHaK3pjzK82y9c=/imovelweb-xml"
        response = requests.get(url)
        tree = ET.fromstring(response.content)
        imoveis = []
        imoveis_tag = tree.find("Imoveis")
        if imoveis_tag is not None:
            for imovel in imoveis_tag.findall("Imovel"):
                imoveis.append({
                    "estado": imovel.findtext("UF", default="GO"),
                    "cidade": imovel.findtext("Cidade"),
                    "bairro": imovel.findtext("Bairro"),
                    "tipo": imovel.findtext("TipoImovel"),
                    "m2": float(imovel.findtext("AreaUtil", default="0")),
                    "quartos": int(imovel.findtext("QtdDormitorios", default="0")),
                    "banheiros": int(imovel.findtext("QtdBanheiros", default="0")),
                    "garagem": int(imovel.findtext("QtdVagas", default="0")),
                    "mobilia": imovel.findtext("Mobiliado", default="Nao"),
                    "ano": 2020,
                    "valor": float(imovel.findtext("PrecoVenda", default="0"))
                })
        df = pd.DataFrame(imoveis)
        df = df[(df['m2'] > 0) & (df['valor'] > 0)]
        # Padroniza para MAIÚSCULO e tira espaços:
        if 'bairro' in df.columns:
            df['bairro'] = df['bairro'].astype(str).str.upper().str.strip()
        df.to_csv(arquivo_csv, index=False)
        print(f'Dados baixados e salvos em {arquivo_csv}!')
        return df
    else:
        try:
            df = pd.read_csv(arquivo_csv)
            # Padroniza para MAIÚSCULO e tira espaços:
            if 'bairro' in df.columns:
                df['bairro'] = df['bairro'].astype(str).str.upper().str.strip()
            print(f'Dados carregados do {arquivo_csv}!')
            return df
        except Exception as e:
            print(f"Erro ao carregar o arquivo {arquivo_csv}: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    carregar_imoveis_portal(atualizar=True)
