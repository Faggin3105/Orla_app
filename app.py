import pandas as pd
import unidecode
from flask import Flask, render_template, request, jsonify
from astral.sun import sun
from astral import LocationInfo
import datetime
import pytz
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os
from flask import Flask, request, jsonify, render_template
import openai
import math
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, request, redirect, url_for
from flask_login import login_required


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.secret_key = "SUA_CHAVE_SECRETA"

class User(UserMixin):
    def __init__(self, id_, username):
        self.id = id_
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(row[0], row[1])
    return None

openai.api_key = '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'

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
    "RESIDENCIAL ALPHAVILLE FLAMBOYANT": "ALPHAVILLE GOIÁS"
}

# Exemplo (substitua pelos valores reais do Sinduscon depois)
cub_por_estado = {
    'AC': {'BAIXO': 2131.00, 'MEDIO': 2558.78, 'ALTO': 3158.54},
    'AL': {'BAIXO': 2359.39, 'MEDIO': 2824.82, 'ALTO': 3520.83},
    'AM': {'BAIXO': 2041.00, 'MEDIO': 2505.82, 'ALTO': 3035.96},
    'AP': {'BAIXO': 2041.00, 'MEDIO': 2505.82, 'ALTO': 3035.96},
    'BA': {'BAIXO': 2359.39, 'MEDIO': 2824.82, 'ALTO': 3520.83},
    'CE': {'BAIXO': 2309.65, 'MEDIO': 2779.49, 'ALTO': 3454.65},
    'DF': {'BAIXO': 2246.50, 'MEDIO': 2703.55, 'ALTO': 3320.61},
    'ES': {'BAIXO': 2614.06, 'MEDIO': 3128.72, 'ALTO': 3856.97},
    'GO': {'BAIXO': 2131.00, 'MEDIO': 2558.78, 'ALTO': 3158.54},
    'MA': {'BAIXO': 1874.60, 'MEDIO': 2128.57, 'ALTO': 2634.46},
    'MG': {'BAIXO': 2359.39, 'MEDIO': 2824.82, 'ALTO': 3520.83},
    'MS': {'BAIXO': 2131.00, 'MEDIO': 2558.78, 'ALTO': 3158.54},
    'MT': {'BAIXO': 3108.21, 'MEDIO': 3644.46, 'ALTO': 4456.61},
    'PA': {'BAIXO': 2218.49, 'MEDIO': 2572.21, 'ALTO': 3276.80},
    'PB': {'BAIXO': 1581.50, 'MEDIO': 1965.59, 'ALTO': 2411.87},
    'PE': {'BAIXO': 2204.87, 'MEDIO': 2609.37, 'ALTO': 3195.79},
    'PI': {'BAIXO': 2609.78, 'MEDIO': 3157.14, 'ALTO': 4299.19},
    'PR': {'BAIXO': 2434.21, 'MEDIO': 3301.67, 'ALTO': 3714.36},
    'RJ': {'BAIXO': 2309.65, 'MEDIO': 2779.49, 'ALTO': 3454.65},
    'RN': {'BAIXO': 2136.84, 'MEDIO': 2368.11, 'ALTO': 2909.26},
    'RO': {'BAIXO': 2194.73, 'MEDIO': 2423.84, 'ALTO': 3262.53},
    'RR': {'BAIXO': 2692.00, 'MEDIO': 3084.08, 'ALTO': 4461.39},
    'RS': {'BAIXO': 2338.98, 'MEDIO': 3064.08, 'ALTO': 4109.35},
    'SC': {'BAIXO': 3651.31, 'MEDIO': 3180.15, 'ALTO': 3875.86},
    'SE': {'BAIXO': 1835.15, 'MEDIO': 2314.41, 'ALTO': 2983.68},
    'SP': {'BAIXO': 2041.56, 'MEDIO': 2505.82, 'ALTO': 3035.96},
    'TO': {'BAIXO': 2218.49, 'MEDIO': 2572.21, 'ALTO': 3276.80},
}

