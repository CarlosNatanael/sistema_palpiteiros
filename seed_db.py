import sqlite3

# Nome do banco de dados que a API irá usar
DB_NAME = "api_data.db"

# ====================================================================
# FONTE DE DADOS CENTRALIZADA
# ====================================================================
# Edite esta lista para adicionar, remover ou alterar jogos.
# ====================================================================
DADOS_DOS_CAMPEONATOS = {
    "Brasileirão 2025": [
        # === RODADA 1 ======
        {
            'id': 2001, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Ceará', 'time1_sigla': 'CEA', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/mSl0cz3i2t8uv4zcprobOg_48x48.png',
            'time2_nome': 'Corinthians', 'time2_sigla': 'COR', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/tCMSqgXVHROpdCpQhzTo1g_48x48.png',
            'data_hora': '2025-07-16 19:00', 'local': 'Arena Castelão'
        },
        {
            'id': 2002, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Fluminense', 'time1_sigla': 'FLU', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/fCMxMMDF2AZPU7LzYKSlig_48x48.png',
            'time2_nome': 'Cruzeiro', 'time2_sigla': 'CRU', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/Tcv9X__nIh-6wFNJPMwIXQ_48x48.png',
            'data_hora': '2025-07-16 19:30', 'local': 'Maracanã'
        },
        {
            'id': 2003, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Juventude', 'time1_sigla': 'JUV', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/JrXw-m4Dov0gE2Sh6XJQMQ_48x48.png',
            'time2_nome': 'Vasco da Gama', 'time2_sigla': 'VAS', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/hHwT8LwRmYCAGxQ-STLxYA_48x48.png',
            'data_hora': '2025-07-16 20:00', 'local': 'Alfredo Jaconi'
        },
        {
            'id': 2004, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Bahia', 'time1_sigla': 'BAH', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/nIdbR6qIUDyZUBO9vojSPw_48x48.png',
            'time2_nome': 'Internacional', 'time2_sigla': 'INT', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/OWVFKuHrQuf4q2Wk0hEmSA_48x48.png',
            'data_hora': '2025-07-16 20:30', 'local': 'Arena Fonte Nova'
        },
        {
            'id': 2005, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Red Bull Bragantino', 'time1_sigla': 'BGT', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/lMyw2zn1Z4cdkaxKJWnsQw_48x48.png',
            'time2_nome': 'São Paulo', 'time2_sigla': 'SAO', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/4w2Z97Hf9CSOqICK3a8AxQ_48x48.png',
            'data_hora': '2025-07-16 21:30', 'local': 'Nabi Abi Chedid'
        },
        {
            'id': 2006, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Atlético-MG', 'time1_sigla': 'CAM', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/q9fhEsgpuyRq58OgmSndcQ_48x48.png',
            'time2_nome': 'Sport Recife', 'time2_sigla': 'SPO', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/u9Ydy0qt6JJjWhTaI6r10A_48x48.png',
            'data_hora': '2025-07-16 21:30', 'local': 'Arena MRV'
        },
        {
            'id': 2007, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Palmeiras', 'time1_sigla': 'PAL', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png',
            'time2_nome': 'Mirassol', 'time2_sigla': 'MIR', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/5J3JY7fcdiDYU5rbPW7AKA_48x48.png',
            'data_hora': '2025-07-16 21:30', 'local': 'Allianz Parque'
        },
        {
            'id': 2008, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Santos', 'time1_sigla': 'SAN', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/VHdNOT6wWOw_vJ38GMjMzg_48x48.png',
            'time2_nome': 'Flamengo', 'time2_sigla': 'FLA', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png',
            'data_hora': '2025-07-16 21:30', 'local': 'Vila Belmiro'
        },
        {
            'id': 2009, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Grêmio', 'time1_sigla': 'GRE', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/Ku-73v_TW9kpex-IEGb0ZA_48x48.png',
            'time2_nome': 'Fortaleza', 'time2_sigla': 'FOR', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/me10ephzRxdj45zVq1Risg_48x48.png',
            'data_hora': '2025-07-16 21:30', 'local': 'Arena do Grêmio'
        },
        {
            'id': 2010, 'rodada': 1, 'fase': 'grupos', 
            'time1_nome': 'Botafogo', 'time1_sigla': 'BOT', 'time1_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png',
            'time2_nome': 'Vitória', 'time2_sigla': 'VIT', 'time2_img': 'https://ssl.gstatic.com/onebox/media/sports/logos/LHSM6VchpkI4NIptoSTHOg_48x48.png',
            'data_hora': '2025-07-16 21:30', 'local': 'Estádio Nilton Santos'
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

def inicializar_e_popular_banco():
    """Cria o banco de dados e a tabela, e insere os jogos."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Cria a tabela de jogos (se ela não existir)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jogos (
        id INTEGER PRIMARY KEY,
        campeonato TEXT NOT NULL,
        rodada INTEGER NOT NULL,
        fase TEXT NOT NULL,
        time1_nome TEXT, time1_img TEXT, time1_sigla TEXT,
        time2_nome TEXT, time2_img TEXT, time2_sigla TEXT,
        data_hora TEXT,
        local TEXT
    )''')
    
    print(f"Populando o banco de dados '{DB_NAME}'...")
    jogos_inseridos = 0
    jogos_atualizados = 0

    # Itera sobre os dados e insere/atualiza no banco
    for campeonato, jogos in DADOS_DOS_CAMPEONATOS.items():
        for jogo in jogos:
            cursor.execute("SELECT id FROM jogos WHERE id = ?", (jogo['id'],))
            data = cursor.fetchone()
            if data is None:
                # Jogo não existe, insere novo
                cursor.execute("""
                    INSERT INTO jogos (id, campeonato, rodada, fase, time1_nome, time1_img, time1_sigla, 
                                       time2_nome, time2_img, time2_sigla, data_hora, local)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    jogo['id'], campeonato, jogo['rodada'], jogo['fase'],
                    jogo['time1_nome'], jogo['time1_img'], jogo['time1_sigla'],
                    jogo['time2_nome'], jogo['time2_img'], jogo['time2_sigla'],
                    jogo['data_hora'], jogo['local']
                ))
                jogos_inseridos += 1
            else:
                # Jogo já existe, atualiza (caso você mude algum dado)
                cursor.execute("""
                    UPDATE jogos SET campeonato=?, rodada=?, fase=?, time1_nome=?, time1_img=?, time1_sigla=?,
                                     time2_nome=?, time2_img=?, time2_sigla=?, data_hora=?, local=?
                    WHERE id=?
                """, (
                    campeonato, jogo['rodada'], jogo['fase'],
                    jogo['time1_nome'], jogo['time1_img'], jogo['time1_sigla'],
                    jogo['time2_nome'], jogo['time2_img'], jogo['time2_sigla'],
                    jogo['data_hora'], jogo['local'], jogo['id']
                ))
                jogos_atualizados += 1

    conn.commit()
    conn.close()
    
    print("\n--- Relatório ---")
    print(f"{jogos_inseridos} novo(s) jogo(s) inserido(s).")
    print(f"{jogos_atualizados} jogo(s) existente(s) foram verificados/atualizados.")
    print("Banco de dados populado com sucesso!")

if __name__ == '__main__':
    inicializar_e_popular_banco()