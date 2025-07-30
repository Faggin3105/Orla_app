import pandas as pd
import re

# Dicionário de padronização de bairros
padroes_bairros = {
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
     "FELIZ": "BAIRRO FELIZ",
     "CIDADE VERA CRUZ - JARDINS MÔNACO": "JARDINS MÔNACO",
     "CIDADE VERA CRUZ JARDINS MÔNACO": "JARDINS MÔNACO",
     "JARDINS MONACO": "JARDINS MÔNACO",
     "CONDOMÍNIO DO LAGO 1ª ETAPA": "CONDOMÍNIO DO LAGO",
     "GOIA": "BAIRRO GOIÁ",
     "GOIA 2": "BAIRRO GOIÁ 2",
     "ILDA": "BAIRRO ILDA",
     "JARDIM GOIAS": "JARDIM GOIÁS",
     "JARDINS FRANCA": "JARDINS FRANÇA",
     "RESIDENCIAL GOIANIA GOLFE CLUBE": "PORTAL DO SOL GREEN",
     "RESIDENCIAL JARDINS LYON": "JARDINS LYON",
     "RESIDENCIAL PARQVILLE JACARANDA": "PARQVILLE JACARANDÁ",
     "PARQVILLE PINHERIOS": "PARQVILLE PINHEIROS",
     "SETOR JAO": "SETOR JAÓ",
    "ALPHAVILLE GOIÁS": "ALPHAVILLE GOIÁS",
    "ALPHAVILLE GOIAS": "ALPHAVILLE GOIÁS",
    "ALPHAVILLE CRUZEIRO": "ALPHAVILLE CRUZEIRO",
    "ALPHAVILLE IPÊS": "ALPHAVILLE IPÊS",
    "ALPHAVILLE IPES": "ALPHAVILLE IPÊS",
    "ALPHAVILLE ARAGUAIA": "ALPHAVILLE ARAGUAIA",
    "ALPHAVILLE GOIÁS": "ALPHAVILLE GOIÁS",
    "ALPHAVILLE GOIAS": "ALPHAVILLE GOIÁS",
    "ALPHAVILLE IPÊS": "ALPHAVILLE IPÊS",
    "ALPHAVILLE IPES": "ALPHAVILLE IPÊS",
    "ALPHAVILLE CRUZEIRO": "ALPHAVILLE CRUZEIRO",
    "ALPHAVILLE ARAGUAIA": "ALPHAVILLE ARAGUAIA",
    "RESIDENCIAL ALPHAVILLE GOIÁS": "ALPHAVILLE GOIÁS",
    "ALPHAVILLE FLAMBOYANT RESIDENCIAL ARAGUAIA": "ALPHAVILLE ARAGUAIA",
    "RESIDENCIAL ALPHAVILLE FLAMBOYANT": "ALPHAVILLE GOIÁS",
    "PLATEAU D`OR": "PLATEAU D`OR"

}
colunas = ['estado','cidade','bairro','tipo','quartos','m2','valor']

def padronizar_bairro(bairro):
    if pd.isnull(bairro):
        return ""
    bairro = bairro.upper().strip()
    return padroes_bairros.get(bairro, bairro)

def padroniza_cidade(cidade):
    c = str(cidade).upper()
    if "GOIÂNIA" in c or "GOIANIA" in c:
        return "GOIANIA"
    elif "SENADOR CANEDO" in c:
        return "SENADOR CANEDO"
    elif "APARECIDA" in c:
        return "APARECIDA DE GOIANIA"
    else:
        return c

def padroniza_tipo(tipo):
    t = str(tipo).upper()
    if "TERRENO" in t: return "TERRENO"
    if "APART" in t: return "APARTAMENTO"
    if "CASA" in t: return "CASA"
    if "RURAL" in t: return "RURAL"
    if "COMERCIAL" in t: return "COMERCIAL"
    if "FLAT" in t: return "APARTAMENTO"
    if "STUDIO" in t or "KITNET" in t: return "APARTAMENTO"
    return t

# ------------ MEUPORTAL
df1 = pd.read_csv('meuportal_base.csv')
df1.columns = [c.strip().lower() for c in df1.columns]
df1['cidade'] = df1['cidade'].apply(padroniza_cidade)
df1['bairro'] = df1['bairro'].apply(padronizar_bairro)
df1['tipo'] = df1['tipo'].apply(padroniza_tipo)
for col in ['quartos','m2','valor']:
    df1[col] = pd.to_numeric(df1[col], errors='coerce').fillna(0).astype(int)
df1 = df1[colunas]