averbacao_por_estado_faixa = {
    'AC': [
        (0, 2000.00, 51.70),
        (2000.01, 5000.00, 82.70),
        (5000.01, 10000.00, 129.10),
        (10000.01, 30000.00, 193.60),
        (30000.01, 50000.00, 322.70),
        (50000.01, 80000.00, 516.00),
        (80000.01, 100000.00, 645.10),
        (100000.01, 200000.00, 967.70),
        (200000.01, 300000.00, 1290.30),
        (300000.01, 500000.00, 2580.10),
        (500000.01, float('inf'), 3870.60),
    ],
    'AL': [
        (0, 200000, 98.71),
        (200001, 500000, 138.00),
        (500001, 1000000, 180.88),
        (1000001, 3000000, 341.68),
        (3000001, 5000000, 513.20),
        (5000001, 8000000, 759.76),
        (8000001, 10000000, 931.28),
        (10000001, 20000000, 1563.76),
        (20000001, 30000000, 1563.76),
        (30000001, 50000000, 1563.76),
        (50000001, float('inf'), 1563.76),
    ],
    'AM': [
        (0, 17595.00, 646.06),
        (17595.01, 35190.00, 988.23),
        (35190.01, 58650.00, 1224.42),
        (58650.01, 117300.00, 1603.45),
        (117300.01, 234600.00, 2794.93),
        (234600.01, 351900.00, 4612.42),
        (351900.01, 469200.00, 7183.31),
        (469200.01, 586500.00, 9151.69),
        (586500.01, 703800.00, 11224.93),
        (703800.01, 821100.00, 11577.13),
        (821100.01, 938400.00, 12994.35),
        (938400.01, 1055700.00, 15303.81),
        (1055700.01, float('inf'), 17639.72),
    ],
    'AP': [
        (0, 250000.00, 2692.42),
        (250000.01, 50000.00, 4038.44),
        (50000.01, 750000.00, 5384.83),
        (750000.01, 1000000.00, 6731.05),
        (1000000.01, 1250000.00, 8077.26),
        (1250000.01, 1500000.00, 9423.48),
        (1500000.01, float('inf'), 10769.71),
    ],
    'BA': [
        (0, 1600.00, 319.12),
        (1600.01, 3200.00, 401.40),
        (3200.01, 8000.00, 483.68),
        (8000.01, 12000.00, 522.76),
        (12000.01, 16000.00, 562.54),
        (16000.01, 24000.00, 642.22),
        (24000.01, 32000.00, 723.98),
        (32000.01, 47000.00, 799.70),
        (47000.01, 63000.00, 881.24),
        (63000.01, 78000.00, 967.68),
        (78000.01, 118000.00, 1030.66),
        (118000.01, 160000.00, 1115.10),
        (160000.01, 235000.00, 1815.16),
        (235000.01, 350000.00, 2708.06),
        (350000.01, 530000.00, 4067.28),
        (530000.01, 800000.00, 6099.38),
        (800000.01, 1200000.00, 9147.62),
        (1200000.01, 1800000.00, 10977.08),
        (1800000.01, 2700000.00, 14270.54),
        (2700000.01, 4000000.00, 18551.68),
        (4000000.01, float('inf'), 24117.28),
    ],
    'CE': [
        (0, 200000, 1800.0),
        (200001, 500000, 2400.0),
        (500001, 1000000, 3000.0),
        (1000001, float('inf'), 4500.0), #nao colocar custas de averbação (escrever CONSULTE CARTÓRIO DE REGISTRO DE IMÓVEIS)
    ],
    'DF': [
        (0, 31442.12, 639.22),
        (31442.13, 78605.31, 807.43),
        (78605.32, 157210.62, 975.65),
        (157210.63, 251536.99, 1093.40),
        (251537.00, 550237.16, 1261.62),
        (550237.17, 833216.27, 1429.84),
        (833216.28, 1100474.32, 1598.06),
        (1100474.33, 1414895.55, 1766.27),
        (1414895.56, 1886527.40, 1934.48),
        (1886527.40, float('inf'), 2102.70),
    ],
    'ES': [
        (0,        1000.00,    42.91),
        (1000.01,  3000.00,    53.12),
        (3000.01,  5000.00,    73.55),
        (5000.01,  10000.00,   109.31),
        (10000.01, 15000.00,   160.38),
        (15000.01, 20000.00,   211.47),
        (20000.01, 25000.00,   262.54),
        (25000.01, 30000.00,   313.61),
        (30000.01, 35000.00,   364.69),
        (35000.01, 40000.00,   415.77),
        (40000.01, 45000.00,   466.85),
        (45000.01, 50000.00,   517.92),
        (50000.01, 55000.00,   569.00),
        (55000.01, 60000.00,   620.08),
        (60000.01, 65000.00,   671.16),
        (65000.01, 70000.00,   722.24),
        (70000.01, 75000.00,   773.32),
        (75000.01, 80000.00,   824.39),
        (80000.01, 85000.00,   875.47),
        (85000.01, 90000.00,   926.54),
        (90000.01, 95000.00,   977.63),
        (95000.01, 100000.00,  1028.70),
        (100000.01, 105000.00, 1079.77),
        (105000.01, 110000.00, 1130.86),
        (110000.01, 115000.00, 1181.93),
        (115000.01, 120000.00, 1233.01),
        (120000.01, 125000.00, 1284.08),
        (125000.01, 130000.00, 1335.16),
        (130000.01, 140000.00, 1411.78),
        (140000.01, 150000.00, 1513.93),
        (150000.01, 160000.00, 1616.09),
        (160000.01, 170000.00, 1718.24),
        (170000.01, 180000.00, 1820.40),
        (180000.01, 200000.00, 1973.63),
        (200000.01, float('inf'), 2177.93),
    ],
    'GO': [
        (0, 625.89, 22.85),
        (625.90, 1251.79, 34.64),
        (1251.80, 2503.58, 44.22),
        (2503.59, 5007.15, 64.13),
        (5007.16, 10014.30, 126.03),
        (10014.31, 15021.47, 134.88),
        (15021.48, 25035.77, 171.73),
        (25035.78, 37553.65, 217.44),
        (37553.66, 50071.55, 288.18),
        (50071.56, 62589.43, 342.72),
        (62589.44, 100143.09, 480.55),
        (100143.10, 150214.64, 722.30),
        (150214.65, 250357.73, 972.89),
        (250357.74, 375536.58, 1277.30),
        (375536.59, 500715.44, 1505.04),
        (500715.45, 751073.17, 1806.50),
        (751073.18, 1126609.75, 2164.69),
        (1126609.76, 1502146.34, 2517.01),
        (1502146.35, float('inf'), 2749.56),
    ],
    'MA': [
        (0, 5680.06, 53.07),
        (5680.07, 7384.08, 66.20),
        (7384.09, 9230.10, 75.33),
        (9230.11, 11537.63, 93.12),
        (11537.64, 14422.04, 116.43),
        (14422.05, 18027.54, 145.59),
        (18027.55, 22534.42, 182.97),
        (22534.43, 28168.01, 229.16),
        (28168.02, 35210.02, 285.54),
        (35210.03, 44012.53, 356.83),
        (44012.54, 55015.63, 446.68),
        (55015.64, 68769.53, 558.21),
        (68769.54, 85961.94, 697.54),
        (85961.95, 107452.41, 871.42),
        (107452.42, 134315.51, 1089.07),
        (134315.52, 167894.37, 1361.89),
        (167894.38, 209867.97, 1702.02),
        (209867.98, 262334.98, 2128.25),
        (262334.99, 327918.71, 2659.41),
        (327918.72, 409898.40, 3324.83),
        (409898.41, 512372.99, 4155.14),
        (512373.00, 640466.24, 5194.59),
        (640466.25, 800582.81, 6493.72),
        (800582.82, 1000728.50, 7852.36),
        (1000728.51, 1250910.66, 8231.50),
    ],
    'MG': [
        (0, 1400.00, 105.34),
        (1400.01, 2720.00, 171.84),
        (2720.01, 5440.00, 249.02),
        (5440.01, 7000.00, 344.74),
        (7000.01, 14000.00, 459.72),
        (14000.01, 28000.00, 593.94),
        (28000.01, 42000.00, 747.06),
        (42000.01, 56000.00, 919.61),
        (56000.01, 70000.00, 1111.24),
        (70000.01, 105000.00, 1398.56),
        (105000.01, 140000.00, 1777.55),
        (140000.01, 175000.00, 1900.87),
        (175000.01, 210000.00, 2024.40),
        (210000.01, 280000.00, 2279.34),
        (280000.01, 350000.00, 2342.14),
        (350000.01, 420000.00, 2405.21),
        (420000.01, 560000.00, 2638.08),
        (560000.01, 700000.00, 2783.08),
        (700000.01, 840000.00, 2928.36),
        (840000.01, 1120000.00, 3279.75),
        (1120000.01, 1400000.00, 3552.54),
        (1400000.01, 1680000.00, 3825.78),
        (1680000.01, 3200000.00, 4099.59),
    ],
    'MS': [
        (0.01, 15000.00, 13.82),
        (15000.01, 20000.00, 17.66),
        (20000.01, 25000.00, 21.50),
        (25000.01, 30000.00, 25.34),
        (30000.01, 35000.00, 29.18),
        (35000.01, 40000.00, 33.02),
        (40000.01, 45000.00, 36.86),
        (45000.01, 50000.00, 40.70),
        (50000.01, 55000.00, 44.54),
        (55000.01, 60000.00, 48.38),
        (60000.01, 65000.00, 52.22),
        (65000.01, 70000.00, 56.06),
        (70000.01, 75000.00, 59.90),
        (75000.01, 80000.00, 63.74),
        (80000.01, 85000.00, 67.58),
        (90000.01, 95000.00, 71.42),
        (95000.01, 100000.00, 75.26),
        (100000.01, 110000.00, 79.10),
        (110000.01, 120000.00, 82.94),
        (120000.01, 130000.00, 86.78),
        (130000.01, 140000.00, 90.62),
        (140000.01, 150000.00, 94.46),
        (150000.01, 160000.00, 98.30),
        (160000.01, 170000.00, 102.14),
        (170000.01, 180000.00, 105.98),
        (180000.01, 190000.00, 109.81),
        (190000.01, 200000.00, 113.65),
        (200000.01, 210000.00, 117.49),
        (210000.01, 220000.00, 121.33),
        (220000.01, 230000.00, 125.17),
        (230000.01, 240000.00, 129.01),
        (240000.01, 250000.00, 132.85),
        (250000.01, 260000.00, 136.69),
        (260000.01, 270000.00, 140.53),
        (270000.01, 280000.00, 144.37),
        (280000.01, 290000.00, 148.21),
        (290000.01, 300000.00, 152.05),
        (300000.01, 325000.00, 155.89),
        (325000.01, 350000.00, 159.73),
        (350000.01, 375000.00, 163.57),
        (375000.01, 400000.00, 167.41),
        (400000.01, 425000.00, 171.25),
        (425000.01, 450000.00, 175.09),
        (450000.01, 475000.00, 178.93),
        (475000.01, 500000.00, 182.77),
        (500000.01, 600000.00, 184.15),
        (600000.01, 700000.00, 185.53),
        (700000.01, 800000.00, 186.91),
        (800000.01, 900000.00, 188.30),
        (900000.01, 1000000.00, 189.68),
        (1000000.01, 2000000.00, 191.06),
        (2000000.01, 3000000.00, 192.44),
        (3000000.01, 4000000.00, 193.82),
        (4000000.01, 5000000.00, 195.21),
        (5000000.01, 7000000.00, 196.59),
        (7000000.01, 9000000.00, 197.97),
        (9000000.01, float('inf'), 199.66),
    ],
    'MT': [
        (0, 70, 200.00),
        (70.01, 100, 300.95),
        (100.01, 150, 501.90),
        (150.01, 200, 803.00),
        (200.01, 250, 1014.65),
        (250.01, 300, 1405.60),
        (300.01, float('inf'), 1807.80), #usa faixa de m2 e nao valor da construcao
    ],
    'PA': [
        (0.00, 15000.00, 226.10),
        (15000.01, 30000.00, 451.70),
        (30000.01, 45000.00, 668.90),
        (45000.01, 60000.00, 887.00),
        (60000.01, 75000.00, 1108.70),
        (75000.01, 90000.00, 1326.60),
        (90000.01, 120000.00, 1768.90),
        (120000.01, 150000.00, 2211.20),
        (150000.01, 180000.00, 2653.40),
        (180000.01, 210000.00, 3095.60),
        (210000.01, 240000.00, 3537.80),
        (240000.01, 270000.00, 3980.00),
        (270000.01, 300000.00, 4422.30),
        (300000.01, 330000.00, 4864.50),
        (330000.01, 360000.00, 5306.70),
        (360000.01, 390000.00, 5749.00),
        (390000.01, 420000.00, 6191.20),
        (420000.01, 450000.00, 6601.80),
        (450000.01, 480000.00, 7041.90),
        (480000.01, 510000.00, 7482.00),
        (510000.01, 540000.00, 7922.10),
        (540000.01, 570000.00, 8362.30),
        (570000.01, 600000.00, 8802.40),
        (600000.01, 630000.00, 9242.50),
        (630000.01, 660000.00, 9682.70),
        (660000.01, 690000.00, 10122.80),
        (690000.01, 720000.00, 10562.90),
        (720000.01, 750000.00, 11003.00),
        (750000.01, 780000.00, 11443.10),
        (780000.01, 810000.00, 11883.30),
        (810000.01, 840000.00, 12323.40),
        (840000.01, 870000.00, 12763.50),
        (870000.01, 900000.00, 13203.60),
        (900000.01, 930000.00, 13643.70),
        (930000.01, 960000.00, 14016.80),
        (960000.01, 990000.00, 14454.80),
        (990000.01, 1020000.00, 14892.80),
        (1020000.01, 1050000.00, 15330.70),
        (1050000.01, 1080000.00, 15768.80),
        (1080000.01, 1110000.00, 16206.80),
        (1110000.01, float('inf'), 16665.70),
    ],
    'PB': [
        (0, 16865.00, 141.67),
        (16865.01, 33730.00, 354.17),
        (33730.01, 47222.00, 566.66),
        (47222.01, 67460.00, 809.52),
    ],
    'PE': [
        (5000.01, 6000.00, 106.87),
        (6000.01, 7000.00, 112.01),
        (7000.01, 8000.00, 117.16),
        (8000.01, 9000.00, 122.32),
        (9000.01, 10000.00, 127.48),
        (10000.01, 11000.00, 132.51),
        (11000.01, 12000.00, 137.81),
        (12000.01, 13000.00, 143.00),
        (13000.01, 14000.00, 148.12),
        (14000.01, 15000.00, 153.26),
        (15000.01, 16000.00, 158.40),
        (16000.01, 17000.00, 163.55),
        (17000.01, 18000.00, 168.70),
        (18000.01, 19000.00, 173.84),
        (19000.01, 20000.00, 178.97),
        (20000.01, 25000.00, 191.97),
        (25000.01, 30000.00, 217.76),
        (30000.01, 35000.00, 243.54),
        (35000.01, 40000.00, 269.30),
        (40000.01, 45000.00, 295.08),
        (45000.01, 50000.00, 320.90),
        (50000.01, 55000.00, 346.70),
        (55000.01, 60000.00, 372.50),
        (60000.01, 65000.00, 398.29),
        (65000.01, 70000.00, 424.05),
        (70000.01, 75000.00, 449.86),
        (75000.01, 80000.00, 475.65),
        (80000.01, 85000.00, 501.45),
        (85000.01, 90000.00, 527.24),
        (90000.01, 95000.00, 553.03),
        (95000.01, 100000.00, 578.83),
        (100000.01, 105000.00, 604.61),
        (105000.01, 110000.00, 630.39),
        (110000.01, 115000.00, 656.19),
        (115000.01, 120000.00, 681.98),
        (120000.01, 125000.00, 707.78),
        (125000.01, 130000.00, 733.57),
        (130000.01, 135000.00, 759.37),
        (135000.01, 140000.00, 785.14),
        (140000.01, 145000.00, 810.93),
        (145000.01, 150000.00, 836.71),
        (150000.01, 155000.00, 862.51),
        (155000.01, 160000.00, 888.30),
        (160000.01, 165000.00, 914.09),
        (165000.01, 170000.00, 939.89),
        (170000.01, 175000.00, 965.69),
        (175000.01, 180000.00, 991.48),
        (180000.01, 185000.00, 1017.29),
        (185000.01, 190000.00, 1043.11),
        (190000.01, 195000.00, 1068.87),
        (195000.01, 200000.00, 1094.62),
        (200000.01, 205000.00, 1120.41),
        (205000.01, 210000.00, 1146.20),
        (210000.01, 215000.00, 1171.98),
        (215000.01, 220000.00, 1197.77),
        (220000.01, 225000.00, 1223.57),
        (225000.01, 230000.00, 1249.36),
        (230000.01, 235000.00, 1275.15),
        (235000.01, 240000.00, 1300.95),
        (240000.01, 245000.00, 1326.73),
        (245000.01, 250000.00, 1352.53),
        (250000.01, 255000.00, 1378.36),
        (255000.01, 260000.00, 1404.15),
        (260000.01, 265000.00, 1429.93),
        (265000.01, 270000.00, 1455.73),
        (270000.01, 275000.00, 1481.51),
        (275000.01, 278000.00, 1502.18),
        (278000.01, float('inf'), 1507.23),
    ],
    'PI': [
        (0, 200000, 1800.0),
        (200001, 500000, 2400.0),
        (500001, 1000000, 3000.0),
        (1000001, float('inf'), 4500.0),#nao colocar custas de averbação (escrever CONSULTE CARTÓRIO DE REGISTRO DE IMÓVEIS)
    ],
    'PR': [
        (0, 200000, 1800.0),
        (200001, 500000, 2400.0),
        (500001, 1000000, 3000.0),
        (1000001, float('inf'), 4500.0), #nao colocar custas de averbação (escrever CONSULTE CARTÓRIO DE REGISTRO DE IMÓVEIS)
    ],
    'RJ': [
        (0, 17417.06, 92.31),
        (17417.07, 34834.16, 242.35),
        (34834.17, 52251.24, 342.25),
        (52251.25, 69668.33, 392.45),
        (69668.34, 92891.09, 492.45),
        (92891.10, 116113.88, 600.45),
        (116113.89, 232227.77, 708.13),
        (232227.78, 464455.57, 770.57), #adicionar o calculo que A partir do valor de R$ 464.455,58, a cada R$ 116.113,88 em que se incluir o valor do imóvel, serão cobrados mais R$ 106,41 no valor da averbação
    ],
    'RN': [
        (0, 100.00, 484.64),
        (100.01, 200.00, 986.13),
        (200.01, 300.00, 1476.15),
        (300.01, 400.00, 1963.76),
        (400.01, 500.00, 2451.32),
        (500.01, 600.00, 2697.31),
        (600.01, 700.00, 2939.23),
        (700.01, 800.00, 3181.15),
        (800.01, 900.00, 3423.08),
        (900.01, 1000.00, 3664.99),
        (1000.01, 1100.00, 3795.47),
        (1100.01, 1200.00, 3921.89),
        (1200.01, 1300.00, 4048.29),
        (1300.01, 1400.00, 4174.69),
    # Acima de 1400m² deve ser consultado no cartório
    ],
    'RO': [
        (0.01, 28493.00, 71.40),
        (28493.01, 37806.00, 132.03),
        (37806.01, 47116.00, 166.49),
        (47116.01, 56428.00, 199.10),
        (56428.01, 65739.00, 231.71),
        (65739.01, 75052.00, 264.30),
        (75052.01, 93675.00, 329.51),
        (93675.01, 112298.00, 386.06),
        (112298.01, 130921.00, 439.77),
        (130921.01, 149546.00, 490.60),
        (149546.01, 168169.00, 538.58),
        (168169.01, 205414.00, 641.75),
        (205414.01, 242661.00, 739.25),
        (242661.01, 279909.00, 831.05),
        (279909.01, 317153.00, 917.24),
        (317153.01, 354400.00, 997.73),
        (354400.01, 447517.00, 1225.34),
        (447517.01, 540633.00, 1438.76),
        (540633.01, 633747.00, 1638.08),
        (633747.01, 726865.00, 1823.33),
        (726865.01, 819981.00, 1953.03),
        (819981.01, 1006213.00, 2270.08),
        (1006213.01, 1192445.00, 2539.72),
        (1192445.01, 1378677.00, 2762.73),
        (1378677.01, 1564910.00, 2939.29),
        (1564910.01, 1751140.00, 3070.78),
        (1751140.01, 1937376.00, 3156.13),
        (1937376.01, 2123605.00, 3195.50),
        (2123605.01, 2309842.00, 3268.03),
        (2309842.01, 2496071.00, 3370.81),
        (2496071.01, 2682304.00, 3498.60),
        (2682304.01, float('inf'), 3626.42),
    ],
    'RR': [
        (0, 5000.00, 58.82),
        (5000.01, 10000.00, 78.01),
        (10000.01, 15000.00, 104.08),
        (15000.01, 20000.00, 138.33),
        (20000.01, 25000.00, 185.01),
        (25000.01, 30000.00, 248.02),
        (30000.01, 35000.00, 333.01),
        (35000.01, 50000.00, 448.16),
        (50000.01, 100000.00, 604.51),
        (100000.01, 200000.00, 815.61),
        (200000.01, float('inf'), 1100.76),
    ],
    'RS': [
        (0, 2344.40, 106.80),
        (2344.41, 4688.60, 109.00),
        (4688.61, 7033.10, 113.85),
        (7033.11, 9377.50, 118.60),
        (9377.51, 11721.80, 123.25),
        (11721.81, 14065.80, 128.00),
        (14065.81, 16409.90, 132.85),
        (16409.91, 18754.70, 137.60),
        (18754.71, 21098.70, 142.05),
        (21098.71, 23443.00, 146.60),
        (23443.01, 35164.60, 161.00),
        (35164.61, 46886.30, 184.60),
        (46886.31, 70329.70, 220.05),
        (70329.71, 93772.70, 267.10),
        (93772.71, 117216.10, 314.05),
        (117216.11, 140659.00, 361.20),
        (140659.01, 164102.20, 408.35),
        (164102.21, 187545.50, 455.40),
        (187545.51, 210988.80, 502.65),
        (210988.81, 234431.80, 549.75),
        (234431.81, 281318.30, 620.30),
        (281318.31, 328204.50, 714.30),
        (328204.51, 375090.70, 808.60),
        (375090.71, 421977.10, 902.75),
        (421977.11, 468863.50, 997.40),
        (468863.51, 586079.70, 1162.30),
        (586079.71, 703295.40, 1397.55),
        (703295.41, 820511.30, 1633.30),
        (820511.31, 937727.10, 1868.60),
        (937727.11, 1054943.10, 2104.15),
        (1054943.11, 1172159.10, 2339.70),
        (1172159.11, float('inf'), 2589.70),
    ],
    'SC': [
        (0, 19850.14, 92.56),
        (19850.15, 33083.58, 108.80),
        (33083.59, 46317.00, 149.41),
        (46317.01, 59550.44, 198.14),
        (59550.45, 72783.87, 248.49),
        (72783.88, 86017.30, 302.08),
        (86017.31, 99250.72, 357.29),
        (99250.73, 112484.17, 412.52),
        (112484.18, 125717.60, 453.13),
        (125717.61, 138951.02, 495.35),
        (138951.03, 152184.45, 548.94),
        (152184.46, 165417.90, 604.16),
        (165417.91, 185268.04, 659.37),
        (185268.05, 205118.19, 727.59),
        (205118.20, 224968.33, 787.69),
        (224968.34, 244818.48, 846.17),
        (244818.49, 264668.63, 906.26),
        (264668.64, 284518.77, 966.35),
        (284518.78, 304368.92, 1024.83), #A cada R$50.000,00 que adicionar na base de cálculo, serão cobrados mais R$ 50,00 (cinquenta reais)
    ],
    'SE': [
        (0, 5999.99, 316.66),
        (6000.00, 12999.99, 513.01),
        (13000.00, 25000.00, 708.46), #A partir de R$ 25.000,01, por cada R$ 5.000,00 excedentes, acrescer o valor de R$ 36,77 até o limite de R$ 8.356,99.
    ],
    'SP': [
        (0.01, 2222.00, 88.09),
        (2222.01, 5551.00, 132.71),
        (5551.01, 9253.00, 226.89),
        (9253.01, 18510.00, 369.48),
        (18510.01, 37020.00, 471.30),
        (37020.01, 111060.00, 492.29),
        (111060.01, 185100.00, 548.33),
        (185100.01, 222120.00, 604.35),
        (222120.01, 259140.00, 632.57),
        (259140.01, 296160.00, 660.39),
        (296160.01, 333180.00, 688.64),
        (333180.01, 370200.00, 716.53),
        (370200.01, 740400.00, 870.52),
        (740400.01, 1110600.00, 1150.82),
        (1110600.01, 1480800.00, 1431.07),
        (1480800.01, 1851000.00, 1711.30),
        (1851000.01, 2221200.00, 1856.17),
        (2221200.01, 3702000.00, 2580.67),
        (3702000.01, 5553000.00, 3884.75),
        (5553000.01, 7404000.00, 5333.70),
        (7404000.01, 9255000.00, 6782.67),
        (9255000.01, 11106000.00, 8231.63),
        (11106000.01, 12957000.00, 9680.60),
        (12957000.01, 14808000.00, 11129.55),
        (14808000.01, 16659000.00, 12578.52),
        (16659000.01, 18510000.00, 14027.48),
        (18510000.01, 22212000.00, 16200.92),
        (22212000.01, 25914000.00, 19098.86),
        (25914000.01, 29616000.00, 21996.77),
        (29616000.01, 33318000.00, 24894.71),
        (33318000.01, 37020000.00, 27792.62),
        (37020000.01, 40722000.00, 32139.52),
        (40722000.01, 44424000.00, 35037.49),
        (44424000.01, 48126000.00, 37935.40),
        (48126000.01, 51828000.00, 40833.34),
        (51828000.01, 55530000.00, 43731.26),
        (55530000.01, 62934000.00, 46629.15),
        (62934000.01, 70338000.00, 52425.00),
        (70338000.01, 77742000.00, 58220.85),
        (77742000.01, 85146000.00, 64016.70),
        (85146000.01, 92550000.00, 69812.56),
        (92550000.01, 99954000.00, 72710.48),
        (99954000.01, 107358000.00, 75608.41),
        (107358000.01, 114762000.00, 78506.33),
        (114762000.01, 122166000.00, 81404.26),
        (122166000.01, 129570000.00, 84302.18),
        (129570000.01, 136974000.00, 87200.11),
        (136974000.01, float('inf'), 90197.64),
    ],
    'TO': [
    (0.01, 3000.00, 237.40),
    (3000.01, 6000.00, 477.45),
    (6000.01, 10000.00, 639.80),
    (10000.01, 20000.00, 885.32),
    (20000.01, 30000.00, 1376.41),
    (30000.01, 40000.00, 1785.65),
    (40000.01, 60000.00, 2194.88),
    (60000.01, 80000.00, 2669.59),
    (80000.01, 100000.00, 2945.81), #Pelo que exceder de R$ 100.000,00 (cem mil reais), a cada R$ 50.000,00, acrescenta-se o valor de R$ 143,12 até o teto de R$ 15.252,57
    ],
}

