from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from datetime import datetime
from functools import wraps
from collections import defaultdict
import sqlite3
import re
import socket

# --- Configurações de Administrador ---
app = Flask(__name__)
app.secret_key = 'ALJDHA76797#%*#JKOL'
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "pokemar16#" 

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
    3: [
        {
            'id': 301,
            'time1_nome': 'Seattle Sounders',
            'time1_sigla': 'SES',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/k6m3hoy4Rn3KRrMYSYDjog_48x48.png',
            'time2_nome': 'PSG',
            'time2_sigla': 'PSG',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/mcpMspef1hwHwi9qrfp4YQ_48x48.png',
            'data_hora': '2025-06-23 16:00',
            'local': 'Lumen Field'
        },
        {
            'id': 302,
            'time1_nome': 'Atlético de Madrid',
            'time1_sigla': 'ATM',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/pEqmA7CL-VRo4Llq3rwIPA_48x48.png',
            'time2_nome': 'Botafogo',
            'time2_sigla': 'BOT',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png',
            'data_hora': '2025-06-23 16:00',
            'local': 'Rose Bowl'
        },
        {
            'id': 303,
            'time1_nome': 'Palmeiras',
            'time1_sigla': 'PAL',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png',
            'time2_nome': 'Inter Miami',
            'time2_sigla': 'INT',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/dn0bMtTbbpx7v3Ieq6TZtQ_48x48.png',
            'data_hora': '2025-06-23 22:00',
            'local': 'Hard Rock Stadium'
        },
        {
            'id': 304,
            'time1_nome': 'Porto',
            'time1_sigla': 'POT',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/QkkllEKwkj60jEVtOEZWAg_48x48.png',
            'time2_nome': 'Al Ahly',
            'time2_sigla': 'ALA',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/JdNbaaw7JlDHvPHZaX2V2A_48x48.png',
            'data_hora': '2025-06-23 22:00',
            'local': 'MetLife Stadium'
        },
        {
            'id': 305,
            'time1_nome': 'Benfica',
            'time1_sigla': 'BEN',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/nFwABZ-4n_A3BGXT9A7Adg_48x48.png',
            'time2_nome': 'Bayern',
            'time2_sigla': 'BAY',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/-_cmntP5q_pHL7g5LfkRiw_96x96.png',
            'data_hora': '2025-06-24 16:00',
            'local': 'Bank of America Stadium'
        },
        {
            'id': 306,
            'time1_nome': 'Auckland City',
            'time1_sigla': 'ACC',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/ydlyVc6hUPBXoaT3wR_lFg_96x96.png',
            'time2_nome': 'Boca Juniors',
            'time2_sigla': 'BOC',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/YO1impuFJT2hex6wvCd9Pw_48x48.png',
            'data_hora': '2025-06-24 16:00',
            'local': 'Geodis Park'
        },
        {
            'id': 307,
            'time1_nome': 'LAFC',
            'time1_sigla': 'LOS',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/waD0z1CWx6_r4UT_hgb7nA_96x96.png',
            'time2_nome': 'Flamengo',
            'time2_sigla': 'FLA',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png',
            'data_hora': '2025-06-24 22:00',
            'local': 'Camping World Stadium'
        },
        {
            'id': 308,
            'time1_nome': 'Espérance',
            'time1_sigla': 'EST',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/Kf32x8gh5SCMEqvKjVGLfg_48x48.png',
            'time2_nome': 'Chelsea',
            'time2_sigla': 'CFC',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/fhBITrIlbQxhVB6IjxUO6Q_48x48.png',
            'data_hora': '2025-06-24 22:00',
            'local': 'Lincoln Financial Field'
        },
        {
            'id': 309,
            'time1_nome': 'Sundowns',
            'time1_sigla': 'MSM',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/Lmp8fUABWWKRwNrHf71m5w_48x48.png',
            'time2_nome': 'Fluminense',
            'time2_sigla': 'FLU',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/fCMxMMDF2AZPU7LzYKSlig_48x48.png',
            'data_hora': '2025-06-25 16:00',
            'local': 'Hard Rock Stadium'
        },
        {
            'id': 310,
            'time1_nome': 'Borussia',
            'time1_sigla': 'BVB',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/FZnTSH2rbHFos4BnlWAItw_48x48.png',
            'time2_nome': 'Ulsan Hyundai',
            'time2_sigla': 'ULH',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/-K1h8OOTItUmjKqR2g5Nnw_48x48.png',
            'data_hora': '2025-06-25 16:00',
            'local': 'TQL Stadium'
        },
        {
            'id': 311,
            'time1_nome': 'Inter',
            'time1_sigla': 'INT',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/l2-icwsMhIvsbRw8AwC1yg_48x48.png',
            'time2_nome': 'River Plate',
            'time2_sigla': 'RIV',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/700Mj6lUNkbBdvOVEbjC3g_48x48.png',
            'data_hora': '2025-06-25 22:00',
            'local': 'Lumen Field'
        },
        {
            'id': 312,
            'time1_nome': 'Urawa Reds',
            'time1_sigla': 'URD',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/F-09rxdgECid61-Rj8Uxrw_48x48.png',
            'time2_nome': 'Monterrey',
            'time2_sigla': 'MTR',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/LXZ8fEgzf0_FwSyq15buPw_48x48.png',
            'data_hora': '2025-06-25 22:00',
            'local': 'Rose Bowl'
        },
        {
            'id': 313,
            'time1_nome': 'Juventus',
            'time1_sigla': 'JUV',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/6lal-0xwWtos5HI99HRvuQ_48x48.png',
            'time2_nome': 'City',
            'time2_sigla': 'MNC',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/z44l-a0W1v5FmgPnemV6Xw_48x48.png',
            'data_hora': '2025-06-26 16:00',
            'local': 'Lincoln Financial Field'
        },
        {
            'id': 314,
            'time1_nome': 'Wydad AC',
            'time1_sigla': 'WYD',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/JxwBeJ9HrjZX_vRqTPwY6A_48x48.png',
            'time2_nome': 'Al Ain',
            'time2_sigla': 'AIN',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/vA9sLyDeHX3q7pn8QTmoeQ_48x48.png',
            'data_hora': '2025-06-26 16:00',
            'local': 'Audi Field'
        },
        {
            'id': 315,
            'time1_nome': 'Salzburg',
            'time1_sigla': 'SLZ',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/vQhr4NoE_4Yg1IhUZvbRNw_48x48.png',
            'time2_nome': 'Real Madrid',
            'time2_sigla': 'RMA',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/Th4fAVAZeCJWRcKoLW7koA_48x48.png',
            'data_hora': '2025-06-26 22:00',
            'local': 'Lincoln Financial Field'
        },
        {
            'id': 316,
            'time1_nome': 'Al Hilal',
            'time1_sigla': 'HIL',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/HGVsnyWvMiGVotxhgicdSQ_48x48.png',
            'time2_nome': 'Pachuca',
            'time2_sigla': 'PCH',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/9dscoX8iYhzbjSNxXVp2gQ_48x48.png',
            'data_hora': '2025-06-26 22:00',
            'local': 'Geodis Park'
        },
    ],
    4: [
        {
            'id': 401,
            'time1_nome': 'Palmeiras',
            'time1_sigla': 'PAL',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png',
            'time2_nome': 'Botafogo',
            'time2_sigla': 'BOT',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png',
            'data_hora': '2025-06-28 13:00',
            'local': 'Lincoln Financial Field'
        },
        {
            'id': 402,
            'time1_nome': 'Benfica',
            'time1_sigla': 'BEN',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/nFwABZ-4n_A3BGXT9A7Adg_48x48.png',
            'time2_nome': 'Chelsea',
            'time2_sigla': 'CFC',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/fhBITrIlbQxhVB6IjxUO6Q_48x48.png',
            'data_hora': '2025-06-28 17:00',
            'local': 'Bank of America Stadium'
        },
        {
            'id': 403,
            'time1_nome': 'PSG',
            'time1_sigla': 'PSG',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/mcpMspef1hwHwi9qrfp4YQ_48x48.png',
            'time2_nome': 'Inter Miami',
            'time2_sigla': 'INT',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/dn0bMtTbbpx7v3Ieq6TZtQ_48x48.png',
            'data_hora': '2025-06-29 13:00',
            'local': 'Mercedes-Benz Stadium'
        },
        {
            'id': 404,
            'time1_nome': 'Flamengo',
            'time1_sigla': 'FLA',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png',
            'time2_nome': 'Bayern',
            'time2_sigla': 'BAY',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/-_cmntP5q_pHL7g5LfkRiw_96x96.png',
            'data_hora': '2025-06-29 17:00',
            'local': 'Hard Rock Stadium'
        },
        {
            'id': 405,
            'time1_nome': 'Inter',
            'time1_sigla': 'INT',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/l2-icwsMhIvsbRw8AwC1yg_48x48.png',
            'time2_nome': 'Fluminense',
            'time2_sigla': 'FLU',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/fCMxMMDF2AZPU7LzYKSlig_48x48.png',
            'data_hora': '2025-06-30 16:00',
            'local': 'Bank of America Stadium'
        },
        {
            'id': 406,
            'time1_nome': 'City',
            'time1_sigla': 'MNC',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/z44l-a0W1v5FmgPnemV6Xw_48x48.png', 
            'time2_nome': 'Al Hilal',
            'time2_sigla': 'HIL',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/HGVsnyWvMiGVotxhgicdSQ_48x48.png',
            'data_hora': '2025-06-30 22:00',
            'local': 'Camping World Stadium'
        },
        {
            'id': 407,
            'time1_nome': 'Real Madrid',
            'time1_sigla': 'RMA',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/Th4fAVAZeCJWRcKoLW7koA_48x48.png',
            'time2_nome': 'Juventus',
            'time2_sigla': 'JUV',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/6lal-0xwWtos5HI99HRvuQ_48x48.png',
            'data_hora': '2025-07-01 16:00',
            'local': 'Hard Rock Stadium'
        },
        {
            'id': 408,
            'time1_nome': 'Borussia',
            'time1_sigla': 'BVB',
            'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/FZnTSH2rbHFos4BnlWAItw_48x48.png',
            'time2_nome': 'Monterrey',
            'time2_sigla': 'MTR',
            'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/LXZ8fEgzf0_FwSyq15buPw_48x48.png',
            'data_hora': '2025-07-01 22:00',
            'local': 'Mercedes-Benz Stadium'
        },
    ]
    # # Adicione mais rodadas e jogos conforme necessário, seguindo a estrutura
    # Certifique-se de que os IDs dos jogos são únicos em todo o dicionário
}


