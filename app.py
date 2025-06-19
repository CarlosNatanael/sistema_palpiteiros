from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import re
from datetime import datetime
from functools import wraps

API_BASE_URL = "http://apifutebol.footstats.com.br/3.1"
API_TOKEN = "Bearer_client_token"

app = Flask(__name__)
app.secret_key = 'ALJDHA76797#%*#JKOL'

# --- Configurações de Administrador ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "pokemar16#" 

def get_db_connection():
    conn = sqlite3.connect('palpites.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS pontuacao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        posicao INTEGER,
        nome TEXT UNIQUE,
        pontos INTEGER DEFAULT 0,
        acertos INTEGER DEFAULT 0,
        erros INTEGER DEFAULT 0
    )''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS palpites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        rodada INTEGER,
        game_id INTEGER,
        time1 TEXT,
        time2 TEXT,
        gol_time1 INTEGER,
        gol_time2 INTEGER,
        resultado TEXT,
        status TEXT
    )''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS jogos (
        id INTEGER PRIMARY KEY,
        rodada INTEGER,
        time1_nome TEXT,
        time1_img TEXT,
        time1_sigla TEXT,
        time2_nome TEXT,
        time2_img TEXT,
        time2_sigla TEXT,
        data_hora TEXT,
        local TEXT,
        placar_time1 INTEGER,
        placar_time2 INTEGER,
        status TEXT DEFAULT 'Pendente'
    )''')

    # TABELA PARA PALPITE CAMPEÃO
    conn.execute('''
    CREATE TABLE IF NOT EXISTS palpite_campeao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE,
        time_campeao TEXT,
        time_campeao_img TEXT,
        rodada INTEGER,
        data_palpite TEXT
    )''')

    # TABELA PARA O CAMPEÃO REAL DO MUNDIAL (Definido pelo Admin)
    conn.execute('''
    CREATE TABLE IF NOT EXISTS campeao_mundial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time_campeao TEXT,
        time_campeao_img TEXT,
        data_definicao TEXT UNIQUE
    )''')

    conn.commit()
    conn.close()

init_db()

# Filtro Jinja2 para formatar datas no template
@app.template_filter('format_date_br')
def format_date_br_filter(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str.split(' ')[0], '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            return date_str
    return ""

# Função auxiliar para extrair nomes e URLs de imagens dos times (para o palpite campeão)
def get_all_teams_for_champion_bet():
    teams = []
    # Usaremos o conteúdo do Imagems times.txt para popular a lista de times nos selects
    # Conteúdo de Imagems times.txt (copiado de uma de suas mensagens anteriores)
    team_data = """
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/nIdbR6qIUDyZUBO9vojSPw_48x48.png" alt="Bahia"> Bahia >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/tCMSqgXVHROpdCpQhzTo1g_48x48.png" alt="Corinthians"> Corinthians >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/u_L7Mkp33uNmFTv3uUlXeQ_48x48.png" alt="Criciúma"> Criciúma >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/hHwT8LwRmYCAGxQ-STLxYA_48x48.png" alt="Vasco"> Vasco >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/9mqMGndwoR9og_Z0uEl2kw_48x48.png" alt="Atlético-GO"> Atlético-GO >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/Ku-73v_TW9kpex-IEGb0ZA_48x48.png" alt="Grêmio"> Grêmio >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/4w2Z97Hf9CSOqICK3a8AxQ_48x48.png" alt="São Paulo"> São Paulo >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png" alt="Flamengo"> Flamengo >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/OWVFKuHrQuf4q2Wk0hEmSA_48x48.png" alt="Internacional"> Internacional >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/9LkdBR4L5plovKM8eIy7nQ_48x48.png" alt="Atlético-PR"> Atlético-PR >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/fCMxMMDF2AZPU7LzYKSlig_48x48.png" alt="Fluminense"> Fluminense >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/LHSM6VchpkI4NIptoSTHOg_48x48.png" alt="Vitória"> Vitória >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/me10ephzRxdj45zVq1Risg_48x48.png" alt="Fortaleza"> Fortaleza >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/q9fhEsgpuyRq58OgmSndcQ_48x48.png" alt="Atlético-MG"> Atlético-MG >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png" alt="Botafogo"> Botafogo >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/JrXw-m4Dov0gE2Sh6XJQMQ_48x48.png" alt="Juventude"> Juventude >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png" alt="Palmeiras"> Palmeiras >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/Tcv9X__nIh-6wFNJPMwIXQ_48x48.png" alt="Cruzeiro"> Cruzeiro >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/j6U8Rgt_6yyf0Egs9nREXw_48x48.png" alt="Cuiabá"> Cuiabá >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/lMyw2zn1Z4cdkaxKJWnsQw_48x48.png" alt="Bragantino"> Bragantino >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png" alt="Palmeiras"> Palmeiras >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png" alt="Flamengo"> Flamengo >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/fCMxMMDF2AZPU7LzYKSlig_48x48.png" alt="Fluminense"> Fluminense >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png" alt="Botafogo"> Botafogo >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/-_cmntP5q_pHL7g5LfkRiw_96x96.png" alt="Bayern"> Bayern >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/ydlyVc6hUPBXoaT3wR_lFg_96x96.png" alt="Auckland City"> Auckland City >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/JdNbaaw7JlDHvPHZaX2V2A_48x48.png" alt="Al Ahly"> Al Ahly >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/dn0bMtTbbpx7v3Ieq6TZtQ_48x48.png" alt="Inter Miami"> Inter Miami >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/QkkllEKwkj60jEVtOEZWAg_48x48.png" alt="Porto"> Porto >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/pEqmA7CL-VRo4Llq3rwIPA_48x48.png" alt="Atlético Madrid"> Atlético Madrid >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/mcpMspef1hwHwi9qrfp4YQ_48x48.png" alt="PSG"> PSG >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/k6m3hoy4Rn3KRrMYSYDjog_48x48.png" alt="Seattle Sounders"> Seattle Sounders >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/nFwABZ-4n_A3BGXT9A7Adg_48x48.png" alt="Benfica"> Benfica >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/YO1impuFJT2hex6wvCd9Pw_48x48.png" alt="Boca Juniors"> Boca Juniors >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/fhBITrIlbQxhVB6IjxUO6Q_48x48.png" alt="Chelsea"> Chelsea >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/Kf32x8gh5SCMEqvKjVGLfg_48x48.png" alt="Espérance"> Espérance >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/waD0z1CWx6_r4UT_hgb7nA_96x96.png" alt="LAFC"> LAFC >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/l2-icwsMhIvsbRw8AwC1yg_48x48.png" alt="Inter"> Inter >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/LXZ8fEgzf0_FwSyq15buPw_48x48.png" alt="Monterrey"> Monterrey >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/700Mj6lUNkbBdvOVEbjC3g_48x48.png" alt="River Plate"> River Plate >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/F-09rxdgECid61-Rj8Uxrw_48x48.png" alt="Urawa Reds"> Urawa Reds >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/FZnTSH2rbHFos4BnlWAItw_48x48.png" alt="Borussia"> Borussia >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/Lmp8fUABWWKRwNrHf71m5w_48x48.png" alt="Sundowns"> Sundowns >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/-K1h8OOTItUmjKqR2g5Nnw_48x48.png" alt="Ulsan Hyundai"> Ulsan Hyundai >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/vA9sLyDeHX3q7pn8QTmoeQ_48x48.png" alt="Al Ain"> Al Ain >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/6lal-0xwWtos5HI99HRvuQ_48x48.png" alt="Juventus"> Juventus >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/z44l-a0W1v5FmgPnemV6Xw_48x48.png" alt="City"> City >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/JxwBeJ9HrjZX_vRqTPwY6A_48x48.png" alt="Wydad AC"> Wydad AC >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/HGVsnyWvMiGVotxhgicdSQ_48x48.png" alt="Al-Hilal"> Al-Hilal >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/9dscoX8iYhzbjSNxXVp2gQ_48x48.png" alt="Pachuca"> Pachuca >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/Th4fAVAZeCJWRcKoLW7koA_48x48.png" alt="Real Madrid"> Real Madrid >
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/vQhr4NoE_4Yg1IhUZvbRNw_48x48.png" alt="RB Salzburg"> RB Salzburg >
    """
    teams = []
    pattern = r'<img src="(.*?)" alt="(.*?)">\s*([^<\n]*?)\s*>'
    matches = re.findall(pattern, team_data)

    for match in matches:
        img_src = match[0]
        alt_text = match[1]
        team_name_from_text = match[2].strip()

        if team_name_from_text and team_name_from_text != alt_text:
            team_name = team_name_from_text
        else:
            team_name = alt_text

        if team_name.endswith('>'):
            team_name = team_name[:-1].strip()

        teams.append({'name': team_name, 'img_src': img_src})
    return teams

# Simulação de jogos do Mundial por rodada
MUNDIAL_JOGOS_POR_RODADA = {
    1: [
        {
            'id': 101,
            'time1_nome': 'Inter Miami','time1_sigla': 'INT','time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/dn0bMtTbbpx7v3Ieq6TZtQ_48x48.png',
            'time2_nome': 'Al Ahly','time2_sigla': 'ALA','time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/JdNbaaw7JlDHvPHZaX2V2A_48x48.png',
            'data_hora': '2025-06-14 21:00',
            'local': 'Hard Rock Stadium'
        },
        {
            'id': 102,
            'time1_nome': 'Palmeiras',
            'time1_sigla': 'PAL',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png',
            'time2_nome': 'Porto',
            'time2_sigla': 'POR',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/QkkllEKwkj60jEVtOEZWAg_48x48.png',
            'data_hora': '2025-05-15 19:00',
            'local': 'MetLife Stadium'
        },
        {
            'id': 103,
            'time1_nome': 'PSG',
            'time1_sigla': 'PSG',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/mcpMspef1hwHwi9qrfp4YQ_48x48.png',
            'time2_nome': 'Atlético Madrid',
            'time2_sigla': 'ATM',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/pEqmA7CL-VRo4Llq3rwIPA_48x48.png',
            'data_hora': '2025-05-15 16:00',
            'local': 'Rose Bowl'
        },
        {
            'id': 104,
            'time1_nome': 'Botafogo',
            'time1_sigla': 'BOT',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png',
            'time2_nome': 'Seattle Sounders',
            'time2_sigla': 'SES',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/k6m3hoy4Rn3KRrMYSYDjog_48x48.png',
            'data_hora': '2025-05-15 23:00',
            'local': 'Lumen Field'
        },
        {
            'id': 105,
            'time1_nome': 'Bayern',
            'time1_sigla': 'BAY',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/-_cmntP5q_pHL7g5LfkRiw_96x96.png',
            'time2_nome': 'Auckland City',
            'time2_sigla': 'ACC',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/ydlyVc6hUPBXoaT3wR_lFg_96x96.png',
            'data_hora': '2025-05-15 13:00',
            'local': 'TQL Stadium'
        },
        {
            'id': 106,
            'time1_nome': 'Boca Juniors',
            'time1_sigla': 'BOC',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/YO1impuFJT2hex6wvCd9Pw_48x48.png',
            'time2_nome': 'Benfica',
            'time2_sigla': 'BEN',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/nFwABZ-4n_A3BGXT9A7Adg_48x48.png',
            'data_hora': '2025-06-16 19:00',
            'local': 'Hard Rock Stadium'
        },
        {
            'id': 107,
            'time1_nome': 'Chelsea',
            'time1_sigla': 'CFC',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/fhBITrIlbQxhVB6IjxUO6Q_48x48.png',
            'time2_nome': 'LAFC',
            'time2_sigla': 'LOS',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/waD0z1CWx6_r4UT_hgb7nA_96x96.png',
            'data_hora': '2025-06-16 16:00',
            'local': 'Mercedes-Benz Stadium'
        },
        {
            'id': 108,
            'time1_nome': 'Flamengo',
            'time1_sigla': 'FLA',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png',
            'time2_nome': 'Espérance',
            'time2_sigla': 'EST',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/Kf32x8gh5SCMEqvKjVGLfg_48x48.png',
            'data_hora': '2025-06-16 22:00',
            'local': 'Lincoln Financial Field'
        },
        {
            'id': 109,
            'time1_nome': 'River Plate',
            'time1_sigla': 'RIV',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/700Mj6lUNkbBdvOVEbjC3g_48x48.png',
            'time2_nome': 'Urawa Reds',
            'time2_sigla': 'URD',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/F-09rxdgECid61-Rj8Uxrw_48x48.png',
            'data_hora': '2025-06-17 16:00',
            'local': 'Lumen Field'
        },
        {
            'id': 110,
            'time1_nome': 'Monterrey',
            'time1_sigla': 'MTR',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/LXZ8fEgzf0_FwSyq15buPw_48x48.png',
            'time2_nome': 'Inter',
            'time2_sigla': 'INT',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/l2-icwsMhIvsbRw8AwC1yg_48x48.png',
            'data_hora': '2025-06-17 22:00',
            'local': 'Rose Bowl'
        },
        {
            'id': 111,
            'time1_nome': 'Fluminense',
            'time1_sigla': 'FLU',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/fCMxMMDF2AZPU7LzYKSlig_48x48.png',
            'time2_nome': 'Borussia',
            'time2_sigla': 'BVB',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/FZnTSH2rbHFos4BnlWAItw_48x48.png',
            'data_hora': '2025-06-17 13:00',
            'local': 'MetLife Stadium'
        },
        {
            'id': 112,
            'time1_nome': 'Ulsan Hyundai',
            'time1_sigla': 'ULH',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/-K1h8OOTItUmjKqR2g5Nnw_48x48.png',
            'time2_nome': 'Sundowns',
            'time2_sigla': 'MSW',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/Lmp8fUABWWKRwNrHf71m5w_48x48.png',
            'data_hora': '2025-06-17 19:00',
            'local': 'Inter Miami CF Stadium'
        },
        {
            'id': 113,
            'time1_nome': 'City',
            'time1_sigla': 'MNC',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/z44l-a0W1v5FmgPnemV6Xw_48x48.png',
            'time2_nome': 'Wydad AC',
            'time2_sigla': 'WYD',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/JxwBeJ9HrjZX_vRqTPwY6A_48x48.png',
            'data_hora': '2025-06-18 13:00',
            'local': 'Lincoln Financial Field'
        },
        {
            'id': 114,
            'time1_nome': 'Al Ain',
            'time1_sigla': 'AIN',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/vA9sLyDeHX3q7pn8QTmoeQ_48x48.png',
            'time2_nome': 'Juventus',
            'time2_sigla': 'JUV',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/6lal-0xwWtos5HI99HRvuQ_48x48.png',
            'data_hora': '2025-06-18 22:00',
            'local': 'Audi Field'
        },
        {
            'id': 115,
            'time1_nome': 'Real Madrid',
            'time1_sigla': 'RMA',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/Th4fAVAZeCJWRcKoLW7koA_48x48.png',
            'time2_nome': 'Al-Hilal',
            'time2_sigla': 'HIL',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/HGVsnyWvMiGVotxhgicdSQ_48x48.png',
            'data_hora': '2025-06-18 16:00',
            'local': 'Hard Rock Stadium'
        },
        {
            'id': 116,
            'time1_nome': 'Pachuca',
            'time1_sigla': 'PCH',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/9dscoX8iYhzbjSNxXVp2gQ_48x48.png',
            'time2_nome': 'RB Salzburg',
            'time2_sigla': 'SLZ',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/vQhr4NoE_4Yg1IhUZvbRNw_48x48.png',
            'data_hora': '2025-06-18 19:00',
            'local': 'TQL Stadium'
        },
    ],
    2: [
        {
            'id': 201,
            'time1_nome': 'Palmeiras',
            'time1_sigla': 'PAL',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png',
            'time2_nome': 'Al Ahly',
            'time2_sigla': 'ALA',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/JdNbaaw7JlDHvPHZaX2V2A_48x48.png',
            'data_hora': '2025-06-19 13:00',
            'local': 'MetLife Stadium'
        },
        {
            'id': 202,
            'time1_nome': 'Inter Miami',
            'time1_sigla': 'INT',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/dn0bMtTbbpx7v3Ieq6TZtQ_48x48.png',
            'time2_nome': 'Porto',
            'time2_sigla': 'POT',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/QkkllEKwkj60jEVtOEZWAg_48x48.png',
            'data_hora': '2025-06-19 16:00',
            'local': 'Mercedes-Benz Stadium'
        },
        {
            'id': 203,
            'time1_nome': 'Seattle Sounders',
            'time1_sigla': 'SES',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/k6m3hoy4Rn3KRrMYSYDjog_48x48.png',
            'time2_nome': 'Atlético de Madrid',
            'time2_sigla': 'ATM',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/pEqmA7CL-VRo4Llq3rwIPA_48x48.png',
            'data_hora': '2025-06-19 19:00',
            'local': 'Lumen Field'
        },
        {
            'id': 204,
            'time1_nome': 'Botafogo',
            'time1_sigla': 'BOT',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png',
            'time2_nome': 'PSG',
            'time2_sigla': 'PSG',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/mcpMspef1hwHwi9qrfp4YQ_48x48.png',
            'data_hora': '2025-06-19 22:00',
            'local': 'Rose Bowl'
        },
        {
            'id': 205,
            'time1_nome': 'Benfica',
            'time1_sigla': 'BEN',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/nFwABZ-4n_A3BGXT9A7Adg_48x48.png',
            'time2_nome': 'Auckland City',
            'time2_sigla': 'ACC',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/ydlyVc6hUPBXoaT3wR_lFg_96x96.png',
            'data_hora': '2025-06-20 13:00',
            'local': 'Inter Miami CF Stadium'
        },
        {
            'id': 206,
            'time1_nome': 'Flamengo',
            'time1_sigla': 'FLA',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png',
            'time2_nome': 'Chelsea',
            'time2_sigla': 'CFC',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/fhBITrIlbQxhVB6IjxUO6Q_48x48.png',
            'data_hora': '2025-06-20 15:00',
            'local': 'Lincoln Financial Field'
        },
        {
            'id': 207,
            'time1_nome': 'LAFC',
            'time1_sigla': 'LOS',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/waD0z1CWx6_r4UT_hgb7nA_96x96.png',
            'time2_nome': 'Espérance',
            'time2_sigla': 'EST',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/Kf32x8gh5SCMEqvKjVGLfg_48x48.png',
            'data_hora': '2025-06-20 19:00',
            'local': 'Geodis Park'
        },
        {
            'id': 208,
            'time1_nome': 'Bayern',
            'time1_sigla': 'BAY',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/-_cmntP5q_pHL7g5LfkRiw_96x96.png',
            'time2_nome': 'Boca Juniors',
            'time2_sigla': 'BOC',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/YO1impuFJT2hex6wvCd9Pw_48x48.png',
            'data_hora': '2025-06-20 22:00',
            'local': 'Hard Rock Stadium'
        },
        {
            'id': 209,
            'time1_nome': 'Sundowns',
            'time1_sigla': 'MSM',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/Lmp8fUABWWKRwNrHf71m5w_48x48.png',
            'time2_nome': 'Borussia',
            'time2_sigla': 'BVB',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/FZnTSH2rbHFos4BnlWAItw_48x48.png',
            'data_hora': '2025-06-21 13:00',
            'local': 'TQL Stadium'
        },
        {
            'id': 210,
            'time1_nome': 'Inter',
            'time1_sigla': 'INT',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/l2-icwsMhIvsbRw8AwC1yg_48x48.png',
            'time2_nome': 'Urawa Reds',
            'time2_sigla': 'URD',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/F-09rxdgECid61-Rj8Uxrw_48x48.png',
            'data_hora': '2025-06-21 16:00',
            'local': 'Lumen Field'
        },
        {
            'id': 211,
            'time1_nome': 'Fluminense',
            'time1_sigla': 'FLU',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/fCMxMMDF2AZPU7LzYKSlig_48x48.png',
            'time2_nome': 'Ulsan Hyundai',
            'time2_sigla': 'ULH',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/-K1h8OOTItUmjKqR2g5Nnw_48x48.png',
            'data_hora': '2025-06-21 19:00',
            'local': 'MetLife Stadium'
        },
        {
            'id': 212,
            'time1_nome': 'River Plate',
            'time1_sigla': 'RIV',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/700Mj6lUNkbBdvOVEbjC3g_48x48.png',
            'time2_nome': 'Monterrey',
            'time2_sigla': 'MTR',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/LXZ8fEgzf0_FwSyq15buPw_48x48.png',
            'data_hora': '2025-06-21 22:00',
            'local': 'Rose Bowl'
        },
        {
            'id': 213,
            'time1_nome': 'Juventus',
            'time1_sigla': 'JUV',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/6lal-0xwWtos5HI99HRvuQ_48x48.png',
            'time2_nome': 'Wydad AC',
            'time2_sigla': 'WYD',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/JxwBeJ9HrjZX_vRqTPwY6A_48x48.png',
            'data_hora': '2025-06-22 13:00',
            'local': 'Lincoln Financial Field'
        },
        {
            'id': 214,
            'time1_nome': 'Real Madrid',
            'time1_sigla': 'RMA',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/Th4fAVAZeCJWRcKoLW7koA_48x48.png',
            'time2_nome': 'Pachuca',
            'time2_sigla': 'PCH',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/9dscoX8iYhzbjSNxXVp2gQ_48x48.png',
            'data_hora': '2025-06-22 16:00',
            'local': 'Bank of America Stadium'
        },
        {
            'id': 215,
            'time1_nome': 'Al Hilal',
            'time1_sigla': 'HIL',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/HGVsnyWvMiGVotxhgicdSQ_48x48.png',
            'time2_nome': 'Salzburg',
            'time2_sigla': 'SLZ',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/vQhr4NoE_4Yg1IhUZvbRNw_48x48.png',
            'data_hora': '2025-06-22 19:00',
            'local': 'Audi Field'
        },
        {
            'id': 216,
            'time1_nome': 'City',
            'time1_sigla': 'MNC',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/z44l-a0W1v5FmgPnemV6Xw_48x48.png',
            'time2_nome': 'Al Ain',
            'time2_sigla': 'AIN',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/vA9sLyDeHX3q7pn8QTmoeQ_48x48.png',
            'data_hora': '2025-06-22 22:00',
            'local': 'Mercedes-Benz Stadium'
        },
    ],
    # Adicione mais rodadas e jogos conforme necessário, seguindo a estrutura
    # Certifique-se de que os IDs dos jogos são únicos em todo o dicionário
}

@app.route('/')
def index():
    conn = get_db_connection()
    pontuacao = conn.execute("SELECT * FROM pontuacao ORDER BY pontos DESC, acertos DESC, erros ASC").fetchall()
    
    agora = datetime.now()
    rodada_param = request.args.get('rodada', type=int)
    
    # Obter todas as rodadas disponíveis
    rodadas_disponiveis = sorted([r['rodada'] for r in conn.execute("SELECT DISTINCT rodada FROM jogos ORDER BY rodada").fetchall()])
    
    # Determinar a rodada ativa
    if rodada_param and rodada_param in rodadas_disponiveis:
        rodada_ativa = rodada_param
    else:
        # Se não houver rodadas, define um padrão para evitar erro
        rodada_ativa = rodadas_disponiveis[-1] if rodadas_disponiveis else 1
    
    # Verificar se há próxima/anterior rodada
    rodada_index = rodadas_disponiveis.index(rodada_ativa) if rodada_ativa in rodadas_disponiveis else -1
    tem_proxima = rodada_index != -1 and rodada_index < len(rodadas_disponiveis) - 1
    tem_anterior = rodada_index > 0
    
    # Filtrar jogos para a rodada ativa
    agora_str = agora.strftime('%Y-%m-%d %H:%M')
    
    jogos_futuros = conn.execute(
        "SELECT id, rodada, time1_nome, time1_img, time1_sigla, time2_nome, time2_img, time2_sigla, data_hora, local, placar_time1, placar_time2 FROM jogos WHERE rodada = ? AND data_hora > ? ORDER BY data_hora ASC",
        (rodada_ativa, agora_str)
    ).fetchall()
    
    jogos_passados = conn.execute(
        "SELECT id, rodada, time1_nome, time1_img, time1_sigla, time2_nome, time2_img, time2_sigla, data_hora, local, placar_time1, placar_time2, status FROM jogos WHERE rodada = ? AND data_hora <= ? ORDER BY data_hora DESC",
        (rodada_ativa, agora_str)
    ).fetchall()
    
    conn.close()
    
    return render_template('index.html', 
        pontuacao=pontuacao,
        rodada_ativa=rodada_ativa,
        jogos_futuros=jogos_futuros,
        jogos_passados=jogos_passados,
        rodadas_disponiveis=rodadas_disponiveis,
        tem_proxima=tem_proxima,
        tem_anterior=tem_anterior,
        proxima_rodada=rodadas_disponiveis[rodada_index + 1] if tem_proxima else None,
        anterior_rodada=rodadas_disponiveis[rodada_index - 1] if tem_anterior else None
    )

@app.route('/palpites')
def exibir_palpites():
    conn = get_db_connection()
    
    # Adicionando um parâmetro de rodada opcional para exibir palpites de rodadas específicas
    rodada_param = request.args.get('rodada', type=int)

    # Lógica para determinar a rodada ativa (se nenhuma for especificada)
    rodada_para_exibir = None
    if rodada_param: # Se uma rodada específica for solicitada na URL
        rodada_para_exibir = rodada_param
    else: # Se nenhuma rodada for especificada, determina a rodada ativa
        agora = datetime.now()
        rodadas_no_db = conn.execute("SELECT DISTINCT rodada FROM jogos ORDER BY rodada ASC").fetchall()
        
        rodada_ativa = None
        for row in rodadas_no_db:
            num_rodada = row['rodada']
            ultimo_jogo_da_rodada = conn.execute(
                "SELECT data_hora FROM jogos WHERE rodada = ? ORDER BY data_hora DESC LIMIT 1", (num_rodada,)
            ).fetchone()
            
            if ultimo_jogo_da_rodada:
                ultimo_jogo_datetime = datetime.strptime(ultimo_jogo_da_rodada['data_hora'], '%Y-%m-%d %H:%M')
                if agora < ultimo_jogo_datetime:
                    rodada_ativa = num_rodada
                    break
        
        if rodada_ativa is None:
            if rodadas_no_db:
                rodada_ativa = rodadas_no_db[-1]['rodada']
            else:
                rodada_ativa = 1 # Padrão para Rodada 1 se não houver rodadas no DB
        rodada_para_exibir = rodada_ativa # Define a rodada a ser exibida

    # Agora, buscar os palpites para a rodada determinada
    palpites = conn.execute("SELECT * FROM palpites WHERE rodada = ? ORDER BY nome", (rodada_para_exibir,)).fetchall()

    palpites_agrupados = {}
    for palpite in palpites:
        nome = palpite['nome']
        if nome not in palpites_agrupados:
            palpites_agrupados[nome] = []
        palpites_agrupados[nome].append(palpite)

    # Obter todas as rodadas existentes para a navegação de próxima/anterior e links
    rodadas_existentes = sorted([r['rodada'] for r in conn.execute("SELECT DISTINCT rodada FROM jogos ORDER BY rodada ASC").fetchall()])
    
    idx_rodada = rodadas_existentes.index(rodada_para_exibir) if rodada_para_exibir in rodadas_existentes else -1
    
    tem_proxima = False
    proxima_rodada = None
    if idx_rodada != -1 and idx_rodada < len(rodadas_existentes) - 1:
        tem_proxima = True
        proxima_rodada = rodadas_existentes[idx_rodada + 1]

    tem_anterior = False
    anterior_rodada = None
    if idx_rodada > 0:
        tem_anterior = True
        anterior_rodada = rodadas_existentes[idx_rodada - 1]

    conn.close() # Mover conn.close() para o final da função

    return render_template(
        'palpites.html',
        palpites_agrupados=palpites_agrupados,
        rodada_exibida_num=rodada_para_exibir,
        tem_proxima=tem_proxima,
        proxima_rodada=proxima_rodada,
        tem_anterior=tem_anterior,
        anterior_rodada=anterior_rodada,
        rodadas_disponiveis=rodadas_existentes # Para o Navbar, se necessário
    )

@app.route('/adicionar_palpites', methods=['GET', 'POST'])
def adicionar_palpites():
    conn = get_db_connection() # Conexão movida para o início da função
    cursor = conn.cursor() # Cursor também

    if request.method == 'POST':
        nome = request.form['nome']
        rodada_selecionada = int(request.form['rodada_selecionada'])

        try:
            cursor.execute("INSERT INTO pontuacao (nome, pontos, acertos, erros, posicao) VALUES (?, ?, ?, ?, ?)", (nome, 0, 0, 0, 99))
            conn.commit()
        except sqlite3.IntegrityError:
            pass

        agora_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        jogos_da_rodada_para_palpite = conn.execute(
            "SELECT id, time1_nome, time2_nome, data_hora FROM jogos WHERE rodada = ? AND data_hora > ?",
            (rodada_selecionada, agora_str)
        ).fetchall()

        for jogo in jogos_da_rodada_para_palpite:
            game_id = jogo['id']
            time1 = jogo['time1_nome']
            time2 = jogo['time2_nome']

            gol_time1 = request.form.get(f'gol_time1_{game_id}')
            gol_time2 = request.form.get(f'gol_time2_{game_id}')
            resultado_palpite = request.form.get(f'resultado_{game_id}')

            if gol_time1 is not None and gol_time2 is not None:
                gol_time1 = int(gol_time1)
                gol_time2 = int(gol_time2)

                existing_palpite = cursor.execute(
                    "SELECT id FROM palpites WHERE nome = ? AND game_id = ?",
                    (nome, game_id)
                ).fetchone()

                if existing_palpite:
                    cursor.execute(
                        "UPDATE palpites SET gol_time1 = ?, gol_time2 = ?, resultado = ?, status = ? WHERE id = ?",
                        (gol_time1, gol_time2, resultado_palpite, 'Pendente', existing_palpite['id'])
                    )
                else:
                    cursor.execute(
                        "INSERT INTO palpites (nome, rodada, game_id, time1, time2, gol_time1, gol_time2, resultado, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (nome, rodada_selecionada, game_id, time1, time2, gol_time1, gol_time2, resultado_palpite, 'Pendente')
                    )
        conn.commit()
        conn.close()
        flash('Seus palpites foram registrados com sucesso!', 'success')
        return redirect(url_for('exibir_palpites'))

    # GET request: exibir o formulário para adicionar palpites
    rodadas_disponiveis = sorted(MUNDIAL_JOGOS_POR_RODADA.keys())

    rodada_param = request.args.get('rodada', type=int)
    rodada_atual = rodada_param if rodada_param in rodadas_disponiveis else (rodadas_disponiveis[0] if rodadas_disponiveis else None)

    agora_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    jogos_da_rodada_selecionada = conn.execute(
        "SELECT id, time1_nome, time1_img, time1_sigla, time2_nome, time2_img, time2_sigla, data_hora, local FROM jogos WHERE rodada = ? AND data_hora > ?",
        (rodada_atual, agora_str)
    ).fetchall()
    
    palpiteiros = ["Ariel", "Carlos", "Celso", "Gabriel", "Lucas"]
    conn.close()

    return render_template(
        'adicionar_palpites.html',
        rodadas=rodadas_disponiveis,
        rodada_selecionada=rodada_atual,
        jogos=jogos_da_rodada_selecionada,
        palpiteiros=palpiteiros
    )

@app.route('/estatisticas')
def estatisticas():
    conn = get_db_connection()
    maior_pontuador = conn.execute("SELECT nome, pontos FROM pontuacao ORDER BY pontos DESC LIMIT 1").fetchone()
    quem_acertou_mais = conn.execute("SELECT nome, acertos FROM pontuacao ORDER BY acertos DESC LIMIT 1").fetchone()
    conn.close()
    return render_template('estatisticas.html', maior_pontuador=maior_pontuador, quem_acertou_mais=quem_acertou_mais)

@app.route('/regras')
def regra():
    return render_template('regras.html')

@app.route('/rodadas')
def exibir_rodadas():
     rodadas = [f"Rodada {i}" for i in sorted(MUNDIAL_JOGOS_POR_RODADA.keys())]
     return render_template('rodadas.html', rodadas=rodadas)

@app.route('/rodada/<int:numero>')
def exibir_rodada(numero):
    conn = get_db_connection()
    palpites = conn.execute("SELECT * FROM palpites WHERE rodada = ?", (numero,)).fetchall()

    jogos_da_rodada = conn.execute(
        "SELECT id, time1_nome, time1_img, time1_sigla, time2_nome, time2_img, time2_sigla, data_hora, local, placar_time1, placar_time2 FROM jogos WHERE rodada = ? ORDER BY data_hora",
        (numero,)
    ).fetchall()
    conn.close()

    palpites_agrupados = {}
    for palpite in palpites:
        nome = palpite['nome']
        if nome not in palpites_agrupados:
            palpites_agrupados[nome] = []
        palpites_agrupados[nome].append({
            'time1': palpite['time1'],
            'gol_time1': palpite['gol_time1'],
            'time2': palpite['time2'],
            'gol_time2': palpite['gol_time2'],
            'resultado': palpite['resultado'],
            'status': palpite['status']
        })

    return render_template('rodada.html', rodada=numero, palpites_agrupados=palpites_agrupados, jogos_da_rodada=jogos_da_rodada)

# Decorator para exigir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard')) # Redirecionar para um dashboard admin
        else:
            flash('Nome de usuário ou senha incorretos.', 'danger')
    return render_template('login.html')

# Rota de Logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

# Dashboard do Administrador (Nova Rota)
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html') # Você precisará criar este template

# Rota de Administração para definir resultados dos jogos (PROTEGIDA)
@app.route('/admin/set_game_result', methods=['GET', 'POST'])
@login_required # Protege esta rota
def set_game_result():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        if request.form.get('password') != ADMIN_PASSWORD:
            flash('Senha incorreta!', 'danger')
            conn.close()
            return redirect(url_for('set_game_result'))

        game_id = request.form.get('game_id', type=int)
        placar_time1 = request.form.get('placar_time1', type=int)
        placar_time2 = request.form.get('placar_time2', type=int)

        try:
            # ALTERAÇÃO: Atualiza o placar e define o status como 'Ao Vivo'
            cursor.execute(
                "UPDATE jogos SET placar_time1 = ?, placar_time2 = ?, status = 'Ao Vivo' WHERE id = ?",
                (placar_time1, placar_time2, game_id)
            )
            conn.commit()
            if cursor.rowcount == 0:
                flash(f'Jogo com ID {game_id} não encontrado.', 'warning')
            else:
                flash(f'Placar ao vivo do jogo ID {game_id} atualizado para {placar_time1}x{placar_time2}!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao atualizar o placar ao vivo: {e}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('set_game_result'))

    # GET request: exibe o formulário
    jogos_disponiveis = conn.execute("SELECT id, time1_nome, time2_nome, data_hora, placar_time1, placar_time2 FROM jogos ORDER BY data_hora").fetchall()
    conn.close()

    return render_template('set_game_result.html', jogos_disponiveis=jogos_disponiveis)


@app.route('/atualizar_pontuacao_admin')
@login_required # Protege esta rota
def atualizar_pontuacao_admin():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE pontuacao SET pontos = 0, acertos = 0, erros = 0")

    # ALTERAÇÃO: Pega apenas jogos com placar definido para calcular pontos
    jogos_com_resultados = conn.execute("SELECT id, placar_time1, placar_time2 FROM jogos WHERE placar_time1 IS NOT NULL AND placar_time2 IS NOT NULL").fetchall()
    resultados_reais_map = {jogo['id']: (jogo['placar_time1'], jogo['placar_time2']) for jogo in jogos_com_resultados}

    cursor.execute("SELECT * FROM palpites")
    palpites = cursor.fetchall()

    for palpite in palpites:
        nome = palpite['nome']
        game_id = palpite['game_id']
        gol_time1 = palpite['gol_time1']
        gol_time2 = palpite['gol_time2']
        palpite_resultado_texto = palpite['resultado']
        palpite_id = palpite['id']

        resultado_real = resultados_reais_map.get(game_id)
        if resultado_real:
            gol_real_time1, gol_real_time2 = resultado_real

            pontos_ganhos = 0
            status_palpite = "Erro (0 pts)"

            if gol_real_time1 > gol_real_time2:
                real_resultado_texto = 'Vitória (Casa)'
            elif gol_real_time1 < gol_real_time2:
                real_resultado_texto = 'Vitória (Fora)'
            else:
                real_resultado_texto = 'Empate'

            if gol_time1 == gol_real_time1 and gol_time2 == gol_real_time2:
                if palpite_resultado_texto == real_resultado_texto:
                    pontos_ganhos = 4
                    status_palpite = "Acerto Total (4 pts)"
                else:
                    pontos_ganhos = 2
                    status_palpite = "Acerto Placar (2 pts)"
                cursor.execute("UPDATE pontuacao SET acertos = acertos + 1 WHERE nome = ?", (nome,))
            else:
                if palpite_resultado_texto == real_resultado_texto:
                    pontos_ganhos = 1
                    status_palpite = "Acerto Resultado (1 pts)"
                    cursor.execute("UPDATE pontuacao SET acertos = acertos + 1 WHERE nome = ?", (nome,))
                else:
                    cursor.execute("UPDATE pontuacao SET erros = erros + 1 WHERE nome = ?", (nome,))
                    status_palpite = "Erro (0 pts)"

            cursor.execute("UPDATE pontuacao SET pontos = pontos + ? WHERE nome = ?", (pontos_ganhos, nome))
            cursor.execute("UPDATE palpites SET status = ? WHERE id = ?", (status_palpite, palpite_id))
        else:
            status_palpite = "Pendente"
            cursor.execute("UPDATE palpites SET status = ? WHERE id = ?", (status_palpite, palpite_id))
    
    # ALTERAÇÃO: Após calcular os pontos, atualiza o status dos jogos processados para 'Finalizado'
    if resultados_reais_map:
        placeholders = ','.join('?' for _ in resultados_reais_map.keys())
        cursor.execute(f"UPDATE jogos SET status = 'Finalizado' WHERE id IN ({placeholders})", list(resultados_reais_map.keys()))


    pontuacao_atualizada = conn.execute("SELECT nome, pontos FROM pontuacao ORDER BY pontos DESC, acertos DESC, erros ASC").fetchall()
    for i, jogador in enumerate(pontuacao_atualizada):
        cursor.execute("UPDATE pontuacao SET posicao = ? WHERE nome = ?", (i + 1, jogador['nome']))

    conn.commit()
    conn.close()
    flash('Pontuação atualizada com sucesso! Jogos foram marcados como finalizados.', 'info')
    return redirect(url_for('admin_dashboard'))


@app.route('/palpite_campeao', methods=['GET', 'POST'])
def palpite_campeao():
    conn = get_db_connection()
    # Obter a lista de todos os times que aparecem em 'jogos'
    all_teams_db = conn.execute('''
        SELECT DISTINCT time1_nome as name, time1_img as img_src FROM jogos
        UNION
        SELECT DISTINCT time2_nome as name, time2_img as img_src FROM jogos
        ORDER BY name
    ''').fetchall()
    
    palpiteiros = ["Ariel", "Carlos", "Celso", "Gabriel", "Lucas"]

    # Determinar a rodada ativa (esta parte deve estar tanto para GET quanto POST)
    agora = datetime.now()
    rodadas_no_db = conn.execute("SELECT DISTINCT rodada FROM jogos ORDER BY rodada ASC").fetchall()
    rodada_ativa_para_registro = None
    for row in rodadas_no_db:
        num_rodada = row['rodada']
        ultimo_jogo_da_rodada = conn.execute(
            "SELECT data_hora FROM jogos WHERE rodada = ? ORDER BY data_hora DESC LIMIT 1", (num_rodada,)
        ).fetchone()
        if ultimo_jogo_da_rodada:
            ultimo_jogo_datetime = datetime.strptime(ultimo_jogo_da_rodada['data_hora'], '%Y-%m-%d %H:%M')
            if agora < ultimo_jogo_datetime:
                rodada_ativa_para_registro = num_rodada
                break
    if rodada_ativa_para_registro is None and rodadas_no_db:
        rodada_ativa_para_registro = rodadas_no_db[-1]['rodada']
    elif not rodadas_no_db:
        rodada_ativa_para_registro = 1

    if request.method == 'POST':
        nome = request.form['nome']
        time_campeao = request.form['time_campeao']
        
        time_campeao_info = next((team for team in all_teams_db if team['name'] == time_campeao), None)
        time_campeao_img = time_campeao_info['img_src'] if time_campeao_info else None

        # Verifica se já existe palpite para este palpiteiro
        existente = conn.execute(
            'SELECT id FROM palpite_campeao WHERE nome = ?',
            (nome,)
        ).fetchone()
        
        if existente:
            conn.execute(
                'UPDATE palpite_campeao SET time_campeao = ?, time_campeao_img = ?, rodada = ?, data_palpite = ? WHERE id = ?',
                (time_campeao, time_campeao_img, rodada_ativa_para_registro, datetime.now().strftime('%Y-%m-%d %H:%M'), existente['id'])
            )
        else:
            conn.execute(
                'INSERT INTO palpite_campeao (nome, time_campeao, time_campeao_img, rodada, data_palpite) VALUES (?, ?, ?, ?, ?)',
                (nome, time_campeao, time_campeao_img, rodada_ativa_para_registro, datetime.now().strftime('%Y-%m-%d %H:%M'))
            )
        
        conn.commit()
        conn.close()
        flash('Seu palpite para campeão foi registrado/atualizado!', 'success')
        return redirect(url_for('ver_palpites_campeao'))
    
    # GET request
    conn.close()
    return render_template('palpite_campeao.html',
        palpiteiros=palpiteiros,
        times=all_teams_db,
        rodada_atual_display=rodada_ativa_para_registro
    )

@app.route('/ver_palpites_campeao')
def ver_palpites_campeao():
    conn = get_db_connection()
    palpites = conn.execute('''
        SELECT p.nome, p.time_campeao, p.data_palpite, p.time_campeao_img, p.rodada
        FROM palpite_campeao p
        ORDER BY p.rodada ASC, p.nome ASC
    ''').fetchall()
    
    campeao_real = conn.execute('SELECT time_campeao, time_campeao_img, data_definicao FROM campeao_mundial ORDER BY data_definicao DESC LIMIT 1').fetchone()

    conn.close()
    
    return render_template('ver_palpites_campeao.html', palpites=palpites, campeao_real=campeao_real)

# Rota para o Admin definir o campeão real
@app.route('/admin/set_champion', methods=['GET', 'POST'])
@login_required
def set_champion():
    conn = get_db_connection()
    cursor = conn.cursor()

    all_teams_db = conn.execute('''
        SELECT DISTINCT time1_nome as name, time1_img as img_src FROM jogos
        UNION
        SELECT DISTINCT time2_nome as name, time2_img as img_src FROM jogos
        ORDER BY name
    ''').fetchall()

    if request.method == 'POST':
        campeao_nome = request.form['campeao_nome']
        
        campeao_info = next((team for team in all_teams_db if team['name'] == campeao_nome), None)
        campeao_img = campeao_info['img_src'] if campeao_info else None

        # Limpa o campeão anterior e insere o novo (assumindo apenas 1 campeão mundial)
        try:
            cursor.execute('DELETE FROM campeao_mundial')
            cursor.execute(
                'INSERT INTO campeao_mundial (time_campeao, time_campeao_img, data_definicao) VALUES (?, ?, ?)',
                (campeao_nome, campeao_img, datetime.now().strftime('%Y-%m-%d %H:%M'))
            )
            conn.commit()
            flash(f'Campeão mundial definido como {campeao_nome}!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao definir campeão: {e}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('set_champion'))

    campeao_atual = conn.execute('SELECT time_campeao, time_campeao_img FROM campeao_mundial LIMIT 1').fetchone()
    conn.close()

    return render_template('set_champion.html', teams=all_teams_db, campeao_atual=campeao_atual)

if __name__ == '__main__':
    conn = get_db_connection()
    cursor = conn.cursor()
    # Adicionando alguns jogos extras para garantir que a rodada ativa mude.
    # A rodada 1 termina no dia 16/06 14:00. Se a data atual for depois disso, a rodada 2 se torna ativa.
    # Ajuste as datas para testar as transições.
    for rodada_num, jogos_rodada in MUNDIAL_JOGOS_POR_RODADA.items():
        for jogo in jogos_rodada:
            cursor.execute("SELECT id FROM jogos WHERE id = ?", (jogo['id'],))
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO jogos (id, rodada, time1_nome, time1_img, time1_sigla, time2_nome, time2_img, time2_sigla, data_hora, local, placar_time1, placar_time2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (jogo['id'], rodada_num, jogo['time1_nome'], jogo['time1_img'], jogo['time1_sigla'], jogo['time2_nome'], jogo['time2_img'], jogo['time2_sigla'], jogo['data_hora'], jogo['local'], None, None)
                )
    conn.commit()
    conn.close()

    app.run(host="0.0.0.0", port=3000, debug=True)