import requests

def get_ibge_custo_construcao():
    url = "https://servicodados.ibge.gov.br/api/v3/agregados/6586/periodos/-1/variaveis/9327?localidades=N1[all]"
    resp = requests.get(url)
    data = resp.json()
    try:
        serie = data[0]['resultados'][0]['series'][0]['serie']
        # pega o último valor disponível
        ultimo_periodo = sorted(serie.keys())[-1]
        valor = float(serie[ultimo_periodo].replace(',', '.'))
        return round(valor, 2)
    except Exception as e:
        print("Erro ao buscar custo construção civil:", e)
        return None

def get_ibge_desemprego():
    url = "https://servicodados.ibge.gov.br/api/v3/agregados/1616/periodos/-1/variaveis/4092?localidades=N1[all]&classificacao=1965[40310]"
    resp = requests.get(url)
    data = resp.json()
    try:
        serie = data[0]['resultados'][0]['series'][0]['serie']
        ultimo_periodo = sorted(serie.keys())[-1]
        valor = float(serie[ultimo_periodo].replace(',', '.'))
        return round(valor, 2)
    except Exception as e:
        print("Erro ao buscar desemprego:", e)
        return None

def calcula_price(valor, taxa_mensal, prazo, data_inicio):
    parcelas = []
    saldo = valor
    total_pago = total_juros = total_amort = 0
    if taxa_mensal == 0:
        parcela_fixa = valor / prazo
    else:
        parcela_fixa = valor * (taxa_mensal * (1+taxa_mensal)**prazo) / ((1+taxa_mensal)**prazo - 1)
    for n in range(1, prazo+1):
        juros = saldo * taxa_mensal
        amort = parcela_fixa - juros
        saldo -= amort
        total_pago += parcela_fixa
        total_juros += juros
        total_amort += amort
        data_venc = (data_inicio + timedelta(days=30*(n-1))).strftime('%d/%m/%Y')
        parcelas.append({
            'numero': n,
            'data_venc': data_venc,
            'valor_parcela': parcela_fixa,
            'amortizacao': amort,
            'juros': juros,
            'saldo_devedor': max(saldo,0)
        })
    return parcelas, total_pago, total_juros, total_amort