def get_db():
    """Abre uma nova conexão com o banco de dados se não houver uma no contexto da requisição."""
    if 'db' not in g:
        g.db = sqlite3.connect('palpites.db', timeout=10)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Fecha a conexão com o banco de dados no final da requisição."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Função de inicialização que usa uma conexão direta e temporária."""
    print("[LOG - init_db]: Verificando e inicializando o banco de dados...")
    with sqlite3.connect('palpites.db') as conn:
        cursor = conn.cursor()
        
        def column_exists(table_name, column_name):
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [info[1] for info in cursor.fetchall()]
            return column_name in columns

        # Adiciona colunas necessárias de forma segura
        if not column_exists('pontuacao', 'pontos_bonus'): conn.execute("ALTER TABLE pontuacao ADD COLUMN pontos_bonus INTEGER DEFAULT 0")
        if not column_exists('jogos', 'fase'): conn.execute("ALTER TABLE jogos ADD COLUMN fase TEXT DEFAULT 'grupos'")
        if not column_exists('jogos', 'time_que_avancou'): conn.execute("ALTER TABLE jogos ADD COLUMN time_que_avancou TEXT")
        if not column_exists('palpites', 'quem_avanca'): conn.execute("ALTER TABLE palpites ADD COLUMN quem_avanca TEXT")
        
        # Cria as tabelas se elas não existirem
        conn.execute('''
        CREATE TABLE IF NOT EXISTS pontuacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT, posicao INTEGER, nome TEXT UNIQUE,
            pontos INTEGER DEFAULT 0, acertos INTEGER DEFAULT 0, erros INTEGER DEFAULT 0,
            pontos_bonus INTEGER DEFAULT 0
        )''')
        conn.execute('''
        CREATE TABLE IF NOT EXISTS palpites (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, rodada INTEGER, game_id INTEGER,
            time1 TEXT, time2 TEXT, gol_time1 INTEGER, gol_time2 INTEGER, resultado TEXT, status TEXT,
            quem_avanca TEXT
        )''')
        conn.execute('''
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY, rodada INTEGER, time1_nome TEXT, time1_img TEXT, time1_sigla TEXT,
            time2_nome TEXT, time2_img TEXT, time2_sigla TEXT, data_hora TEXT, local TEXT,
            placar_time1 INTEGER, placar_time2 INTEGER, status TEXT DEFAULT 'Pendente',
            time_que_avancou TEXT
        )''')
        conn.execute('''
        CREATE TABLE IF NOT EXISTS campeao_palpiteiros (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            pontos INTEGER,
            acertos INTEGER,
            erros INTEGER,
            data_definicao TEXT NOT NULL
        )''')
        conn.commit()
    print("[LOG - init_db]: Banco de dados pronto.")

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
    if not date_str: return ""
    try:
        return datetime.strptime(date_str.split(' ')[0], '%Y-%m-%d').strftime('%d/%m/%Y')
    except (ValueError, IndexError):
        return date_str

