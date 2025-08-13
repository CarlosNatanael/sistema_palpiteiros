import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_DB_PATH = os.path.join(BASE_DIR, 'api_data.db')

# ====================================================================
#  COLOQUE AQUI OS NOVOS JOGOS QUE VOCÊ QUER ADICIONAR OU ATUALIZAR
# ====================================================================
# APENAS OS JOGOS DO LIBERTADORES
NOVOS_JOGOS_E_CAMPEONATOS = {
    "Libertadores 2025": [
        # === OITAVAS DE FINAL (IDA) ===
        {
          "id": 3001, "rodada": 1, "fase": "mata-mata", "confronto_id": 1,
          "time1_nome": "Fortaleza", "time1_sigla": "FOR", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/me10ephzRxdj45zVq1Risg_48x48.png",
          "time2_nome": "Vélez Sarsfield", "time2_sigla": "VEL", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/EG7pVKQAW2mvbnKsMoMbYA_48x48.png",
          "data_hora": "2025-08-12 19:00", "local": "Arena Castelão"
        },
        {
          "id": 3002, "rodada": 1, "fase": "mata-mata", "confronto_id": 2,
          "time1_nome": "Peñarol", "time1_sigla": "PEN", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/dO-HNzx-ozLofoWOj7kr9g_48x48.png",
          "time2_nome": "Racing", "time2_sigla": "RAC", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/wi-J-3U7th2bpIB_Uy9Euw_48x48.png",
          "data_hora": "2025-08-12 21:30", "local": "Campeón del Siglo"
        },
        {
          "id": 3003, "rodada": 1, "fase": "mata-mata", "confronto_id": 3,
          "time1_nome": "Atlético Nacional", "time1_sigla": "ATL", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/i6-Yda76iPfeYEg4JcNbuw_48x48.png",
          "time2_nome": "São Paulo", "time2_sigla": "SAO", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/4w2Z97Hf9CSOqICK3a8AxQ_48x48.png",
          "data_hora": "2025-08-12 21:30", "local": "Atanasio Girardot"
        },
        {
          "id": 3004, "rodada": 1, "fase": "mata-mata", "confronto_id": 4,
          "time1_nome": "Botafogo", "time1_sigla": "BOT", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png",
          "time2_nome": "LDU", "time2_sigla": "LDU", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/Iuk3Emwfmii37cXTu4qJEQ_48x48.png",
          "data_hora": "2025-08-14 19:00", "local": "Nilton Santos"
        },
        {
          "id": 3005, "rodada": 1, "fase": "mata-mata", "confronto_id": 5,
          "time1_nome": "Libertad", "time1_sigla": "LIB", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/-n4YxXgf_vhcYhp03Mq6Dw_48x48.png",
          "time2_nome": "River Plate", "time2_sigla": "RIV", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/700Mj6lUNkbBdvOVEbjC3g_48x48.png",
          "data_hora": "2025-08-14 21:30", "local": "Defensores del Chaco"
        },
        {
          "id": 3006, "rodada": 1, "fase": "mata-mata", "confronto_id": 6,
          "time1_nome": "Flamengo", "time1_sigla": "FLA", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png",
          "time2_nome": "Internacional", "time2_sigla": "INT", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/OWVFKuHrQuf4q2Wk0hEmSA_48x48.png",
          "data_hora": "2025-08-13 21:30", "local": "Maracanã"
        },
        {
          "id": 3007, "rodada": 1, "fase": "mata-mata", "confronto_id": 7,
          "time1_nome": "Universitario", "time1_sigla": "UNI", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/HfG2HscVnIAKV-aSmLcY-A_48x48.png",
          "time2_nome": "Palmeiras", "time2_sigla": "PAL", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png",
          "data_hora": "2025-08-14 21:00", "local": "Estadio Monumental"
        },
        {
          "id": 3008, "rodada": 1, "fase": "mata-mata", "confronto_id": 8,
          "time1_nome": "Cerro Porteño", "time1_sigla": "CER", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/q_2P3cWhPBE6a_0bB-xLAQ_48x48.png",
          "time2_nome": "Estudiantes", "time2_sigla": "EST", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/nDfL4YLZSNWXZniXushVag_48x48.png",
          "data_hora": "2025-08-13 21:00", "local": "La Nueva Olla"
        },
        # === OITAVAS DE FINAL - VOLTA (Rodada 2) ===
        {
          "id": 3009, "rodada": 2, "fase": "mata-mata", "confronto_id": 1,
          "time1_nome": "Vélez Sarsfield", "time1_sigla": "VEL", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/EG7pVKQAW2mvbnKsMoMbYA_48x48.png",
          "time2_nome": "Fortaleza", "time2_sigla": "FOR", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/me10ephzRxdj45zVq1Risg_48x48.png",
          "data_hora": "2025-08-19 19:00", "local": "Estadio José Amalfitani"
        },
        {
          "id": 3010, "rodada": 2, "fase": "mata-mata", "confronto_id": 2,
          "time1_nome": "Racing", "time1_sigla": "RAC", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/wi-J-3U7th2bpIB_Uy9Euw_48x48.png",
          "time2_nome": "Peñarol", "time2_sigla": "PEN", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/dO-HNzx-ozLofoWOj7kr9g_48x48.png",
          "data_hora": "2025-08-19 21:30", "local": "El Cilindro"
        },
        {
          "id": 3011, "rodada": 2, "fase": "mata-mata", "confronto_id": 3,
          "time1_nome": "São Paulo", "time1_sigla": "SAO", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/4w2Z97Hf9CSOqICK3a8AxQ_48x48.png",
          "time2_nome": "Atlético Nacional", "time2_sigla": "ATL", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/i6-Yda76iPfeYEg4JcNbuw_48x48.png",
          "data_hora": "2025-08-19 21:30", "local": "Morumbis"
        },
        {
          "id": 3012, "rodada": 2, "fase": "mata-mata", "confronto_id": 8,
          "time1_nome": "Estudiantes", "time1_sigla": "EST", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/nDfL4YLZSNWXZniXushVag_48x48.png",
          "time2_nome": "Cerro Porteño", "time2_sigla": "CER", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/q_2P3cWhPBE6a_0bB-xLAQ_48x48.png",
          "data_hora": "2025-08-20 19:00", "local": "Estadio Jorge Luis Hirschi"
        },
        {
          "id": 3013, "rodada": 2, "fase": "mata-mata", "confronto_id": 6,
          "time1_nome": "Internacional", "time1_sigla": "INT", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/OWVFKuHrQuf4q2Wk0hEmSA_48x48.png",
          "time2_nome": "Flamengo", "time2_sigla": "FLA", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png",
          "data_hora": "2025-08-20 21:30", "local": "Beira-Rio"
        },
        {
          "id": 3014, "rodada": 2, "fase": "mata-mata", "confronto_id": 4,
          "time1_nome": "LDU Quito", "time1_sigla": "LDU", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/Iuk3Emwfmii37cXTu4qJEQ_48x48.png",
          "time2_nome": "Botafogo", "time2_sigla": "BOT", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png",
          "data_hora": "2025-08-21 19:00", "local": "Estadio Rodrigo Paz Delgado"
        },
        {
          "id": 3015, "rodada": 2, "fase": "mata-mata", "confronto_id": 5,
          "time1_nome": "River Plate", "time1_sigla": "RIV", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/700Mj6lUNkbBdvOVEbjC3g_48x48.png",
          "time2_nome": "Libertad", "time2_sigla": "LIB", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/-n4YxXgf_vhcYhp03Mq6Dw_48x48.png",
          "data_hora": "2025-08-21 21:30", "local": "Monumental de Núñez"
        },
        {
          "id": 3016, "rodada": 2, "fase": "mata-mata", "confronto_id": 7,
          "time1_nome": "Palmeiras", "time1_sigla": "PAL", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png",
          "time2_nome": "Universitario", "time2_sigla": "UNI", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/HfG2HscVnIAKV-aSmLcY-A_48x48.png",
          "data_hora": "2025-08-21 21:30", "local": "Allianz Parque"
        }
    ]
}