def calcula_sac(valor, taxa_mensal, prazo, data_inicio):
    parcelas = []
    saldo = valor
    amort = valor / prazo
    total_pago = total_juros = total_amort = 0
    for n in range(1, prazo+1):
        juros = saldo * taxa_mensal
        valor_parcela = amort + juros
        saldo -= amort
        total_pago += valor_parcela
        total_juros += juros
        total_amort += amort
        data_venc = (data_inicio + timedelta(days=30*(n-1))).strftime('%d/%m/%Y')
        parcelas.append({
            'numero': n,
            'data_venc': data_venc,
            'valor_parcela': valor_parcela,
            'amortizacao': amort,
            'juros': juros,
            'saldo_devedor': max(saldo,0)
        })
    return parcelas, total_pago, total_juros, total_amort

def get_bcb_last(codigo_serie):
    """Busca o último valor do BACEN usando a interface pública JSON."""
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados/ultimos/1?formato=json"
    resp = requests.get(url)
    resp.raise_for_status()
    dados = resp.json()
    if dados and isinstance(dados, list) and len(dados) > 0:
        valor = float(dados[-1]['valor'].replace(',', '.'))
        return valor
    return None

def format_money(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcula_valor_m2(valor, area):
    try:
        if area and area > 0:
            return valor / area
        else:
            return 0.0
    except Exception:
        return 0.0

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

def buscar_referencias(df, bairro, tipo, m2, quartos, banheiros, garagem, ano, n=20):
    similares = df[
        (df['bairro'] == bairro) &
        (df['tipo'] == tipo)
    ].copy()
    if tipo.upper() in ["APARTAMENTO", "CASA"]:
        similares = similares[(similares['m2'] > 0) & ((similares['valor'] / similares['m2']) >= 7000)]
    else:
        similares = similares[similares['m2'] > 0]
    if similares.empty:
        return []
    similares['score'] = (similares['m2'] - m2).abs()
    return similares.sort_values('score').head(n)

# ---- LOGIN ----
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row and check_password_hash(row[2], password):
            user = User(row[0], row[1])
            login_user(user)
            return render_template("home.html")  # Ou redirect(url_for("home"))
        else:
            return render_template("login.html", error="Usuário ou senha inválidos.")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ---- HOME ----
@app.route("/")
@login_required
def home():
    return render_template("home.html")

@app.route("/avaliacao", methods=["GET", "POST"])
@login_required
def avaliacao():
    estados = sorted(list(estados_cidades_bairros.keys()))
    estado = request.form.get("estado") or estados[0]
    cidades_disp = sorted(list(estados_cidades_bairros[estado].keys()))
    cidade = request.form.get("cidade") or cidades_disp[0]
    bairros = estados_cidades_bairros[estado][cidade]
    tipos_disp = ["APARTAMENTO", "CASA", "TERRENO"]
    mobilias_disp = ["SIM", "NAO", "SO ARMARIOS"]

    valor_rapido = valor_ate_6m = valor_apos_12m = None
    valor_rapido_m2 = valor_ate_6m_m2 = valor_apos_12m_m2 = None
    mensagem_erro = None
    dados_busca = None
    lista_referencias = []
    valor_medio = None

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
                n=20
            )

            if not isinstance(referencias, list) and not referencias.empty:
                valores_m2 = (referencias["valor"] / referencias["m2"]).copy()

                # Filtro de outliers pelo método IQR (robusto)
                q1 = valores_m2.quantile(0.10)
                q3 = valores_m2.quantile(0.90)
                iqr = q3 - q1
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                valores_filtrados = valores_m2[(valores_m2 >= lower) & (valores_m2 <= upper)]

                # Use sempre a mediana!
                valor_m2_medio = valores_filtrados.median()

                # Fator de mobília
                fator_mobilia = 1.0
                if mobilia == "SIM":
                    fator_mobilia = 1.08
                elif mobilia in ["SO ARMARIOS", "SÓ ARMÁRIOS"]:
                    fator_mobilia = 1.05

                valor_m2_final = valor_m2_medio * fator_mobilia
                valor_ate_6m = valor_m2_final * m2
                valor_rapido = valor_ate_6m * 0.88
                valor_apos_12m = valor_ate_6m * 1.12
                valor_medio = valor_ate_6m

                valor_rapido_m2 = calcula_valor_m2(valor_rapido, m2)
                valor_ate_6m_m2 = calcula_valor_m2(valor_ate_6m, m2)
                valor_apos_12m_m2 = calcula_valor_m2(valor_apos_12m, m2)

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
            else:
                mensagem_erro = "Corretor, este filtro ainda está em aprendizado pela I.A. Por favor, verifique se o perfil de busca está correto."
                valor_rapido = valor_ate_6m = valor_apos_12m = None
                valor_rapido_m2 = valor_ate_6m_m2 = valor_apos_12m_m2 = None
                lista_referencias = []

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
        mensagem_erro=mensagem_erro,
        dados_busca=dados_busca,
        lista_referencias=lista_referencias,
        valor_rapido=valor_rapido,
        valor_ate_6m=valor_ate_6m,
        valor_apos_12m=valor_apos_12m,
        valor_rapido_m2=valor_rapido_m2,
        valor_ate_6m_m2=valor_ate_6m_m2,
        valor_apos_12m_m2=valor_apos_12m_m2,
        format_money=format_money,
    )

