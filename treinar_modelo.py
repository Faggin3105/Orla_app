import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import os
import unidecode

BASE = "base_unificada.csv"

padroes_bairros = {
    "FAZENDA VAU DAS POMBAS": "PORTAL DO SOL GREEN",
    "GOIANIA GOLFE CLUBE": "PORTAL DO SOL GREEN",
    "GOIÂNIA GOL CLUB": "PORTAL DO SOL GREEN",
    "RESIDENCIAL GOIÂNIA GOLFE CLUBE": "PORTAL DO SOL GREEN",
    "ALTO DA GLORIA": "ALTO DA GLORIA",
    "JARDIM AMERICA": "JARDIM AMERICA",
    "JARDINS ITALIA": "JARDINS ITALIA",
    "JARDINS VALENCIA": "JARDINS VALENCIA",
    "LOTEAMENTO PORTAL DO SOL 2": "CONDOMINIO PORTAL DO SOL 2",
    "LOTEAMENTO PORTAL DO SOL II": "CONDOMINIO PORTAL DO SOL 2",
    "PORTAL DO SOL 2": "CONDOMINIO PORTAL DO SOL 2",
    "PORTAL DO SOL II": "CONDOMINIO PORTAL DO SOL 2",
    "SERRINHA": "SETOR SERRINHA",
    "TERRAS ALPHA RESIDENCIAL 1": "CONDOMINIO TERRAS ALPHA 1",
    "TERRAS ALPHA 1": "CONDOMINIO TERRAS ALPHA 1",
    "TERRAS ALPHA I": "CONDOMINIO TERRAS ALPHA 1",
    "TERRAS ALPHA RESIDENCIAL 2": "CONDOMINIO TERRAS ALPHA 2",
    "TERRAS ALPHA 2": "CONDOMINIO TERRAS ALPHA 2",
    "TERRAS ALPHA II": "CONDOMINIO TERRAS ALPHA 2",
    "GOLF CLUB": "PORTAL DO SOL GREEN",
    "ST.BUENO": "SETOR BUENO",
    "ST. BUENO": "SETOR BUENO",
    "FELIZ": "BAIRRO FELIZ",
    "CIDADE VERA CRUZ - JARDINS MONACO": "JARDINS MONACO",
    "CIDADE VERA CRUZ JARDINS MONACO": "JARDINS MONACO",
    "JARDINS MONACO": "JARDINS MONACO",
    "CONDOMINIO DO LAGO 1A ETAPA": "CONDOMINIO DO LAGO",
    "CONDOMINIO DO LAGO 1ª ETAPA": "CONDOMINIO DO LAGO",
    "GOIA": "BAIRRO GOIA",
    "GOIA 2": "BAIRRO GOIA 2",
    "ILDA": "BAIRRO ILDA",
    "JARDIM GOIAS": "JARDIM GOIAS",
    "JARDINS FRANCA": "JARDINS FRANCA",
    "ALPHAVILLE": "RESIDENCIAL ALPHAVILLE",
    "RESIDENCIAL ALPHAVILLE FLAMBOYANT": "RESIDENCIAL ALPHAVILLE",
    "RESIDENCIAL GOIANIA GOLFE CLUBE": "PORTAL DO SOL GREEN",
    "RESIDENCIAL JARDINS LYON": "JARDINS LYON",
    "RESIDENCIAL PARQVILLE JACARANDA": "PARQVILLE JACARANDA",
    "PARQVILLE PINHERIOS": "PARQVILLE PINHEIROS",
    "SETOR JAO": "SETOR JAO",
    "LOTEAMENTO PORTAL DO SOL I":  "CONDOMINIO PORTAL DO SOL 1",
    "RUA  C 238": "JARDIM AMERICA",

}

def normaliza_texto(txt):
    if pd.isna(txt): return ""
    return unidecode.unidecode(str(txt).upper().strip())

def padronizar_bairro(bairro):
    if pd.isnull(bairro):
        return ""
    bairro_norm = normaliza_texto(bairro)
    resultado = padroes_bairros.get(bairro_norm, bairro_norm)
    return normaliza_texto(resultado)

# Carrega base
df = pd.read_csv(BASE)
df.columns = [col.strip().lower() for col in df.columns]

# Normaliza e padroniza colunas principais
for col in ['tipo', 'bairro', 'cidade', 'estado']:
    if col in df.columns:
        df[col] = df[col].apply(normaliza_texto)
if 'bairro' in df.columns:
    df['bairro'] = df['bairro'].apply(padronizar_bairro)

# Veja TODOS os bairros finais padronizados usados para treino!
print("Bairros únicos padronizados:", sorted(df['bairro'].unique()))

tipos_principais = ["APARTAMENTO", "CASA", "TERRENO"]

for tipo in tipos_principais:
    df_tipo = df[df["tipo"] == tipo].copy()
    print(f"{tipo}: {len(df_tipo)} registros originais.")

    # Remove registros sem m2 ou valor
    df_tipo = df_tipo[df_tipo["m2"].notnull() & df_tipo["valor"].notnull()]
    df_tipo = df_tipo[df_tipo["m2"] > 0]
    df_tipo = df_tipo[df_tipo["valor"] > 1000]
    print(f"{tipo}: {len(df_tipo)} registros após limpeza.")

    if len(df_tipo) < 10:
        print(f"Pulando {tipo} pois não tem registros suficientes após limpeza.")
        continue

    if tipo == "TERRENO":
        features = ["estado", "cidade", "bairro", "tipo", "m2"]
    else:
        features = ["estado", "cidade", "bairro", "tipo", "quartos", "banheiros", "garagem", "ano", "m2"]

    for col in features:
        if col not in df_tipo.columns:
            df_tipo[col] = 0
        df_tipo[col] = df_tipo[col].fillna(0)

    X = df_tipo[features].copy()
    y = df_tipo["valor"]

    # LabelEncoder nas variáveis categóricas
    le_dict = {}
    for col in ["estado", "cidade", "bairro", "tipo"]:
        if col in X.columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            le_dict[col] = le

    # Veja TODOS os bairros que o LabelEncoder do modelo vai aceitar!
    print(f"Bairros usados no modelo {tipo.lower()}:", le_dict['bairro'].classes_)

    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X, y)

    tipo_nome = tipo.lower()
    if not os.path.exists("models"):
        os.makedirs("models")
    joblib.dump(modelo, f"models/modelo_{tipo_nome}.joblib")
    joblib.dump(le_dict, f"models/label_encoders_{tipo_nome}.joblib")
    joblib.dump(features, f"models/colunas_modelo_{tipo_nome}.joblib")
    print(f"Modelo para {tipo} treinado com {len(X)} registros.")
