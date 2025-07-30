import pandas as pd
from meuportal import carregar_imoveis_portal

import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib

# ----- PADRONIZAÇÃO DE BAIRROS -----
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

def padronizar_mobilia(valor):
    v = str(valor).strip().lower()
    if v in ['sim', '1', 'true', 'mobilia', 'mobiliado']:
        return 'Sim'
    elif v in ['nao', 'não', '0', 'false', 'n', 'indefinido', 'nan', '']:
        return 'Nao'
    else:
        return 'Nao'

# Passo 1: Carrega as bases
print("Carregando base do portal próprio...")
df_portal = carregar_imoveis_portal(atualizar=False)

print("Carregando base do 62imoveis...")
df_62 = pd.read_csv('62imoveis_goiania.csv')
df_62 = pd.read_csv("62imoveis_goiania.csv")

# Adiciona a coluna 'tipo' baseado no título
def extrair_tipo(titulo):
    t = str(titulo).lower()
    if "terreno" in t:
        return "Terreno"
    elif "apartamento" in t:
        return "Apartamento"
    elif "casa" in t:
        return "Casa"
    elif "rural" in t:
        return "Rural"
    elif "comercial" in t:
        return "Comercial"
    else:
        return "Indefinido"

df_62["tipo"] = df_62["titulo"].apply(extrair_tipo)

df_portal['bairro'] = df_portal['bairro'].apply(padronizar_bairro)
df_62['bairro'] = df_62['bairro'].apply(padronizar_bairro)

# Passo 2: Lista das colunas essenciais do seu modelo
colunas_essenciais = [
    'estado', 'cidade', 'bairro', 'tipo', 'm2',
    'quartos', 'banheiros', 'garagem', 'mobilia', 'ano', 'valor'
]
# Passo 3: Garante que todas as colunas existam nas duas bases
for col in colunas_essenciais:
    if col not in df_portal.columns:
        df_portal[col] = "Indefinido"
    if col not in df_62.columns:
        df_62[col] = "Indefinido"

# Passo 4: Ajusta os tipos das colunas numéricas
for col in ['m2', 'valor', 'quartos', 'banheiros', 'garagem', 'ano']:
    df_portal[col] = pd.to_numeric(df_portal[col], errors='coerce')
    df_62[col] = pd.to_numeric(df_62[col], errors='coerce')

df_portal['bairro'] = df_portal['bairro'].astype(str).str.upper().str.strip()
df_62['bairro'] = df_62['bairro'].astype(str).str.upper().str.strip()

df_portal['mobilia'] = df_portal['mobilia'].apply(padronizar_mobilia)
df_62['mobilia'] = df_62['mobilia'].apply(padronizar_mobilia)

# Passo 7: Junta as duas bases
df_treino = pd.concat([
    df_portal[colunas_essenciais],
    df_62[colunas_essenciais]
], ignore_index=True)

# Filtra fora todos os imóveis cujo tipo é 'Indefinido'
df_treino = df_treino[df_treino['tipo'].str.upper().str.strip() != "INDEFINIDO"]

print(f"\nBase de treino pronta! Total de imóveis: {len(df_treino)}")
print(df_treino.head())
print("Colunas finais:", df_treino.columns.tolist())

# === Treina um modelo para cada tipo de imóvel ===

os.makedirs('models', exist_ok=True)

tipos = df_treino['tipo'].dropna().unique()
for tipo in tipos:
    df_tipo = df_treino[df_treino['tipo'] == tipo].copy()
    print(f"Treinando modelo para tipo: {tipo} - total de imóveis: {len(df_tipo)}")
    if len(df_tipo) < 15:
        print(f"Tipo '{tipo}' tem poucos dados. Pulando...")
        continue

    X = df_tipo.drop(columns=['valor'])
    y = df_tipo['valor']

    # Encode colunas categóricas
    colunas_categoricas = ['estado', 'cidade', 'bairro', 'tipo', 'mobilia']
    le_dict = {}
    for col in colunas_categoricas:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        le_dict[col] = le

    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X, y)
    # Salva um modelo e encoders para cada tipo
    tipo_nome = tipo.lower().replace(" ", "_")
    joblib.dump(modelo, f'models/modelo_{tipo_nome}.joblib')
    joblib.dump(le_dict, f'models/label_encoders_{tipo_nome}.joblib')
    joblib.dump(list(X.columns), f'models/colunas_modelo_{tipo_nome}.joblib')
    print(f"Modelo para '{tipo}' salvo como 'models/modelo_{tipo_nome}.joblib'")

# Exibe a média do valor por bairro para consulta
medias = df_treino.groupby('bairro')['valor'].mean().sort_values()
print("\nMédia de valor por bairro na base de treino:")
print(medias)