@app.route('/')
def index():
    conn = get_db() # MUDANÇA
    pontuacao = conn.execute('''
        SELECT nome, acertos, erros, pontos, pontos_bonus, 
               (pontos + pontos_bonus) as total_pontos
        FROM pontuacao 
        ORDER BY total_pontos DESC, acertos DESC
    ''').fetchall()
    
    agora = datetime.now()
    rodada_param = request.args.get('rodada', type=int)
    
    rodadas_disponiveis_rows = conn.execute("SELECT DISTINCT rodada FROM jogos ORDER BY rodada").fetchall()
    rodadas_disponiveis = [r['rodada'] for r in rodadas_disponiveis_rows]
    
    rodada_ativa = rodada_param if (rodada_param and rodada_param in rodadas_disponiveis) else (rodadas_disponiveis[-1] if rodadas_disponiveis else 1)
    
    print(f"\n[LOG - index]: Rodada ativa para exibição: {rodada_ativa}\n")
    
    rodada_index = rodadas_disponiveis.index(rodada_ativa) if rodada_ativa in rodadas_disponiveis else -1
    tem_proxima = rodada_index != -1 and rodada_index < len(rodadas_disponiveis) - 1
    tem_anterior = rodada_index > 0
    
    agora_str = agora.strftime('%Y-%m-%d %H:%M')
    
    jogos_futuros = conn.execute("SELECT * FROM jogos WHERE rodada = ? AND data_hora > ? ORDER BY data_hora ASC", (rodada_ativa, agora_str)).fetchall()
    jogos_passados = conn.execute("SELECT * FROM jogos WHERE rodada = ? AND data_hora <= ? ORDER BY data_hora DESC", (rodada_ativa, agora_str)).fetchall()
    
    
    
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