@app.route("/posicao-solar")
@login_required
def posicao_solar():
    return render_template("posicao_solar.html")

@app.route("/api/solar", methods=["POST"])
@login_required
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
@login_required
def api_indices():
    try:
        indices = [
            {"nome": "IPCA",   "valor_atual": get_bcb_last(433),    "unidade": "% a.m."},
            {"nome": "SELIC",  "valor_atual": get_bcb_last(432),    "unidade": "%"},
            {"nome": "CDI",    "valor_atual": get_bcb_last(12),     "unidade": "% a.d."},
            {"nome": "IGPM",   "valor_atual": get_bcb_last(189),    "unidade": "% a.m."},
            {"nome": "INCC",   "valor_atual": get_bcb_last(192),    "unidade": "% a.m."},
            {"nome": "Dólar",  "valor_atual": get_bcb_last(10813),  "unidade": "R$"},
            {"nome": "Euro",   "valor_atual": get_bcb_last(21620),  "unidade": "R$"},
            {"nome": "Libra",  "valor_atual": get_bcb_last(21624),  "unidade": "R$"},
        ]
        custo_construcao = get_ibge_custo_construcao()
        desemprego = get_ibge_desemprego()
        indices.append({"nome": "Custo Construção Civil", "valor_atual": custo_construcao, "unidade": "R$/m²"})
        indices.append({"nome": "Desemprego", "valor_atual": desemprego, "unidade": "%"})
        return jsonify({"indices": indices})
    except Exception as e:
        return jsonify({"erro": f"Erro ao obter índices: {str(e)}"}), 500

