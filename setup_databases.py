import sqlite3
import os

# --- Nomes dos bancos de dados ---
API_DB_NAME = 'api_data.db'
APP_DB_NAME = 'palpites.db'

# --- Dados dos jogos para popular a API ---
DADOS_DOS_CAMPEONATOS = {
    "Brasileirão 2025": [
        # === RODADA 1 ======
        {
            'id': 2001, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Ceará', 'time1_sigla': 'CEA', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/mSl0cz3i2t8uv4zcprobOg_48x48.png',
            'time2_nome': 'Corinthians', 'time2_sigla': 'COR', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/tCMSqgXVHROpdCpQhzTo1g_48x48.png',
            'data_hora': '2025-07-17 10:00', 'local': 'Arena Castelão'
        },
        {
            'id': 2002, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Fluminense', 'time1_sigla': 'FLU', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/fCMxMMDF2AZPU7LzYKSlig_48x48.png',
            'time2_nome': 'Cruzeiro', 'time2_sigla': 'CRU', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/Tcv9X__nIh-6wFNJPMwIXQ_48x48.png',
            'data_hora': '2025-07-17 19:30', 'local': 'Maracanã'
        },
        {
            'id': 2003, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Red Bull Bragantino', 'time1_sigla': 'BGT', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/lMyw2zn1Z4cdkaxKJWnsQw_48x48.png',
            'time2_nome': 'São Paulo', 'time2_sigla': 'SAO', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/4w2Z97Hf9CSOqICK3a8AxQ_48x48.png',
            'data_hora': '2025-07-17 10:00', 'local': 'Nabi Abi Chedid'
        },
        {
            'id': 2004, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Palmeiras', 'time1_sigla': 'PAL', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png',
            'time2_nome': 'Mirassol', 'time2_sigla': 'MIR', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/5J3JY7fcdiDYU5rbPW7AKA_48x48.png',
            'data_hora': '2025-07-17 10:00', 'local': 'Allianz Parque'
        },
        {
            'id': 2005, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Santos', 'time1_sigla': 'SAN', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/VHdNOT6wWOw_vJ38GMjMzg_48x48.png',
            'time2_nome': 'Flamengo', 'time2_sigla': 'FLA', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png',
            'data_hora': '2025-07-17 10:00', 'local': 'Vila Belmiro'
        },
        {
            'id': 2006, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Botafogo', 'time1_sigla': 'BOT', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png',
            'time2_nome': 'Vitória', 'time2_sigla': 'VIT', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/LHSM6VchpkI4NIptoSTHOg_48x48.png',
            'data_hora': '2025-07-17 10:00', 'local': 'Estádio Nilton Santos'
        },
        # === RODADA 2 ======
        {
            "id": 2007, "rodada": 2, "fase": "grupos",
            "time1_nome": "Fortaleza", "time1_sigla": "FOR", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/me10ephzRxdj45zVq1Risg_48x48.png",
            "time2_nome": "Bahia", "time2_sigla": "BAH", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/nIdbR6qIUDyZUBO9vojSPw_48x48.png",
            "data_hora": "2025-07-19 16:00", "local": "Arena Castelão"
        },
        {
            "id": 2008, "rodada": 2, "fase": "grupos",
            "time1_nome": "Vasco da Gama", "time1_sigla": "VAS", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/hHwT8LwRmYCAGxQ-STLxYA_48x48.png",
            "time2_nome": "Grêmio", "time2_sigla": "GRE", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/Ku-73v_TW9kpex-IEGb0ZA_48x48.png",
            "data_hora": "2025-07-19 17:30", "local": "São Januário"
        },
        {
            "id": 2009, "rodada": 2, "fase": "grupos",
            "time1_nome": "Mirassol", "time1_sigla": "MIR", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/5J3JY7fcdiDYU5rbPW7AKA_48x48.png",
            "time2_nome": "Santos", "time2_sigla": "SAN", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/VHdNOT6wWOw_vJ38GMjMzg_48x48.png",
            "data_hora": "2025-07-19 18:30", "local": "Estádio José Maria de Campos Maia"
        },
        {
            "id": 2010, "rodada": 2, "fase": "grupos",
            "time1_nome": "São Paulo", "time1_sigla": "SAO", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/4w2Z97Hf9CSOqICK3a8AxQ_48x48.png",
            "time2_nome": "Corinthians", "time2_sigla": "COR", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/tCMSqgXVHROpdCpQhzTo1g_48x48.png",
            "data_hora": "2025-07-19 21:00", "local": "Morumbis"
        },
        {
            "id": 2011, "rodada": 2, "fase": "grupos",
            "time1_nome": "Internacional", "time1_sigla": "INT", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/OWVFKuHrQuf4q2Wk0hEmSA_48x48.png",
            "time2_nome": "Ceará SC", "time2_sigla": "CEA", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/mSl0cz3i2t8uv4zcprobOg_48x48.png",
            "data_hora": "2025-07-20 11:00", "local": "Beira-Rio"
        },
        {
            "id": 2012, "rodada": 2, "fase": "grupos",
            "time1_nome": "EC Vitória", "time1_sigla": "VIT", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/LHSM6VchpkI4NIptoSTHOg_48x48.png",
            "time2_nome": "Bragantino", "time2_sigla": "BGT", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/lMyw2zn1Z4cdkaxKJWnsQw_48x48.png",
            "data_hora": "2025-07-20 16:00", "local": "Barradão"
        },
        {
            "id": 2013, "rodada": 2, "fase": "grupos",
            "time1_nome": "Cruzeiro", "time1_sigla": "CRU", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/Tcv9X__nIh-6wFNJPMwIXQ_48x48.png",
            "time2_nome": "Juventude", "time2_sigla": "JUV", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/JrXw-m4Dov0gE2Sh6XJQMQ_48x48.png",
            "data_hora": "2025-07-20 16:00", "local": "Mineirão"
        },
        {
            "id": 2014, "rodada": 2, "fase": "grupos",
            "time1_nome": "Sport Recife", "time1_sigla": "SPO", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/u9Ydy0qt6JJjWhTaI6r10A_48x48.png",
            "time2_nome": "Botafogo", "time2_sigla": "BOT", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png",
            "data_hora": "2025-07-20 17:30", "local": "Ilha do Retiro"
        },
        {
            "id": 2015, "rodada": 2, "fase": "grupos",
            "time1_nome": "Palmeiras", "time1_sigla": "PAL", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png",
            "time2_nome": "Atlético-MG", "time2_sigla": "CAM", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/q9fhEsgpuyRq58OgmSndcQ_48x48.png",
            "data_hora": "2025-07-20 17:30", "local": "Allianz Parque"
        },
        {
            "id": 2016, "rodada": 2, "fase": "grupos",
            "time1_nome": "Flamengo", "time1_sigla": "FLA", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png",
            "time2_nome": "Fluminense", "time2_sigla": "FLU", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/fCMxMMDF2AZPU7LzYKSlig_48x48.png",
            "data_hora": "2025-07-20 19:30", "local": "Maracanã"
        }
    ],
    "Libertadores 2025": [
        # === OITAVAS DE FINAL (IDA) ===
        {
          "id": 3001, "rodada": 1, "fase": "mata-mata",
          "time1_nome": "Fortaleza", "time1_sigla": "FOR", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/me10ephzRxdj45zVq1Risg_48x48.png",
          "time2_nome": "Vélez Sarsfield", "time2_sigla": "VEL", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/EG7pVKQAW2mvbnKsMoMbYA_48x48.png",
          "data_hora": "2025-08-13 19:00", "local": "Arena Castelão"
        },
        {
          "id": 3002, "rodada": 1, "fase": "mata-mata",
          "time1_nome": "Peñarol", "time1_sigla": "PEN", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/dO-HNzx-ozLofoWOj7kr9g_48x48.png",
          "time2_nome": "Racing", "time2_sigla": "RAC", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/wi-J-3U7th2bpIB_Uy9Euw_48x48.png",
          "data_hora": "2025-08-13 21:30", "local": "Campeón del Siglo"
        },
        {
          "id": 3003, "rodada": 1, "fase": "mata-mata",
          "time1_nome": "Atlético Nacional", "time1_sigla": "ATL", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/i6-Yda76iPfeYEg4JcNbuw_48x48.png",
          "time2_nome": "São Paulo", "time2_sigla": "SAO", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/4w2Z97Hf9CSOqICK3a8AxQ_48x48.png",
          "data_hora": "2025-08-13 21:30", "local": "Atanasio Girardot"
        },
        {
          "id": 3004, "rodada": 1, "fase": "mata-mata",
          "time1_nome": "Botafogo", "time1_sigla": "BOT", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png",
          "time2_nome": "LDU", "time2_sigla": "LDU", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/Iuk3Emwfmii37cXTu4qJEQ_48x48.png",
          "data_hora": "2025-08-14 19:00", "local": "Nilton Santos"
        },
        {
          "id": 3005, "rodada": 1, "fase": "mata-mata",
          "time1_nome": "Libertad", "time1_sigla": "LIB", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/-n4YxXgf_vhcYhp03Mq6Dw_48x48.png",
          "time2_nome": "River Plate", "time2_sigla": "RIV", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/700Mj6lUNkbBdvOVEbjC3g_48x48.png",
          "data_hora": "2025-08-14 21:30", "local": "Defensores del Chaco"
        },
        {
          "id": 3006, "rodada": 1, "fase": "mata-mata",
          "time1_nome": "Flamengo", "time1_sigla": "FLA", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png",
          "time2_nome": "Internacional", "time2_sigla": "INT", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/OWVFKuHrQuf4q2Wk0hEmSA_48x48.png",
          "data_hora": "2025-08-14 21:30", "local": "Maracanã"
        },
        {
          "id": 3007, "rodada": 1, "fase": "mata-mata",
          "time1_nome": "Universitario", "time1_sigla": "UNI", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/HfG2HscVnIAKV-aSmLcY-A_48x48.png",
          "time2_nome": "Palmeiras", "time2_sigla": "PAL", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png",
          "data_hora": "2025-08-15 21:00", "local": "Estadio Monumental"
        },
        {
          "id": 3008, "rodada": 1, "fase": "mata-mata",
          "time1_nome": "Cerro Porteño", "time1_sigla": "CER", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/q_2P3cWhPBE6a_0bB-xLAQ_48x48.png",
          "time2_nome": "Estudiantes", "time2_sigla": "EST", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/nDfL4YLZSNWXZniXushVag_48x48.png",
          "data_hora": "2025-08-15 21:00", "local": "La Nueva Olla"
        }
    ]
}