@app.route('/chaveamento')
def chaveamento():
    print("[LOG]: Acessando a página de chaveamento.")
    conn = get_db()
    
    # Busca todos os jogos de mata-mata (Rodada 4 em diante)
    jogos_mata_mata = conn.execute("SELECT * FROM jogos WHERE rodada >= 4 ORDER BY id ASC").fetchall()
    

    # Organiza os jogos por rodada e ID para fácil acesso
    jogos_map = {jogo['id']: dict(jogo) for jogo in jogos_mata_mata}

    # Função para determinar o vencedor de um jogo
    def get_vencedor(jogo_id):
        jogo = jogos_map.get(jogo_id)
        if not jogo or jogo.get('time_que_avancou') is None:
            return {'nome': 'A definir', 'sigla': '???', 'img': 'https://placehold.co/40x40/eee/eee?text='}
        
        vencedor_nome = jogo['time_que_avancou']
        if vencedor_nome == jogo['time1_nome']:
            return {'nome': jogo['time1_nome'], 'sigla': jogo['time1_sigla'], 'img': jogo['time1_img']}
        else:
            return {'nome': jogo['time2_nome'], 'sigla': jogo['time2_sigla'], 'img': jogo['time2_img']}

    # Estrutura do chaveamento (hardcoded para o torneio de 16 times)
    # Oitavas de Final
    oitavas = [jogos_map.get(i) for i in range(401, 409)]

    # Quartas de Final
    quartas = [
        {'id': 501, 'time1': get_vencedor(401), 'time2': get_vencedor(402), 'dados_jogo': jogos_map.get(501)},
        {'id': 502, 'time1': get_vencedor(403), 'time2': get_vencedor(404), 'dados_jogo': jogos_map.get(502)},
        {'id': 503, 'time1': get_vencedor(405), 'time2': get_vencedor(406), 'dados_jogo': jogos_map.get(503)},
        {'id': 504, 'time1': get_vencedor(407), 'time2': get_vencedor(408), 'dados_jogo': jogos_map.get(504)},
    ]

    # Semifinais
    semis = [
        {'id': 601, 'time1': get_vencedor(501), 'time2': get_vencedor(502), 'dados_jogo': jogos_map.get(601)},
        {'id': 602, 'time1': get_vencedor(503), 'time2': get_vencedor(504), 'dados_jogo': jogos_map.get(602)},
    ]

    # Final
    final = [
        {'id': 701, 'time1': get_vencedor(601), 'time2': get_vencedor(602), 'dados_jogo': jogos_map.get(701)},
    ]
    
    campeao = get_vencedor(701)

    return render_template('chaveamento.html', 
                           oitavas=oitavas, 
                           quartas=quartas, 
                           semis=semis, 
                           final=final,
                           campeao=campeao)

@app.route('/palpites')
def exibir_palpites():
    conn = get_db()
    rodada_param = request.args.get('rodada', type=int)

    # Lógica para determinar a rodada a ser exibida
    rodada_para_exibir = 0
    if rodada_param:
        rodada_para_exibir = rodada_param
    else:
        # Encontra a rodada mais recente que tem palpites
        rodada_recente_row = conn.execute("SELECT MAX(rodada) as max_rodada FROM palpites").fetchone()
        if rodada_recente_row and rodada_recente_row['max_rodada']:
            rodada_para_exibir = rodada_recente_row['max_rodada']
        else:
            # Se não houver palpites, mostra a primeira rodada
            rodada_para_exibir = 1
    
    # Busca os palpites e os jogos da rodada selecionada
    palpites = conn.execute("SELECT * FROM palpites WHERE rodada = ? ORDER BY nome", (rodada_para_exibir,)).fetchall()
    jogos_da_rodada = conn.execute("SELECT * FROM jogos WHERE rodada = ?", (rodada_para_exibir,)).fetchall()
    
    # Cria um "mapa" para facilitar a busca de jogos no template
    jogos_map = {jogo['id']: jogo for jogo in jogos_da_rodada}

    # Agrupa os palpites por nome de jogador
    palpites_agrupados = defaultdict(list)
    for palpite in palpites:
        palpites_agrupados[palpite['nome']].append(palpite)

    # Lógica para navegação entre rodadas
    rodadas_existentes = sorted([r['rodada'] for r in conn.execute("SELECT DISTINCT rodada FROM jogos ORDER BY rodada ASC").fetchall()])
    idx_rodada = rodadas_existentes.index(rodada_para_exibir) if rodada_para_exibir in rodadas_existentes else -1
    tem_proxima = idx_rodada != -1 and idx_rodada < len(rodadas_existentes) - 1
    tem_anterior = idx_rodada > 0
    proxima_rodada = rodadas_existentes[idx_rodada + 1] if tem_proxima else None
    anterior_rodada = rodadas_existentes[idx_rodada - 1] if tem_anterior else None

    

    return render_template(
        'palpites.html',
        palpites_agrupados=palpites_agrupados,
        jogos_map=jogos_map,  # Passa os dados dos jogos para o template
        rodada_exibida_num=rodada_para_exibir,
        tem_proxima=tem_proxima,
        proxima_rodada=proxima_rodada,
        tem_anterior=tem_anterior,
        anterior_rodada=anterior_rodada
    )