@app.route("/indices")
@login_required
def indices():
    return render_template("indices.html")

@app.route("/simulador", methods=["GET", "POST"])
@login_required
def simulador():
    parcelas = []
    total_pago = total_juros = total_amort = 0
    form_data = None
    if request.method == "POST":
        valor_imovel = float(request.form.get("valor_imovel") or 0)
        percentual_entrada = float(request.form.get("percentual_entrada") or 20)
        valor_entrada = float(request.form.get("valor_entrada") or (valor_imovel * percentual_entrada / 100))
        valor_financiado = float(request.form.get("valor_financiado") or (valor_imovel - valor_entrada))
        prazo = int(request.form.get("prazo") or 360)
        taxa_juros = float(request.form.get("taxa_juros") or 1.0) / 100
        sistema = request.form.get("sistema") or "PRICE"
        data_inicio_str = request.form.get("data_inicio") or datetime.today().strftime('%Y-%m-%d')
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
        if sistema == "PRICE":
            parcelas, total_pago, total_juros, total_amort = calcula_price(valor_financiado, taxa_juros, prazo, data_inicio)
        else:
            parcelas, total_pago, total_juros, total_amort = calcula_sac(valor_financiado, taxa_juros, prazo, data_inicio)
        form_data = request.form
    return render_template(
        "simulador.html",
        parcelas=parcelas,
        total_pago=total_pago,
        total_juros=total_juros,
        total_amort=total_amort,
        form_data=form_data
    )