# ------------ 62IMOVEIS
df2 = pd.read_csv('62imoveis_goiania.csv')
df2.columns = [c.strip().lower() for c in df2.columns]
def extrair_cidade_titulo(titulo):
    if pd.isna(titulo):
        return ""
    partes = [p.strip().upper() for p in str(titulo).split(',')]
    if len(partes) >= 1:
        return partes[-1]
    return ""
def extrair_bairro_titulo(titulo):
    if pd.isna(titulo):
        return ""
    partes = [p.strip().upper() for p in str(titulo).split(',')]
    if len(partes) >= 2:
        return partes[-2]
    return ""
def extrair_tipo_descricao(desc):
    if pd.isna(desc):
        return ""
    desc = desc.upper()
    if "TERRENO" in desc: return "TERRENO"
    if "APART" in desc: return "APARTAMENTO"
    if "CASA" in desc: return "CASA"
    if "RURAL" in desc: return "RURAL"
    if "COMERCIAL" in desc: return "COMERCIAL"
    return "INDEFINIDO"
df2['cidade'] = df2['titulo'].apply(extrair_cidade_titulo).apply(padroniza_cidade)
df2['bairro'] = df2['titulo'].apply(extrair_bairro_titulo).apply(padronizar_bairro)
df2['tipo'] = df2['descricao'].apply(extrair_tipo_descricao).apply(padroniza_tipo)
df2['estado'] = "GO"
for col in ['quartos','m2','valor']:
    df2[col] = pd.to_numeric(df2[col], errors='coerce').fillna(0).astype(int)
df2 = df2[colunas]

# ------------ CHAVES
df3 = pd.read_csv('base_chaves.csv')
df3.columns = [c.strip().lower() for c in df3.columns]
df3['cidade'] = df3['cidade'].apply(padroniza_cidade)
df3['bairro'] = df3['bairro'].apply(padronizar_bairro)
df3['tipo'] = df3['tipo'].apply(padroniza_tipo)
df3['estado'] = df3['estado'].apply(lambda x: str(x).upper() if pd.notnull(x) else "GO")

def limpar_m2(val):
    if pd.isnull(val):
        return 0
    # Aceita formatos tipo "65²", "65m²", "65 m2", etc.
    numeros = re.findall(r'\d+', str(val))
    return int(numeros[0]) if numeros else 0

df3['m2'] = df3['m2'].apply(limpar_m2)
for col in ['quartos','m2','valor']:
    df3[col] = pd.to_numeric(df3[col], errors='coerce').fillna(0).astype(int)
df3 = df3[colunas]

# ------------ ALPHAVILLE (novos CSVs)
csv_alphaville = [
    "viva_alp_cruzeiro.csv",
    "viva_alp_goias.csv",
    "viva_alp_ipes.csv",
    "viva_alp_araguaia.csv"
]
dfs_alphaville = []
for fname in csv_alphaville:
    df = pd.read_csv(fname)
    df.columns = [c.strip().lower() for c in df.columns]
    df['cidade'] = df['cidade'].apply(padroniza_cidade)
    df['bairro'] = df['bairro'].apply(padronizar_bairro)
    df['tipo'] = df['tipo'].apply(padroniza_tipo)
    for col in ['quartos', 'm2', 'valor']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    df = df[colunas]
    dfs_alphaville.append(df)
df_alphaville = pd.concat(dfs_alphaville, ignore_index=True)

# ------------ VIVA PLATEAU
df_viva_plateau = pd.read_csv('viva_plateau.csv')
df_viva_plateau.columns = [c.strip().lower() for c in df_viva_plateau.columns]
df_viva_plateau['cidade'] = df_viva_plateau['cidade'].apply(padroniza_cidade)
df_viva_plateau['bairro'] = df_viva_plateau['bairro'].apply(padronizar_bairro)
df_viva_plateau['tipo'] = df_viva_plateau['tipo'].apply(padroniza_tipo)
for col in ['quartos', 'm2', 'valor']:
    df_viva_plateau[col] = pd.to_numeric(df_viva_plateau[col], errors='coerce').fillna(0).astype(int)
df_viva_plateau = df_viva_plateau[colunas]

# ------------ UNIFICAR
cidades_interesse = ["GOIANIA", "SENADOR CANEDO", "APARECIDA DE GOIANIA"]
df_unificado = pd.concat([df1, df2, df3, df_alphaville, df_viva_plateau], ignore_index=True)
df_unificado = df_unificado[df_unificado['cidade'].isin(cidades_interesse)].reset_index(drop=True)
df_unificado.to_csv('base_unificada.csv', index=False, encoding="utf-8-sig")
print(f"Base unificada salva com {len(df_unificado)} registros.")