@app.route('/adicionar_palpites', methods=['GET', 'POST'])
def adicionar_palpites():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        # A lógica de salvar os palpites (POST) precisa ser atualizada para incluir 'quem_avanca'
        nome = request.form.get('nome')
        rodada_selecionada = int(request.form.get('rodada_selecionada'))
        
        agora_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        jogos_da_rodada_para_palpite = conn.execute(
            "SELECT * FROM jogos WHERE rodada = ? AND data_hora > ?",
            (rodada_selecionada, agora_str)
        ).fetchall()

        for jogo in jogos_da_rodada_para_palpite:
            game_id = jogo['id']
            if f'gol_time1_{game_id}' in request.form:
                gol_time1 = int(request.form[f'gol_time1_{game_id}'])
                gol_time2 = int(request.form[f'gol_time2_{game_id}'])
                resultado_palpite = request.form[f'resultado_{game_id}']
                quem_avanca = request.form.get(f'quem_avanca_{game_id}', None)

                # Deleta o palpite antigo para inserir o novo/atualizado
                cursor.execute("DELETE FROM palpites WHERE nome = ? AND game_id = ?", (nome, game_id))
                cursor.execute(
                    "INSERT INTO palpites (nome, rodada, game_id, time1, time2, gol_time1, gol_time2, resultado, status, quem_avanca) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (nome, rodada_selecionada, game_id, jogo['time1_nome'], jogo['time2_nome'], gol_time1, gol_time2, resultado_palpite, 'Pendente', quem_avanca)
                )
        
        conn.commit()
        
        print(f"\n[LOG]: {nome} adicionou na rodada {rodada_selecionada}")
        print(f"[LOG]: {nome} adicionou {jogo['time1_nome']} x {jogo['time2_nome']}")
        flash('Palpites registrados com sucesso!', 'success')
        return redirect(url_for('exibir_palpites'))

    # --- LÓGICA DO GET ATUALIZADA ---
    agora_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    todas_as_rodadas_rows = conn.execute("SELECT DISTINCT rodada FROM jogos ORDER BY rodada ASC").fetchall()
    todas_as_rodadas = [r['rodada'] for r in todas_as_rodadas_rows]

    rodada_selecionada_pelo_usuario = request.args.get('rodada', type=int)
    rodada_ativa = 0

    if rodada_selecionada_pelo_usuario in todas_as_rodadas:
        rodada_ativa = rodada_selecionada_pelo_usuario
    else:
        rodada_aberta_row = conn.execute(
            "SELECT rodada FROM jogos WHERE data_hora > ? ORDER BY rodada ASC LIMIT 1", (agora_str,)
        ).fetchone()
        rodada_ativa = rodada_aberta_row['rodada'] if rodada_aberta_row else (todas_as_rodadas[-1] if todas_as_rodadas else 1)
    
    # CORREÇÃO: A consulta agora busca TODAS as colunas, incluindo 'fase'
    jogos_para_palpitar = conn.execute(
        "SELECT * FROM jogos WHERE rodada = ? AND data_hora > ?",
        (rodada_ativa, agora_str)
    ).fetchall()
    
    palpiteiros = ["Ariel", "Arthur", "Carlos", "Celso", "Gabriel", "Lucas"]
    

    return render_template(
        'adicionar_palpites.html',
        rodadas=todas_as_rodadas,
        rodada_selecionada=rodada_ativa,
        jogos=jogos_para_palpitar,
        palpiteiros=palpiteiros
    )

