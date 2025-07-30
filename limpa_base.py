import pandas as pd

# 1. Carrega base
df = pd.read_csv('base_unificada.csv')
df.columns = [c.strip().lower() for c in df.columns]

# 2. Remove imóveis SEM valor (>0)
df = df[df['valor'].notnull() & (df['valor'] > 0)]

# 3. Padronização do campo 'tipo'
def padroniza_tipo(tipo):
    if pd.isnull(tipo):
        return ""
    t = str(tipo).upper().strip()
    # 2. SOBRADO => CASA
    if t == "SOBRADO":
        return "CASA"
    # 3. LOTE => TERRENO
    if t == "LOTE":
        return "TERRENO"
    # 5. COBERTURA, EDIFÍCIO => APARTAMENTO
    if t in ["COBERTURA", "EDIFICIO", "EDIFÍCIO", "FLAT"]:
        return "APARTAMENTO"
    # 7. JARDINS => CASA
    if t == "JARDINS":
        return "CASA"
    # Default
    return t

df['tipo'] = df['tipo'].apply(padroniza_tipo)

# 4. Remove os tipos AGIO, ÁGIO
df = df[~df['tipo'].isin(['AGIO', 'ÁGIO'])]

# 6. FLAT já foi tratado no padroniza_tipo acima

# Salva resultado final sobrescrevendo o original
df.to_csv('base_unificada.csv', index=False, encoding='utf-8-sig')

print(f"Base salva com {len(df)} imóveis (limpa e padronizada).")
