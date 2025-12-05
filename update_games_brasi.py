import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_DB_PATH = os.path.join(BASE_DIR, 'api_data.db')

# ====================================================================
#  COLOQUE AQUI OS NOVOS JOGOS QUE VOCÊ QUER ADICIONAR OU ATUALIZAR
# ====================================================================
# APENAS OS JOGOS DO BRASILEIRÃO
NOVOS_JOGOS_E_CAMPEONATOS = {
  "Brasileirão 2025": [
    {
      "id": 2207, "rodada": 27, "fase": "grupos",
      "time1_nome": "Mirassol", "time1_sigla": "MIR", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/5J3JY7fcdiDYU5rbPW7AKA_48x48.png",
      "time2_nome": "Flamengo", "time2_sigla": "FLA", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png",
      "data_hora": "2025-12-06 18:30", "local": "Estádio José Maria de Campos Maia"
    },
    {
      "id": 2208, "rodada": 27, "fase": "grupos",
      "time1_nome": "Fluminense", "time1_sigla": "FLU", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/fCMxMMDF2AZPU7LzYKSlig_48x48.png",
      "time2_nome": "Bahia", "time2_sigla": "BAH", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/nIdbR6qIUDyZUBO9vojSPw_48x48.png",
      "data_hora": "2025-12-07 16:00", "local": "Maracanã"
    },
    {
      "id": 2209, "rodada": 27, "fase": "grupos",
      "time1_nome": "Ceará SC", "time1_sigla": "CEA", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/mSl0cz3i2t8uv4zcprobOg_48x48.png",
      "time2_nome": "Palmeiras", "time2_sigla": "PAL", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png",
      "data_hora": "2025-12-07 16:00", "local": "Arena Castelão"
    },
    {
      "id": 2210, "rodada": 27, "fase": "grupos",
      "time1_nome": "Corinthians", "time1_sigla": "COR", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/tCMSqgXVHROpdCpQhzTo1g_48x48.png",
      "time2_nome": "Juventude", "time2_sigla": "JUV", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/JrXw-m4Dov0gE2Sh6XJQMQ_48x48.png",
      "data_hora": "2025-12-07 16:00", "local": "Neo Química Arena"
    },
    {
      "id": 2211, "rodada": 27, "fase": "grupos",
      "time1_nome": "Santos", "time1_sigla": "SAN", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/VHdNOT6wWOw_vJ38GMjMzg_48x48.png",
      "time2_nome": "Cruzeiro", "time2_sigla": "CRU", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/Tcv9X__nIh-6wFNJPMwIXQ_48x48.png",
      "data_hora": "2025-12-07 16:00", "local": "Vila Belmiro"
    },
    {
      "id": 2212, "rodada": 27, "fase": "grupos",
      "time1_nome": "Sport Recife", "time1_sigla": "SPO", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/u9Ydy0qt6JJjWhTaI6r10A_48x48.png",
      "time2_nome": "Grêmio", "time2_sigla": "GRE", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/Ku-73v_TW9kpex-IEGb0ZA_48x48.png",
      "data_hora": "2025-12-07 16:00", "local": "Ilha do Retiro"
    },
    {
      "id": 2213, "rodada": 27, "fase": "grupos",
      "time1_nome": "EC Vitória", "time1_sigla": "VIT", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/LHSM6VchpkI4NIptoSTHOg_48x48.png",
      "time2_nome": "São Paulo", "time2_sigla": "SAO", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/4w2Z97Hf9CSOqICK3a8AxQ_48x48.png",
      "data_hora": "2025-12-07 16:00", "local": "Barradão"
    },
    {
      "id": 2214, "rodada": 27, "fase": "grupos",
      "time1_nome": "Botafogo", "time1_sigla": "BOT", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png",
      "time2_nome": "Fortaleza", "time2_sigla": "FOR", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/me10ephzRxdj45zVq1Risg_48x48.png",
      "data_hora": "2025-12-07 16:00", "local": "Nilton Santos"
    },
    {
      "id": 2215, "rodada": 27, "fase": "grupos",
      "time1_nome": "Atlético-MG", "time1_sigla": "CAM", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/q9fhEsgpuyRq58OgmSndcQ_48x48.png",
      "time2_nome": "Vasco da Gama", "time2_sigla": "VAS", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/hHwT8LwRmYCAGxQ-STLxYA_48x48.png",
      "data_hora": "2025-12-07 16:00", "local": "Arena MRV"
    },
    {
      "id": 2216, "rodada": 27, "fase": "grupos",
      "time1_nome": "Internacional", "time1_sigla": "INT", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/OWVFKuHrQuf4q2Wk0hEmSA_48x48.png",
      "time2_nome": "Bragantino", "time2_sigla": "BGT", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/lMyw2zn1Z4cdkaxKJWnsQw_48x48.png",
      "data_hora": "2025-12-07 16:00", "local": "Beira-Rio"
    }
  ]
}

def atualizar_banco_de_jogos():
    """
    Conecta ao banco de dados da API e insere ou atualiza os jogos
    definidos em NOVOS_JOGOS_E_CAMPEONATOS.
    """
    print(f"--- Conectando ao banco de dados da API em: {API_DB_PATH} ---")
    try:
        conn = sqlite3.connect(API_DB_PATH)
        cursor = conn.cursor()

        jogos_inseridos = 0
        jogos_atualizados = 0

        for campeonato, jogos in NOVOS_JOGOS_E_CAMPEONATOS.items():
            for jogo in jogos:
                cursor.execute("SELECT id FROM jogos WHERE id = ?", (jogo['id'],))
                data = cursor.fetchone()

                if data is None:
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

        print("\n--- Relatório da Atualização ---")
        print(f"{jogos_inseridos} novo(s) jogo(s) inserido(s).")
        print(f"{jogos_atualizados} jogo(s) existente(s) foram atualizados.")
        print("Banco de dados da API atualizado com sucesso!")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao acessar o banco de dados: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


if __name__ == '__main__':
    atualizar_banco_de_jogos()