@app.route('/estatisticas')
def estatisticas():
    conn = get_db()

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

    

    print(f"\n[LOG - estatisticas]: Rodada atual para cálculo de bônus: {rodada_atual_bonus}")
    print(f"[LOG - estatisticas]: Estatísticas carregadas para {len(estatisticas_completas)} jogadores.\n")

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

    conn = get_db()
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
    conn = get_db()
    # A busca de palpites já pega a coluna 'quem_avanca', então está correta.
    palpites = conn.execute("SELECT * FROM palpites WHERE rodada = ?", (numero,)).fetchall()

    # CORREÇÃO: A busca de jogos agora inclui as colunas 'fase' e 'time_que_avancou'
    jogos_da_rodada = conn.execute(
        "SELECT * FROM jogos WHERE rodada = ? ORDER BY data_hora",
        (numero,)
    ).fetchall()
    

    palpites_agrupados = {}
    for palpite in palpites:
        nome = palpite['nome']
        if nome not in palpites_agrupados:
            palpites_agrupados[nome] = []
        # O palpite completo já é adicionado, o que é perfeito.
        palpites_agrupados[nome].append(palpite)

    return render_template('rodada.html', 
                           rodada=numero, 
                           palpites_agrupados=palpites_agrupados, 
                           jogos_da_rodada=jogos_da_rodada)

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        ip_cliente = request.remote_addr
        
        if username == ADMIN_USERNAME and request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            print(f"\n[LOG - login]: Login BEM-SUCEDIDO para '{username}' a partir do IP {ip_cliente}.\n")
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            print(f"\n[LOG - login]: Tentativa de login FALHOU para '{username}' a partir do IP {ip_cliente}.\n")
            flash('Nome de usuário ou senha incorretos.', 'danger')
    return render_template('login.html')

