import pandas as pd
import joblib
import unidecode
from flask import Flask, render_template, request, jsonify
from astral.sun import sun
from astral import LocationInfo
import datetime
import pytz
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Dicionário padronizador dos bairros
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
    "LOTEAMENTO PORTAL DO SOL I": "CONDOMINIO PORTAL DO SOL 1",
    "RUA  C 238": "JARDIM AMERICA",
}

def get_bcb_last(codigo_serie, meses=12):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados/ultimos/{meses}?formato=json"
    resp = requests.get(url)
    resp.raise_for_status()
    dados = resp.json()
    historico = [float(x["valor"].replace(',', '.')) for x in dados]
    datas = [x["data"] for x in dados]
    ult_valor = historico[-1] if historico else None
    return {
        "valor_atual": ult_valor,
        "historico": historico,
        "datas": datas
    }

def normaliza_texto(txt):
    if pd.isna(txt): return ""
    return unidecode.unidecode(str(txt).upper().strip())

def padronizar_bairro(bairro):
    if pd.isnull(bairro):
        return ""
    bairro = normaliza_texto(bairro)
    return padroes_bairros.get(bairro, bairro)

# Carregar a base
df = pd.read_csv("base_unificada.csv")
df.columns = [col.strip().lower() for col in df.columns]
for col in ['quartos', 'banheiros', 'garagem', 'ano', 'm2', 'valor', 'mobilia']:
    if col not in df.columns:
        df[col] = 0
df['bairro'] = df['bairro'].apply(lambda b: padronizar_bairro(normaliza_texto(b)))

estados_cidades_bairros = {}
for _, row in df.iterrows():
    estado = normaliza_texto(row.get('estado', ''))
    cidade = normaliza_texto(row.get('cidade', ''))
    bairro = row.get('bairro', '')
    if not estado or not cidade or not bairro:
        continue
    estados_cidades_bairros.setdefault(estado, {}).setdefault(cidade, set()).add(bairro)
for estado in estados_cidades_bairros:
    for cidade in estados_cidades_bairros[estado]:
        estados_cidades_bairros[estado][cidade] = sorted(list(estados_cidades_bairros[estado][cidade]))

def buscar_referencias(df, bairro, tipo, m2, quartos, banheiros, garagem, ano, n=10):
    similares = df[
        (df['bairro'] == bairro) &
        (df['tipo'] == tipo)
    ].copy()
    # Só usa imóveis acima de 7000/m2 para apartamentos/casas
    if tipo.upper() in ["APARTAMENTO", "CASA"]:
        similares = similares[(similares['m2'] > 0) & ((similares['valor'] / similares['m2']) >= 7000)]
    else:
        similares = similares[similares['m2'] > 0]
    if similares.empty:
        return []
    # Ordena pelo mais próximo da metragem
    similares['score'] = (similares['m2'] - m2).abs()
    return similares.sort_values('score').head(n)

@app.route("/", methods=["GET", "POST"])
def avaliacao():
    estados = sorted(list(estados_cidades_bairros.keys()))
    estado = request.form.get("estado") or estados[0]
    cidades_disp = sorted(list(estados_cidades_bairros[estado].keys()))
    cidade = request.form.get("cidade") or cidades_disp[0]
    bairros = estados_cidades_bairros[estado][cidade]
    tipos_disp = ["APARTAMENTO", "CASA", "TERRENO"]
    mobilias_disp = ["SIM", "NAO", "SO ARMARIOS"]

    valor_estimado = None
    valor_final = None
    valor_m2_final = None
    mensagem_erro = None
    dados_busca = None
    lista_referencias = []
    valor_medio = None
    valor_m2_medio = None

    valor_rapido = None
    valor_ate_6m = None
    valor_apos_12m = None

    if request.method == "POST" and "avaliar" in request.form:
        try:
            estado_form = normaliza_texto(request.form.get("estado") or "GO")
            cidade_form = normaliza_texto(request.form.get("cidade") or "")
            bairro_form = padronizar_bairro(normaliza_texto(request.form.get("bairro") or ""))
            tipo = normaliza_texto(request.form.get("tipo") or "")
            mobilia = normaliza_texto(request.form.get("mobilia") or "")
            m2 = float(request.form.get("m2") or 0)
            quartos = int(request.form.get("quartos") or 0)
            banheiros = int(request.form.get("banheiros") or 0)
            garagem = int(request.form.get("garagem") or 0)
            ano = int(request.form.get("ano") or 2000)

            dados_busca = {
                "Estado": estado_form,
                "Cidade": cidade_form,
                "Bairro": bairro_form,
                "Tipo": tipo,
                "Metragem (m²)": m2,
                "Quartos": quartos,
                "Banheiros": banheiros,
                "Garagem": garagem,
                "Ano": ano,
                "Mobília": mobilia,
            }

            referencias = buscar_referencias(
                df,
                bairro=bairro_form,
                tipo=tipo,
                m2=m2,
                quartos=quartos,
                banheiros=banheiros,
                garagem=garagem,
                ano=ano,
                n=10
            )

            if not isinstance(referencias, list) and not referencias.empty:
                valor_m2_medio = (referencias["valor"] / referencias["m2"]).mean()

                # Fator de mobília
                fator_mobilia = 1.0
                if mobilia == "SIM":
                    fator_mobilia = 1.12
                elif mobilia in ["SO ARMARIOS", "SÓ ARMÁRIOS"]:
                    fator_mobilia = 1.08

                valor_m2_final = valor_m2_medio * fator_mobilia
                valor_final = valor_m2_final * m2
                valor_medio = valor_final 

                lista_referencias = []
                for _, item in referencias.iterrows():
                    lista_referencias.append({
                        "bairro": item.get("bairro", ""),
                        "tipo": item.get("tipo", ""),
                        "m2": item.get("m2", 0),
                        "quartos": item.get("quartos", 0),
                        "banheiros": item.get("banheiros", 0),
                        "garagem": item.get("garagem", 0),
                        "mobilia": item.get("mobilia", ""),
                        "valor": item.get("valor", 0),
                        "valor_m2": float(item["valor"]) / float(item["m2"]) if item.get("m2", 0) else 0,
                    })

                valor_rapido = valor_final * 0.88
                valor_ate_6m = valor_final
                valor_apos_12m = valor_final * 1.12
            else:
                mensagem_erro = "Corretor, este filtro ainda está em aprendizado pela I.A. Por favor, verifique se o perfil de busca está correto."
                valor_final = None
                valor_m2_final = None
                lista_referencias = []
                valor_rapido = None
                valor_ate_6m = None
                valor_apos_12m = None

        except Exception as e:
            mensagem_erro = f"Erro na avaliação: {e}"

    return render_template(
        "avaliacao.html",
        estados=estados,
        cidades=cidades_disp,
        bairros=bairros,
        estado=estado,
        cidade=cidade,
        bairro=request.form.get("bairro") or bairros[0],
        tipos=tipos_disp,
        mobilias=mobilias_disp,
        valor_estimado=valor_final,
        valor_m2=valor_m2_final,
        mensagem_erro=mensagem_erro,
        dados_busca=dados_busca,
        lista_referencias=lista_referencias,
        valor_medio_referencias=valor_medio,
        valor_m2_medio_referencias=valor_m2_medio,
        valor_rapido=valor_rapido,
        valor_ate_6m=valor_ate_6m,
        valor_apos_12m=valor_apos_12m,
    )