@app.route('/calculadora')
@login_required
def calculadora():
    return render_template('calculadora.html')

@app.route('/openai-assistente', methods=['POST'])
@login_required
def openai_assistente():
    data = request.get_json()
    pergunta = data.get('pergunta', '')
    if not pergunta:
        return jsonify({'resposta': 'Pergunta não enviada!'}), 400

    # Prompt "inteligente" focado em HP12C e linguagem amigável para corretores
    prompt = f"""
Você é um assistente financeiro especialista em HP12C, explicando para corretores de imóveis super leigos.
Explique passo a passo de maneira fácil: "{pergunta}"
Se a dúvida envolver "valor total pago", "financiamento" ou "qual foi o juros", sempre oriente a dividir o valor total pelo número de meses (PMT), deixar FV=0, e siga fielmente o passo a passo HP12C real, inclusive informando quando deve-se apertar o enter na calculadora.
Sempre comece com o nome da função, depois explique como usar na HP12C, com exemplos práticos e que funcionem 100%. Você precisa ser o mais didático possível.
"""

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # ou "gpt-4" se você tiver acesso
            messages=[
                {"role": "system", "content": "Você é um especialista em HP12C para corretores."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=550,
            temperature=0.1,
        )
        txt = resposta['choices'][0]['message']['content']
        return jsonify({'resposta': txt})
    except Exception as e:
        return jsonify({'resposta': f"Erro: {str(e)}"}), 500
    
@app.route('/construcao', methods=['GET', 'POST'])
@login_required
def construcao():
    estados = list(cub_por_estado.keys())
    resultado = None
    estado = faixa = subfaixa = area = None
    iss_percent = 0.0

    if request.method == 'POST':
        estado = request.form.get('estado')
        faixa = request.form.get('faixa')
        subfaixa = request.form.get('subfaixa')
        area = float(request.form.get('area', 0) or 0)
        iss_percent = float(request.form.get('iss', 0) or 0)

        # 1. Busca CUB Base
        cub_base = cub_por_estado[estado][faixa.upper()]

        # 2. Define fator acabamento
        fator = 1
        if faixa == 'ALTO':
            if subfaixa == 'ALTO PADRÃO BÁSICO':
                fator = 1.35
            elif subfaixa == 'LUXO':
                fator = 1.90
            elif subfaixa == 'SUPER LUXO':
                fator = 2.30

        # 3. Custo obra e valor m2
        custo_obra = cub_base * area * fator
        valor_m2 = cub_base * fator
        custo_inss = cub_base * area

        # 4. INSS (25% da obra, depois 11% disso)
        mao_obra = custo_inss * 0.25
        inss = mao_obra * 0.11

        # 5. Averbação especial para cada estado
        averbacao = calcular_averbacao(
            estado=estado,
            custo_obra=custo_obra,
            area=area
        )

        # 6. ISS (se informado)
        iss_valor = custo_obra * (iss_percent / 100.0) if iss_percent else 0

        # 7. Totais
        total_automatico = inss + (averbacao if isinstance(averbacao, float) else 0)
        total_geral = total_automatico + iss_valor

        resultado = {
            'estado': estado,
            'faixa': faixa,
            'subfaixa': subfaixa,
            'area': area,
            'valor_m2': round(valor_m2, 2),
            'custo_obra': round(custo_obra, 2),
            'inss': round(inss, 2),
            'averbacao': averbacao,
            'iss_percent': iss_percent,
            'iss_valor': round(iss_valor, 2),
            'total_automatico': round(total_automatico, 2),
            'total_geral': round(total_geral, 2)
        }

    return render_template(
        'construcao.html',
        estados=estados,
        resultado=resultado,
        estado=estado,
        faixa=faixa,
        subfaixa=subfaixa,
        area=area,
    )
def calcular_averbacao(estado, custo_obra, area):
    # CE: hiperlink
    if estado == 'CE':
        return '<a href="https://portal.tjce.jus.br/uploads/2024/12/Port.-Emolumentos-2025.pdf" target="_blank">Consulte Aqui</a>'
    # PI: hiperlink
    if estado == 'PI':
        return '<a href="https://www.tjpi.jus.br/cobjud/download/tabela_2022-02.pdf" target="_blank">Consulte Aqui</a>'
    # PR: hiperlink
    if estado == 'PR':
        return '<a href="https://www.anoregpr.org.br/wp-content/uploads/2021/12/TABELA-DE-EMOLUMENTOS-2022-RI-VRC-R-0246.pdf" target="_blank">Consulte Aqui</a>'
    # MT: faixa de m2
    if estado == 'MT':
        faixas_mt = [
            (0, 70, 200.00),
            (70.01, 100, 300.95),
            (100.01, 150, 501.90),
            (150.01, 200, 803.00),
            (200.01, 250, 1014.65),
            (250.01, 300, 1405.60),
            (300.01, float('inf'), 'Consultar cartório')
        ]
        for min_m2, max_m2, valor in faixas_mt:
            if area >= min_m2 and area <= max_m2:
                return valor
        return 'Consultar cartório'
    # RJ: progressivo acima de 464.455,58
    if estado == 'RJ':
        faixas_rj = [
            (0, 17417.06, 92.31),
            (17417.07, 34834.16, 242.35),
            (34834.17, 52251.24, 342.25),
            (52251.25, 69668.33, 392.45),
            (69668.34, 92891.09, 492.45),
            (92891.10, 116113.88, 600.45),
            (116113.89, 232227.77, 708.13),
            (232227.78, 464455.57, 770.57),
        ]
        for faixa_min, faixa_max, valor in faixas_rj:
            if custo_obra >= faixa_min and custo_obra <= faixa_max:
                return valor
        if custo_obra > 464455.58:
            excedente = custo_obra - 464455.58
            acrescimos = math.ceil(excedente / 116113.88)
            return 770.57 + acrescimos * 106.41
        return 'Consultar cartório'
    # RN: acima de 1400m2, consultar cartorio
    if estado == 'RN':
        faixas_rn = [
            (0, 100, 484.64),
            (100.01, 200, 986.13),
            (200.01, 300, 1476.15),
            (300.01, 400, 1963.76),
            (400.01, 500, 2451.32),
            (500.01, 600, 2697.31),
            (600.01, 700, 2939.23),
            (700.01, 800, 3181.15),
            (800.01, 900, 3423.08),
            (900.01, 1000, 3664.99),
            (1000.01, 1100, 3795.47),
            (1100.01, 1200, 3921.89),
            (1200.01, 1300, 4048.29),
            (1300.01, 1400, 4174.69),
        ]
        for faixa_min, faixa_max, valor in faixas_rn:
            if area >= faixa_min and area <= faixa_max:
                return valor
        return 'Consultar cartório'
    # SC: progressivo
    if estado == 'SC':
        faixas_sc = [
            (0, 19850.14, 92.56),
            (19850.15, 33083.58, 108.80),
            (33083.59, 46317.00, 149.41),
            (46317.01, 59550.44, 198.14),
            (59550.45, 72783.87, 248.49),
            (72783.88, 86017.30, 302.08),
            (86017.31, 99250.72, 357.29),
            (99250.73, 112484.17, 412.52),
            (112484.18, 125717.60, 453.13),
            (125717.61, 138951.02, 495.35),
            (138951.03, 152184.45, 548.94),
            (152184.46, 165417.90, 604.16),
            (165417.91, 185268.04, 659.37),
            (185268.05, 205118.19, 727.59),
            (205118.20, 224968.33, 787.69),
            (224968.34, 244818.48, 846.17),
            (244818.49, 264668.63, 906.26),
            (264668.64, 284518.77, 966.35),
            (284518.78, 304368.92, 1024.83)
        ]
        for faixa_min, faixa_max, valor in faixas_sc:
            if custo_obra >= faixa_min and custo_obra <= faixa_max:
                return valor
        if custo_obra > 304368.92:
            excedente = custo_obra - 304368.92
            acrescimos = math.ceil(excedente / 50000.00)
            return 835.03+189.80 + acrescimos*50
        return 'Consultar cartório'
    # SE: progressivo
    if estado == 'SE':
        faixas_se = [
            (0, 5999.99, 316.66),
            (6000.00, 12999.99, 513.01),
            (13000.00, 25000.00, 708.46),
    ]
        for faixa_min, faixa_max, valor in faixas_se:
            if custo_obra >= faixa_min and custo_obra <= faixa_max:
                return valor
        if custo_obra > 25000.00:
            excedente = custo_obra - 25000.00
            acrescimos = math.ceil(excedente / 5000.00)
            valor_averbacao = 708.46 + (acrescimos * 36.77)
            return min(valor_averbacao, 8356.99)
        return 'Consultar cartório'
    # TO: progressivo
    if estado == 'TO':
        faixas_to = [
            (0.01, 3000.00, 237.40),
            (3000.01, 6000.00, 477.45),
            (6000.01, 10000.00, 639.80),
            (10000.01, 20000.00, 885.32),
            (20000.01, 30000.00, 1376.41),
            (30000.01, 40000.00, 1785.65),
            (40000.01, 60000.00, 2194.88),
            (60000.01, 80000.00, 2669.59),
            (80000.01, 100000.00, 2945.81),
        ]
        for faixa_min, faixa_max, valor in faixas_to:
            if custo_obra >= faixa_min and custo_obra <= faixa_max:
                return valor
        if custo_obra > 100000.00:
            excedente = custo_obra - 100000.00
            acrescimos = math.floor(excedente / 50000.00)
            valor = 2945.81 + acrescimos * 143.12
            return min(valor, 15252.57)
        return 'Consultar cartório'
    # PB: progressivo
    if estado == 'PB':
        faixas_pb = [
            (0, 16865.00, 141.67),
            (16865.01, 33730.00, 354.17),
            (33730.01, 47222.00, 566.66),
            (47222.01, 67460.00, 809.52),
        ]
        for faixa_min, faixa_max, valor in faixas_pb:
            if custo_obra >= faixa_min and custo_obra <= faixa_max:
                return valor
        if custo_obra > 67460.00:
            excedente = custo_obra - 67460.00
            acrescimos = math.ceil(excedente / 6746.00)
            valor_averbacao = 809.52 + (acrescimos * 60.71)
            return min(valor_averbacao, 10119.00)
        return 809.52
    averbacao_faixas = averbacao_por_estado_faixa.get(estado, [])
    for faixa_min, faixa_max, valor in averbacao_faixas:
        if custo_obra >= faixa_min and custo_obra <= faixa_max:
            return valor
    return 'Consultar cartório'
if __name__ == '__main__':
    app.run(debug=True)