# Rota de Logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    print(f"\n[LOG] Logout realizado por {session.get('username', 'N/A')}\n")
    session.pop('logged_in', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    conn = get_db()
    pontuacao_geral = conn.execute("SELECT nome FROM pontuacao ORDER BY nome").fetchall()
    campeao_atual = conn.execute("SELECT nome FROM campeao_palpiteiros WHERE id = 1").fetchone()
    return render_template('admin_dashboard.html', pontuacao_geral=pontuacao_geral, campeao_atual=campeao_atual)


@app.route('/admin/set_game_result', methods=['GET', 'POST'])
@login_required
def set_game_result():
    conn = get_db()
    
    if request.method == 'POST':
        if request.form.get('password') != ADMIN_PASSWORD:
            flash('Senha incorreta!', 'danger')
            
            return redirect(url_for('set_game_result'))

        game_id = request.form.get('game_id', type=int)
        placar_time1 = request.form.get('placar_time1', type=int)
        placar_time2 = request.form.get('placar_time2', type=int)
        
        # --- NOVA LÓGICA PARA SALVAR QUEM AVANÇOU ---
        time_que_avancou = request.form.get('time_que_avancou')
        # Garante que um valor vazio seja salvo como NULL no banco
        if not time_que_avancou:
            time_que_avancou = None

        print(f"\n[LOG] Admin definindo resultado para Jogo ID {game_id}: {placar_time1}x{placar_time2}, Avançou: {time_que_avancou}")

        try:
            conn.execute(
                "UPDATE jogos SET placar_time1 = ?, placar_time2 = ?, status = 'Ao Vivo', time_que_avancou = ? WHERE id = ?",
                (placar_time1, placar_time2, time_que_avancou, game_id)
            )
            conn.commit()
            flash(f'Placar do jogo ID {game_id} atualizado com sucesso!', 'success')
        except Exception as e:
            conn.rollback()
            print(f"[ERRO] ao atualizar jogo: {e}")
            flash(f'Erro ao atualizar o placar: {e}', 'danger')
            
        
        return redirect(url_for('set_game_result'))

    # A busca de jogos para o GET continua a mesma
    jogos_disponiveis = conn.execute("SELECT * FROM jogos ORDER BY data_hora").fetchall()
    

    return render_template('set_game_result.html', jogos_disponiveis=jogos_disponiveis)


@app.route('/atualizar_pontuacao_admin')
@login_required
def atualizar_pontuacao_admin():
    print("\n[LOG]: Iniciando atualização de pontuação.")
    conn = get_db()
    
    # Zera os pontos de jogos, mas mantém os pontos de bônus
    conn.execute("UPDATE pontuacao SET pontos = 0, acertos = 0, erros = 0")
    
    palpites = conn.execute("SELECT * FROM palpites").fetchall()
    
    # ** A CORREÇÃO PRINCIPAL ESTÁ AQUI **
    # Busca TODOS os jogos que já têm um placar definido, não importa o status.
    jogos_finalizados = conn.execute("SELECT * FROM jogos WHERE placar_time1 IS NOT NULL AND placar_time2 IS NOT NULL").fetchall()
    
    if not jogos_finalizados:
        flash('Nenhum jogo com resultado definido para calcular a pontuação.', 'info')
        return redirect(url_for('admin_dashboard'))

    jogos_map = {jogo['id']: dict(jogo) for jogo in jogos_finalizados}
    print(f"[LOG]: Encontrados {len(jogos_finalizados)} jogos com resultado para processar.")

    for palpite in palpites:
        game_id = palpite['game_id']
        if game_id in jogos_map:
            jogo = jogos_map[game_id]
            nome = palpite['nome']
            pontos_ganhos = 0
            
            p_avanca = palpite['quem_avanca']
            j_avancou = jogo['time_que_avancou']
            
            p_gol1, p_gol2 = palpite['gol_time1'], palpite['gol_time2']
            p_resultado = palpite['resultado']
            j_gol1, j_gol2 = jogo['placar_time1'], jogo['placar_time2']
            
            if j_gol1 > j_gol2: j_resultado = 'Vitória (Casa)'
            elif j_gol1 < j_gol2: j_resultado = 'Vitória (Fora)'
            else: j_resultado = 'Empate'

            acerto_placar = (p_gol1 == j_gol1 and p_gol2 == j_gol2)
            acerto_resultado = (p_resultado == j_resultado)
            acerto_avanco = (p_avanca is not None and p_avanca == j_avancou)
            
            status_palpite = "Erro (0 pts)"

            if jogo['rodada'] >= 4: # Lógica para mata-mata
                if acerto_placar and acerto_resultado and acerto_avanco: pontos_ganhos, status_palpite = 5, "Acerto Total! (5 pts)"
                elif acerto_placar and acerto_resultado: pontos_ganhos, status_palpite = 4, "Acerto Placar + Resultado (4 pts)"
                elif acerto_placar and acerto_avanco: pontos_ganhos, status_palpite = 3, "Acerto Placar + Avanço (3 pts)"
                elif acerto_placar: pontos_ganhos, status_palpite = 2, "Acerto Placar (2 pts)"
                elif acerto_resultado and acerto_avanco: pontos_ganhos, status_palpite = 2, "Acerto Resultado + Avanço (2 pts)"
                elif acerto_resultado: pontos_ganhos, status_palpite = 1, "Acerto Resultado (1 pt)"
                elif acerto_avanco: pontos_ganhos, status_palpite = 1, "Acerto Avanço (1 pt)"
            else: # Lógica para fase de grupos
                if acerto_placar: pontos_ganhos, status_palpite = 4, "Acerto Total (4 pts)"
                elif acerto_resultado: pontos_ganhos, status_palpite = 1, "Acerto Resultado (1 pt)"

            if pontos_ganhos > 0:
                conn.execute("UPDATE pontuacao SET pontos = pontos + ?, acertos = acertos + 1 WHERE nome = ?", (pontos_ganhos, nome))
            else:
                conn.execute("UPDATE pontuacao SET erros = erros + 1 WHERE nome = ?", (nome,))
            
            conn.execute("UPDATE palpites SET status = ? WHERE id = ?", (status_palpite, palpite['id']))

    # Marca TODOS os jogos processados como 'Finalizado'
    ids_processados = list(jogos_map.keys())
    placeholders = ','.join('?' for _ in ids_processados)
    conn.execute(f"UPDATE jogos SET status = 'Finalizado' WHERE id IN ({placeholders})", ids_processados)
    print(f"[LOG]: Jogos com IDs {ids_processados} foram marcados como 'Finalizado'.")

    # Bônus do campeão
    campeao_real = conn.execute("SELECT time_campeao FROM campeao_mundial LIMIT 1").fetchone()
    if campeao_real:
        palpites_campeao = conn.execute("SELECT nome, time_campeao FROM palpite_campeao").fetchall()
        for palpite in palpites_campeao:
            if palpite['time_campeao'] == campeao_real['time_campeao']:
                conn.execute("UPDATE pontuacao SET pontos_bonus = pontos_bonus + ? WHERE nome = ?", (5, palpite['nome']))
        pass

    conn.commit()
    print("[LOG - atualizar_pontuacao_admin]: FIM do processo de atualização.")
    flash('Pontuação atualizada com sucesso!', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/palpite_campeao', methods=['GET', 'POST'])
def palpite_campeao():
    conn = get_db()
    # Obter a lista de todos os times que aparecem em 'jogos'
    all_teams_db = conn.execute('''
        SELECT DISTINCT time1_nome as name, time1_img as img_src FROM jogos
        UNION
        SELECT DISTINCT time2_nome as name, time2_img as img_src FROM jogos
        ORDER BY name
    ''').fetchall()
    
    palpiteiros = ["Ariel", "Arthur", "Carlos", "Celso", "Gabriel", "Lucas"]

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
        
        flash('Seu palpite para campeão foi registrado/atualizado!', 'success')
        return redirect(url_for('ver_palpites_campeao'))
    
    # GET request
    
    
    print(f"\n[LOG] Exibindo formulário de palpite campeão para rodada {rodada_ativa_para_registro}\n")
    return render_template('palpite_campeao.html',
        palpiteiros=palpiteiros,
        times=all_teams_db,
        rodada_atual_display=rodada_ativa_para_registro
    )

@app.route('/ver_palpites_campeao')
def ver_palpites_campeao():
    conn = get_db()
    palpites = conn.execute('''
        SELECT p.nome, p.time_campeao, p.data_palpite, p.time_campeao_img, p.rodada
        FROM palpite_campeao p
        ORDER BY p.rodada ASC, p.nome ASC
    ''').fetchall()
    
    campeao_real = conn.execute('SELECT time_campeao, time_campeao_img, data_definicao FROM campeao_mundial ORDER BY data_definicao DESC LIMIT 1').fetchone()

    
    
    print(f"\n[LOG] Exibindo palpites de campeão - Total: {len(palpites)}\n")
    return render_template('ver_palpites_campeao.html', palpites=palpites, campeao_real=campeao_real)

@app.route('/admin/set_champion', methods=['GET', 'POST'])
@login_required
def set_champion():
    conn = get_db()
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
            
        return redirect(url_for('set_champion'))

    campeao_atual = conn.execute('SELECT time_campeao, time_campeao_img FROM campeao_mundial LIMIT 1').fetchone()
    

    print("\n[LOG] Acessando página de definição de campeão\n")
    return render_template('set_champion.html', teams=all_teams_db, campeao_atual=campeao_atual)

@app.route('/campeao_geral')
def campeao_geral():
    conn = get_db()
    campeao_data = conn.execute("SELECT * FROM campeao_palpiteiros WHERE id = 1").fetchone()
    
    campeao = None
    if campeao_data:
        # Converte a linha do banco para um dicionário para podermos adicionar novos dados
        campeao = dict(campeao_data)
        total_jogos = campeao['acertos'] + campeao['erros']
        if total_jogos > 0:
            percentual = (campeao['acertos'] / total_jogos) * 100
            campeao['percentual_acertos'] = round(percentual, 1)
        else:
            campeao['percentual_acertos'] = 0

    return render_template('campeao_geral.html', campeao=campeao)

# Adicione esta nova rota de admin
@app.route('/admin/set_campeao_palpiteiro', methods=['POST'])
@login_required
def set_campeao_palpiteiro():
    conn = get_db()
    nome_campeao = request.form.get('campeao_nome')
    
    if not nome_campeao:
        flash('Nenhum jogador selecionado.', 'warning')
        return redirect(url_for('admin_dashboard'))

    # Busca os dados do jogador, incluindo o total de pontos calculado
    jogador_stats = conn.execute(
        "SELECT nome, acertos, erros, (pontos + pontos_bonus) as total_pontos FROM pontuacao WHERE nome = ?", 
        (nome_campeao,)
    ).fetchone()
    
    if not jogador_stats:
        flash('Jogador não encontrado.', 'danger')
        return redirect(url_for('admin_dashboard'))

    # Limpa a tabela para garantir um único campeão
    conn.execute("DELETE FROM campeao_palpiteiros")
    
    # Insere o novo campeão
    conn.execute(
        "INSERT INTO campeao_palpiteiros (id, nome, pontos, acertos, erros, data_definicao) VALUES (?, ?, ?, ?, ?, ?)",
        (1, jogador_stats['nome'], jogador_stats['total_pontos'], jogador_stats['acertos'], jogador_stats['erros'], datetime.now().strftime('%Y-%m-%d %H:%M'))
    )
    conn.commit()
    flash(f'{nome_campeao} foi definido como o Campeão dos Palpiteiros!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        init_db()
        conn = get_db()
        cursor = conn.cursor()
        print("\n" + "="*50)
        print("      INICIANDO APLICAÇÃO DE PALPITES")
        print("="*50 + "\n")
        for rodada_num, jogos_rodada in MUNDIAL_JOGOS_POR_RODADA.items():
            for jogo in jogos_rodada:
                cursor.execute("SELECT id FROM jogos WHERE id = ?", (jogo['id'],))
                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO jogos (id, rodada, time1_nome, time1_img, time1_sigla, time2_nome, time2_img, time2_sigla, data_hora, local, placar_time1, placar_time2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (jogo['id'], rodada_num, jogo['time1_nome'], jogo['time1_img'], jogo['time1_sigla'], jogo['time2_nome'], jogo['time2_img'], jogo['time2_sigla'], jogo['data_hora'], jogo['local'], None, None)
                    )
        conn.commit()


        try:
            hostname = socket.gethostname()
            ip_server = socket.gethostbyname(hostname)
        except socket.error as e:
            ip_server = '127.0.0.1' # IP de fallback caso não consiga encontrar
            print(f"[AVISO] Não foi possível obter o IP local: {e}. Usando {ip_server} como fallback.")

        print(f"[LOG - Main]: Servidor Flask rodando. Acesse nos seguintes endereços:")
        print(f"   - Na mesma máquina: http://127.0.0.1:3000")
        print(f"   - Em outros dispositivos na mesma rede: http://{ip_server}:3000")
        print("\nPressione CTRL+C para parar o servidor.")

        # O host '0.0.0.0' é essencial para permitir acessos de outros dispositivos na rede
        app.run(host="0.0.0.0", port=3000, debug=True)