@app.route("/posicao-solar")
def posicao_solar():
    return render_template("posicao_solar.html")

@app.route("/api/solar", methods=["POST"])
def api_solar():
    data = request.get_json()
    latitude = float(data.get("latitude"))
    longitude = float(data.get("longitude"))
    date_str = data.get("date")
    time_str = data.get("time")
    if date_str and time_str:
        dt_str = f"{date_str} {time_str}"
        dt = datetime.fromisoformat(dt_str)
    else:
        dt = datetime.now()
    city = LocationInfo(name="Imóvel", region="BR", timezone="America/Sao_Paulo", latitude=latitude, longitude=longitude)
    tz = pytz.timezone(city.timezone)
    dt = tz.localize(dt.replace(tzinfo=None))
    s = sun(city.observer, date=dt, tzinfo=city.timezone)
    from astral import sun as sunmod

    azimuth_now = sunmod.azimuth(city.observer, dt)
    elevation_now = sunmod.elevation(city.observer, dt)

    arco_points = []
    for h in range(0, 24*4):
        t = s['sunrise'].replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(minutes=15*h)
        az = sunmod.azimuth(city.observer, t)
        el = sunmod.elevation(city.observer, t)
        arco_points.append({'azimuth': az, 'elevation': el})

    arco_dia = [pt for pt in arco_points if pt['elevation'] > 0]
    sunrise = s['sunrise']
    sunset = s['sunset']
    azimuth_sunrise = sunmod.azimuth(city.observer, sunrise)
    azimuth_sunset = sunmod.azimuth(city.observer, sunset)

    return jsonify({
        "latitude": latitude,
        "longitude": longitude,
        "datetime": dt.strftime("%Y-%m-%d %H:%M"),
        "azimuth": round(azimuth_now, 2),
        "elevation": round(elevation_now, 2),
        "arco_points": arco_points,
        "arco_dia": arco_dia,
        "azimuth_sunrise": round(azimuth_sunrise, 2),
        "azimuth_sunset": round(azimuth_sunset, 2),
        "sunrise": sunrise.strftime("%H:%M"),
        "sunset": sunset.strftime("%H:%M")
    })

@app.route("/api/indices", methods=["GET"])
def api_indices():
    meses_labels = []
    indices = []
    try:
        ipca = get_bcb_last(433)
        selic = get_bcb_last(1178)
        cdi = get_bcb_last(12)
        poup = get_bcb_last(4390)

        if ipca["datas"]:
            meses_labels = ipca["datas"]

        indices = [
            {
                "nome": "IPCA",
                "valor_atual": ipca["valor_atual"],
                "unidade": "%",
                "historico": ipca["historico"],
                "datas": ipca["datas"]
            },
            {
                "nome": "SELIC",
                "valor_atual": selic["valor_atual"],
                "unidade": "%",
                "historico": selic["historico"],
                "datas": selic["datas"]
            },
            {
                "nome": "CDI",
                "valor_atual": cdi["valor_atual"],
                "unidade": "%",
                "historico": cdi["historico"],
                "datas": cdi["datas"]
            },
            {
                "nome": "Poupança",
                "valor_atual": poup["valor_atual"],
                "unidade": "%",
                "historico": poup["historico"],
                "datas": poup["datas"]
            },
            {
                "nome": "IGPM",
                "valor_atual": 3.15,
                "unidade": "%",
                "historico": [2.9, 3.1, 3.0, 3.2, 3.3, 3.15],
                "datas": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
            },
            {
                "nome": "INCC",
                "valor_atual": 2.98,
                "unidade": "%",
                "historico": [2.5, 2.8, 2.7, 2.9, 3.0, 2.98],
                "datas": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
            },
        ]
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    return jsonify({"indices": indices, "meses": meses_labels})

@app.route("/indices")
def indices():
    return render_template("indices.html")

if __name__ == "__main__":
    app.run(debug=True)