def atualizar_banco_de_jogos():
    """Conecta ao banco de dados e insere ou atualiza os jogos."""
    print(f"--- Conectando ao banco de dados da API em: {API_DB_PATH} ---")
    try:
        conn = sqlite3.connect(API_DB_PATH)
        cursor = conn.cursor()
        jogos_inseridos, jogos_atualizados = 0, 0

        for campeonato, jogos in NOVOS_JOGOS_E_CAMPEONATOS.items():
            for jogo in jogos:
                cursor.execute("SELECT id FROM jogos WHERE id = ?", (jogo['id'],))
                data = cursor.fetchone()

                if data is None:
                    cursor.execute("""
                        INSERT INTO jogos (id, campeonato, rodada, fase, confronto_id, time1_nome, time1_img, time1_sigla,
                                           time2_nome, time2_img, time2_sigla, data_hora, local)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        jogo['id'], campeonato, jogo['rodada'], jogo['fase'], jogo.get('confronto_id'),
                        jogo['time1_nome'], jogo['time1_img'], jogo['time1_sigla'],
                        jogo['time2_nome'], jogo['time2_img'], jogo['time2_sigla'],
                        jogo['data_hora'], jogo['local']
                    ))
                    jogos_inseridos += 1
                else:
                    cursor.execute("""
                        UPDATE jogos SET campeonato=?, rodada=?, fase=?, confronto_id=?, time1_nome=?, time1_img=?, time1_sigla=?,
                                         time2_nome=?, time2_img=?, time2_sigla=?, data_hora=?, local=?
                        WHERE id=?
                    """, (
                        campeonato, jogo['rodada'], jogo['fase'], jogo.get('confronto_id'),
                        jogo['time1_nome'], jogo['time1_img'], jogo['time1_sigla'],
                        jogo['time2_nome'], jogo['time2_img'], jogo['time2_sigla'],
                        jogo['data_hora'], jogo['local'], jogo['id']
                    ))
                    jogos_atualizados += 1

        conn.commit()
        conn.close()
        print("\n--- Relatório da Atualização ---")
        print(f"{jogos_inseridos} novo(s) jogo(s) inserido(s).")
        print(f"{jogos_atualizados} jogo(s) existente(s) foram atualizados.")
        print("Banco de dados da API atualizado com sucesso!")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao acessar o banco de dados: {e}")

if __name__ == '__main__':
    atualizar_banco_de_jogos()