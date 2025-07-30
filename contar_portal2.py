import pandas as pd
import unidecode

# Funções de padronização (use as mesmas do modelo!)
padroes_bairros = {
    "FAZENDA VAU DAS POMBAS": "PORTAL DO SOL GREEN",
    "GOIANIA GOLFE CLUBE": "PORTAL DO SOL GREEN",
    "GOIÂNIA GOL CLUB": "PORTAL DO SOL GREEN",
    "GOIANIA GOL CLUB": "PORTAL DO SOL GREEN",
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
    "FELIZ": "BAIRRO FELIZ",
    "CIDADE VERA CRUZ - JARDINS MÔNACO": "JARDINS MÔNACO",
    "CIDADE VERA CRUZ JARDINS MÔNACO": "JARDINS MÔNACO",
    "JARDINS MONACO": "JARDINS MÔNACO",
    "CONDOMÍNIO DO LAGO 1ª ETAPA": "CONDOMÍNIO DO LAGO",
    "CONDOMÍNIO DO LAGO 1A ETAPA": "CONDOMÍNIO DO LAGO",
    "GOIA": "BAIRRO GOIÁ",
    "GOIA 2": "BAIRRO GOIÁ 2",
    "ILDA": "BAIRRO ILDA",
    "JARDIM GOIAS": "JARDIM GOIÁS",
    "JARDINS FRANCA": "JARDINS FRANÇA",
    "ALPHAVILLE": "RESIDENCIAL ALPHAVILLE",
    "RESIDENCIAL ALPHAVILLE FLAMBOYANT": "RESIDENCIAL ALPHAVILLE",
    "RESIDENCIAL GOIANIA GOLFE CLUBE": "PORTAL DO SOL GREEN",
    "RESIDENCIAL JARDINS LYON": "JARDINS LYON",
    "RESIDENCIAL PARQVILLE JACARANDA": "PARQVILLE JACARANDÁ",
    "PARQVILLE PINHERIOS": "PARQVILLE PINHEIROS",
    "SETOR JAO": "SETOR JAÓ",
    "LOTEAMENTO PORTAL DO SOL I":  "CONDOMÍNIO PORTAL DO SOL 1",
}

def padronizar_bairro(bairro):
    if pd.isnull(bairro):
        return ""
    bairro = unidecode.unidecode(str(bairro).upper().strip())
    return padroes_bairros.get(bairro, bairro)

# Carregue a base de dados
df = pd.read_csv("base_unificada.csv")
df.columns = [col.strip().lower() for col in df.columns]

# Padronize os bairros
df['bairro_padronizado'] = df['bairro'].apply(lambda b: padronizar_bairro(unidecode.unidecode(str(b).upper().strip())))

# Filtre e conte
alvo = "JARDINS MÔNACO"
num = (df['bairro_padronizado'] == alvo).sum()

print(f"Número de imóveis no bairro '{alvo}': {num}")

# Após o print do total, adicione isto:
tipos_disponiveis = df[df['bairro_padronizado'] == alvo]['tipo'].str.upper().unique()
print(f"Tipos disponíveis nesse bairro: {tipos_disponiveis}")

num_casas = ((df['bairro_padronizado'] == alvo) & (df['tipo'].str.upper() == 'CASA')).sum()
print(f"Número de imóveis do tipo CASA no bairro '{alvo}': {num_casas}")

# Se quiser ver todos os tipos e quantos de cada:
tipos_counts = df[df['bairro_padronizado'] == alvo]['tipo'].str.upper().value_counts()
print("\nQuantidade por tipo nesse bairro:")
print(tipos_counts)

