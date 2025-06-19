from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from functools import wraps
from collections import defaultdict
import sqlite3
import re


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
    print("\n[LOG - init_db]: Verificando e inicializando o banco de dados...")
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS pontuacao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        posicao INTEGER,
        nome TEXT UNIQUE,
        pontos INTEGER DEFAULT 0,
        acertos INTEGER DEFAULT 0,
        erros INTEGER DEFAULT 0,
        pontos_bonus INTEGER DEFAULT 0
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

# Decorator para exigir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
    pontuacao = conn.execute('''
        SELECT nome, acertos, erros, pontos, pontos_bonus, 
               (pontos + pontos_bonus) as total_pontos
        FROM pontuacao 
        ORDER BY total_pontos DESC, acertos DESC
    ''').fetchall()
    
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

    print(f"\n[LOG] Acessando página inicial - Rodada ativa: {rodada_ativa}")
    print(f"[LOG] Jogos futuros: {len(jogos_futuros)}, Jogos passados: {len(jogos_passados)}\n")
    
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
        print(f"[LOG] Rodada solicitada via parâmetro: {rodada_para_exibir}")
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
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # A lógica de salvar os palpites (POST) continua a mesma
        nome = request.form['nome']
        rodada_selecionada = int(request.form['rodada_selecionada'])
        print(f"\n[LOG - adicionar_palpites]: Recebido POST de '{nome}' para a rodada {rodada_selecionada}.")

        try:
            cursor.execute("INSERT OR IGNORE INTO pontuacao (nome) VALUES (?)", (nome,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass # Ignora se o nome já existe, que é o esperado

        agora_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        jogos_da_rodada_para_palpite = conn.execute(
            "SELECT id, time1_nome, time2_nome FROM jogos WHERE rodada = ? AND data_hora > ?",
            (rodada_selecionada, agora_str)
        ).fetchall()

        palpites_inseridos = 0
        for jogo in jogos_da_rodada_para_palpite:
            game_id = jogo['id']
            # Checa se o palpite para este jogo específico foi enviado
            if f'gol_time1_{game_id}' in request.form:
                gol_time1 = int(request.form[f'gol_time1_{game_id}'])
                gol_time2 = int(request.form[f'gol_time2_{game_id}'])
                resultado_palpite = request.form[f'resultado_{game_id}']
                
                # Insere ou atualiza o palpite
                cursor.execute("DELETE FROM palpites WHERE nome = ? AND game_id = ?", (nome, game_id))
                cursor.execute(
                    "INSERT INTO palpites (nome, rodada, game_id, time1, time2, gol_time1, gol_time2, resultado, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (nome, rodada_selecionada, game_id, jogo['time1_nome'], jogo['time2_nome'], gol_time1, gol_time2, resultado_palpite, 'Pendente')
                )
                palpites_inseridos += 1

        conn.commit()
        conn.close()
        
        if palpites_inseridos > 0:
            print(f"[LOG - adicionar_palpites]: {palpites_inseridos} palpites de '{nome}' registrados com sucesso.")
            flash(f'{palpites_inseridos} palpites foram registrados com sucesso!', 'success')
        else:
            flash('Nenhum palpite novo foi registrado (a rodada pode estar fechada).', 'warning')
            
        return redirect(url_for('exibir_palpites'))

    # --- LÓGICA DO GET ATUALIZADA ---
    # Quando a página é carregada (sem POST)
    
    agora_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 1. Pega todas as rodadas que existem no sistema para o menu dropdown
    todas_as_rodadas_rows = conn.execute("SELECT DISTINCT rodada FROM jogos ORDER BY rodada ASC").fetchall()
    todas_as_rodadas = [r['rodada'] for r in todas_as_rodadas_rows]

    rodada_selecionada_pelo_usuario = request.args.get('rodada', type=int)
    rodada_ativa = 0

    # 2. Verifica se o usuário escolheu uma rodada específica na URL
    if rodada_selecionada_pelo_usuario in todas_as_rodadas:
        rodada_ativa = rodada_selecionada_pelo_usuario
    else:
        # 3. Se não, encontra a primeira rodada que ainda tem jogos abertos
        rodada_aberta_row = conn.execute(
            "SELECT rodada FROM jogos WHERE data_hora > ? ORDER BY rodada ASC LIMIT 1",
            (agora_str,)
        ).fetchone()

        if rodada_aberta_row:
            rodada_ativa = rodada_aberta_row['rodada']
        else:
            # Se não houver nenhuma rodada aberta, seleciona a última rodada como padrão
            rodada_ativa = todas_as_rodadas[-1] if todas_as_rodadas else 1
    
    # 4. Busca os jogos que ainda estão abertos para a rodada ativa
    jogos_para_palpitar = conn.execute(
        "SELECT id, time1_nome, time1_img, time1_sigla, time2_nome, time2_img, time2_sigla, data_hora, local FROM jogos WHERE rodada = ? AND data_hora > ?",
        (rodada_ativa, agora_str)
    ).fetchall()
    
    palpiteiros = ["Ariel", "Carlos", "Celso", "Gabriel", "Lucas"]
    conn.close()

    return render_template(
        'adicionar_palpites.html',
        rodadas=todas_as_rodadas,
        rodada_selecionada=rodada_ativa,
        jogos=jogos_para_palpitar,
        palpiteiros=palpiteiros
    )

@app.route('/estatisticas')
def estatisticas():
    conn = get_db_connection()

    # 1. Busca estatísticas e calcula o percentual (sem alterações aqui)
    estatisticas_completas = conn.execute('''
        SELECT nome, pontos, acertos, erros,
               CASE WHEN (acertos + erros) = 0 THEN 0.0 ELSE ROUND((acertos * 100.0 / (acertos + erros)), 1) END as percentual_acertos
        FROM pontuacao ORDER BY pontos DESC, acertos DESC
    ''').fetchall()

    maior_pontuador = estatisticas_completas[0] if estatisticas_completas else None
    quem_acertou_mais = sorted(estatisticas_completas, key=lambda x: x['acertos'], reverse=True)[0] if estatisticas_completas else None

    # --- LÓGICA ATUALIZADA PARA SEQUÊNCIA ATUAL NA RODADA ---
    
    # 2. Descobre a última rodada com palpites avaliados
    rodada_atual_row = conn.execute("SELECT MAX(rodada) as rodada FROM palpites WHERE status != 'Pendente'").fetchone()
    rodada_atual_bonus = rodada_atual_row['rodada'] if rodada_atual_row and rodada_atual_row['rodada'] else 0

    print(f"\n[LOG] Rodada atual para cálculo de bônus: {rodada_atual_bonus}")

    sequencias_info = defaultdict(int)
    
    if rodada_atual_bonus > 0:
        palpites_rodada_atual = conn.execute("""
            SELECT p.nome, p.status, j.data_hora FROM palpites p
            JOIN jogos j ON p.game_id = j.id
            WHERE p.status != 'Pendente' AND p.rodada = ?
            ORDER BY p.nome, j.data_hora
        """, (rodada_atual_bonus,)).fetchall()

        # 3. Calcula a SEQUÊNCIA ATUAL para cada jogador
        for jogador in estatisticas_completas:
            nome = jogador['nome']
            palpites_do_jogador_na_rodada = [p for p in palpites_rodada_atual if p['nome'] == nome]
            
            sequencia_atual = 0
            for palpite in palpites_do_jogador_na_rodada:
                if "Erro" not in palpite['status']:
                    sequencia_atual += 1
                else:
                    # Se errar, a sequência atual é zerada imediatamente.
                    sequencia_atual = 0
            
            # O valor final é a sequência atual, contada até o último jogo avaliado.
            sequencias_info[nome] = sequencia_atual

    # 4. Prepara os dados para o template (sem alterações aqui)
    sequencias_para_template = []
    for jogador in estatisticas_completas:
        nome = jogador['nome']
        max_streak = sequencias_info[nome]
        sequencias_para_template.append({
            'nome': nome,
            'sequencia': max_streak,
            'bonus': '🔥 Bônus Disponível!' if max_streak >= 3 else '--'
        })

    conn.close()

    print(f"\n[LOG] Estatísticas carregadas para {len(estatisticas_completas)} jogadores\n")

    return render_template('estatisticas.html',
                           maior_pontuador=maior_pontuador,
                           quem_acertou_mais=quem_acertou_mais,
                           estatisticas_completas=estatisticas_completas,
                           sequencias=sequencias_para_template,
                           rodada_atual_bonus=rodada_atual_bonus)

# --- ROTA COMPLETAMENTE NOVA PARA O ADMIN CONCEDER O BÔNUS ---
@app.route('/admin/award_bonus', methods=['POST'])
@login_required
def award_bonus():
    if request.form.get('password') != ADMIN_PASSWORD:
        print("\n[LOG] Tentativa de conceder bônus com senha incorreta")
        flash('Senha de administrador incorreta!', 'danger')
        return redirect(url_for('admin_dashboard'))

    nome_jogador = request.form.get('nome_jogador')
    pontos_bonus = 3

    if not nome_jogador:
        print("\n[LOG] Nenhum jogador selecionado para bônus")
        flash('Você precisa selecionar um jogador para conceder o bônus.', 'warning')
        return redirect(url_for('admin_dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    print(f"\n[LOG] Tentando conceder bônus para {nome_jogador}")

    try:
        cursor.execute("UPDATE pontuacao SET pontos_bonus = pontos_bonus + ? WHERE nome = ?", (pontos_bonus, nome_jogador))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"\n[LOG] Bônus concedido com sucesso para {nome_jogador}")
            flash(f'Bônus de {pontos_bonus} pontos concedido para {nome_jogador} com sucesso!', 'success')
        else:
            print(f"\n[LOG] Jogador {nome_jogador} não encontrado")
            flash(f'Jogador {nome_jogador} não encontrado na tabela de pontuação.', 'danger')
    except Exception as e:
        print(f"\n[LOG] Erro ao conceder bônus: {str(e)}")
        conn.rollback()
        flash(f'Erro ao conceder bônus: {e}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/regras')
def regra():
    print("\n[LOG] Acessando página de regras\n")
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

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            print(f"\n[LOG] Login realizado por {username}\n")
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            print(f"\n[LOG] Tentativa de login falhou - Usuário: {username}")
            flash('Nome de usuário ou senha incorretos.', 'danger')
    return render_template('login.html')

# Rota de Logout
@app.route('/logout')
def logout():
    print(f"\n[LOG] Logout realizado por {session.get('username', 'N/A')}\n")
    session.pop('logged_in', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    conn = get_db_connection()
    # Busca a pontuação para popular o dropdown do bônus
    pontuacao_geral = conn.execute("SELECT nome FROM pontuacao ORDER BY nome").fetchall()
    conn.close()
    return render_template('admin_dashboard.html', pontuacao_geral=pontuacao_geral)

@app.route('/admin/set_game_result', methods=['GET', 'POST'])
@login_required
def set_game_result():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n[LOG] Acessando rota /admin/set_game_result")

    if request.method == 'POST':
        if request.form.get('password') != ADMIN_PASSWORD:
            print("\n[LOG] Tentativa de acesso com senha incorreta")
            flash('Senha incorreta!', 'danger')
            conn.close()
            return redirect(url_for('set_game_result'))

        game_id = request.form.get('game_id', type=int)
        placar_time1 = request.form.get('placar_time1', type=int)
        placar_time2 = request.form.get('placar_time2', type=int)
        
        print(f"\n[LOG] Tentativa de atualizar jogo {game_id} para {placar_time1}x{placar_time2}")

        try:
            cursor.execute(
                "UPDATE jogos SET placar_time1 = ?, placar_time2 = ?, status = 'Ao Vivo' WHERE id = ?",
                (placar_time1, placar_time2, game_id)
            )
            conn.commit()
            if cursor.rowcount == 0:
                print(f"\n[LOG] Jogo com ID {game_id} não encontrado")
                flash(f'Jogo com ID {game_id} não encontrado.', 'warning')
            else:
                print(f"\n[LOG] Jogo {game_id} atualizado com sucesso\n")
                flash(f'Placar ao vivo do jogo ID {game_id} atualizado para {placar_time1}x{placar_time2}!', 'success')
        except Exception as e:
            print(f"\n[LOG] Erro ao atualizar jogo: {str(e)}")
            conn.rollback()
            flash(f'Erro ao atualizar o placar ao vivo: {e}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('set_game_result'))

    # GET request
    jogos_disponiveis = conn.execute("SELECT id, time1_nome, time2_nome, data_hora, placar_time1, placar_time2 FROM jogos ORDER BY data_hora").fetchall()
    conn.close()
    
    print(f"\n[LOG] Exibindo formulário com {len(jogos_disponiveis)} jogos disponíveis")

    return render_template('set_game_result.html', jogos_disponiveis=jogos_disponiveis)


@app.route('/atualizar_pontuacao_admin')
@login_required
def atualizar_pontuacao_admin():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n[LOG] Iniciando atualização de pontuação")

    cursor.execute("UPDATE pontuacao SET pontos = 0, acertos = 0, erros = 0")
    print("\n[LOG] Zeradas as pontuações existentes")

    jogos_com_resultados = conn.execute("SELECT id, placar_time1, placar_time2 FROM jogos WHERE placar_time1 IS NOT NULL AND placar_time2 IS NOT NULL").fetchall()
    resultados_reais_map = {jogo['id']: (jogo['placar_time1'], jogo['placar_time2']) for jogo in jogos_com_resultados}
    
    print(f"\n[LOG] Jogos com resultados definidos: {len(resultados_reais_map)}")

    cursor.execute("SELECT * FROM palpites")
    palpites = cursor.fetchall()
    
    print(f"\n[LOG] Total de palpites a processar: {len(palpites)}")

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
            
            print(f"\n[LOG] Processando palpite de {nome} para jogo {game_id}")
            print(f"[LOG] Palpite: {gol_time1}-{gol_time2} ({palpite_resultado_texto})")
            print(f"[LOG] Resultado real: {gol_real_time1}-{gol_real_time2}")

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
                print(f"[LOG] Acerto total/placar: +{pontos_ganhos} pontos")
            else:
                if palpite_resultado_texto == real_resultado_texto:
                    pontos_ganhos = 1
                    status_palpite = "Acerto Resultado (1 pts)"
                    cursor.execute("UPDATE pontuacao SET acertos = acertos + 1 WHERE nome = ?", (nome,))
                    print(f"[LOG] Acerto resultado: +1 ponto")
                else:
                    cursor.execute("UPDATE pontuacao SET erros = erros + 1 WHERE nome = ?", (nome,))
                    status_palpite = "Erro (0 pts)"
                    print(f"[LOG] Erro: 0 pontos")

            cursor.execute("UPDATE pontuacao SET pontos = pontos + ? WHERE nome = ?", (pontos_ganhos, nome))
            cursor.execute("UPDATE palpites SET status = ? WHERE id = ?", (status_palpite, palpite_id))
        else:
            status_palpite = "Pendente"
            cursor.execute("UPDATE palpites SET status = ? WHERE id = ?", (status_palpite, palpite_id))
    
    # ALTERAÇÃO: Após calcular os pontos, atualiza o status dos jogos processados para 'Finalizado'
    if resultados_reais_map:
        placeholders = ','.join('?' for _ in resultados_reais_map.keys())
        cursor.execute(f"UPDATE jogos SET status = 'Finalizado' WHERE id IN ({placeholders})", list(resultados_reais_map.keys()))

        # --- INÍCIO DA NOVA LÓGICA PARA PONTUAR O CAMPEÃO ---
    PONTOS_CAMPEAO = 5 
    campeao_real = conn.execute("SELECT time_campeao FROM campeao_mundial LIMIT 1").fetchone()
    if campeao_real:
        palpites_campeao = conn.execute("SELECT nome, time_campeao FROM palpite_campeao").fetchall()
        for palpite in palpites_campeao:
            if palpite['time_campeao'] == campeao_real['time_campeao']:
                # Adiciona os pontos e um acerto extra para o palpite de campeão
                cursor.execute("UPDATE pontuacao SET pontos = pontos + ?, acertos = acertos + 1 WHERE nome = ?", (PONTOS_CAMPEAO, palpite['nome']))
                print(f"\n[LOG] Pontos de campeão concedidos para {palpite['nome']}")

    pontuacao_atualizada = conn.execute("SELECT nome, pontos FROM pontuacao ORDER BY pontos DESC, acertos DESC, erros ASC").fetchall()
    for i, jogador in enumerate(pontuacao_atualizada):
        cursor.execute("UPDATE pontuacao SET posicao = ? WHERE nome = ?", (i + 1, jogador['nome']))

    conn.commit()
    conn.close()
    
    print("\n[LOG] Pontuação atualizada com sucesso")
    flash('Pontuação atualizada com sucesso!', 'info')
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
            print(f"\n[LOG] Atualizando palpite de campeão para {nome}\n")
            conn.execute(
                'UPDATE palpite_campeao SET time_campeao = ?, time_campeao_img = ?, rodada = ?, data_palpite = ? WHERE id = ?',
                (time_campeao, time_campeao_img, rodada_ativa_para_registro, datetime.now().strftime('%Y-%m-%d %H:%M'), existente['id'])
            )
        else:
            print(f"\n[LOG] Inserindo novo palpite de campeão para {nome}\n")
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
    
    print(f"\n[LOG] Exibindo formulário de palpite campeão para rodada {rodada_ativa_para_registro}\n")
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
    
    print(f"\n[LOG] Exibindo palpites de campeão - Total: {len(palpites)}\n")
    return render_template('ver_palpites_campeao.html', palpites=palpites, campeao_real=campeao_real)

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
            print(f"\n[LOG] Campeão definido: {campeao_nome}\n")
            flash(f'Campeão mundial definido como {campeao_nome}!', 'success')
        except Exception as e:
            conn.rollback()
            print(f"\n[LOG] Erro ao definir campeão: {str(e)}\n")
            flash(f'Erro ao definir campeão: {e}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('set_champion'))

    campeao_atual = conn.execute('SELECT time_campeao, time_campeao_img FROM campeao_mundial LIMIT 1').fetchone()
    conn.close()

    print("\n[LOG] Acessando página de definição de campeão\n")
    return render_template('set_champion.html', teams=all_teams_db, campeao_atual=campeao_atual)

if __name__ == '__main__':
    conn = get_db_connection()
    cursor = conn.cursor()
    print(f"\n[LOG - Main]: Servidor Flask iniciando em http://192.168.1.244:3000")
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

    print("[LOG] Iniciando aplicação Flask\n")
    print("Pressione CTRL+C para parar o servidor.\n")
    app.run(host="0.0.0.0", port=3000, debug=True)