def setup_api_database():
    print(f"--- Configurando Banco de Dados da API: {API_DB_NAME} ---")
    if os.path.exists(API_DB_NAME): os.remove(API_DB_NAME)
    
    conn = sqlite3.connect(API_DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE jogos (id INTEGER PRIMARY KEY, campeonato TEXT, rodada INTEGER, fase TEXT, time1_nome TEXT, time1_img TEXT, time1_sigla TEXT, time2_nome TEXT, time2_img TEXT, time2_sigla TEXT, data_hora TEXT, local TEXT)''')
    for campeonato, jogos in DADOS_DOS_CAMPEONATOS.items():
        for jogo in jogos:
            cursor.execute("INSERT INTO jogos VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (jogo['id'], campeonato, jogo['rodada'], jogo['fase'], jogo['time1_nome'], jogo['time1_img'], jogo['time1_sigla'], jogo['time2_nome'], jogo['time2_img'], jogo['time2_sigla'], jogo['data_hora'], jogo['local']))
    conn.commit()
    conn.close()
    print("Banco da API configurado.")

def setup_app_database():
    print(f"--- Configurando Banco de Dados da Aplicação: {APP_DB_NAME} ---")
    if os.path.exists(APP_DB_NAME): os.remove(APP_DB_NAME)
    
    conn = sqlite3.connect(APP_DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE jogos (id INTEGER PRIMARY KEY, placar_time1 INTEGER, placar_time2 INTEGER, status TEXT, time_que_avancou TEXT)''')
    cursor.execute('''CREATE TABLE pontuacao (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE, pontos INTEGER DEFAULT 0, acertos INTEGER DEFAULT 0, erros INTEGER DEFAULT 0, pontos_bonus INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE palpites (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, rodada INTEGER, game_id INTEGER, time1 TEXT, time2 TEXT, gol_time1 INTEGER, gol_time2 INTEGER, resultado TEXT, status TEXT, quem_avanca TEXT)''')
    cursor.execute('''CREATE TABLE palpite_campeao (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, campeonato TEXT, time_campeao TEXT, time_campeao_img TEXT, data_palpite TEXT)''')
    cursor.execute('''CREATE TABLE campeao_real (id INTEGER PRIMARY KEY AUTOINCREMENT, campeonato TEXT UNIQUE, time_campeao TEXT, time_campeao_img TEXT, data_definicao TEXT)''')
    cursor.execute('''CREATE TABLE campeao_palpiteiros (id INTEGER PRIMARY KEY AUTOINCREMENT, temporada TEXT UNIQUE, competicao TEXT, nome TEXT, pontos INTEGER, acertos INTEGER, erros INTEGER, data_definicao TEXT)''')
    
    # --- INÍCIO DA SEÇÃO ADICIONADA: DADOS HISTÓRICOS ---
    campeao_temporada_1 = {
        'temporada': '1ª Temporada',
        'competicao': 'Super Mundial da FIFA',
        'nome': 'Lucas',
        'pontos': 71,
        'acertos': 33,
        'erros': 25,
        'data_definicao': '2025-07-13 00:00:00'
    }
    
    try:
        cursor.execute("""
            INSERT INTO campeao_palpiteiros (temporada, competicao, nome, pontos, acertos, erros, data_definicao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            campeao_temporada_1['temporada'],
            campeao_temporada_1['competicao'],
            campeao_temporada_1['nome'],
            campeao_temporada_1['pontos'],
            campeao_temporada_1['acertos'],
            campeao_temporada_1['erros'],
            campeao_temporada_1['data_definicao']
        ))
        print("-> Campeão histórico (1ª Temporada) inserido com sucesso!")
    except sqlite3.IntegrityError:
        print("-> Campeão histórico (1ª Temporada) já existe no banco de dados.")
    # --- FIM DA SEÇÃO ADICIONADA ---

    conn.commit()
    conn.close()
    print("Banco da Aplicação configurado.")
    
if __name__ == '__main__':
    print("Iniciando configuração completa dos bancos de dados...")
    setup_api_database()
    setup_app_database()
    print("\nConfiguração finalizada com sucesso!")