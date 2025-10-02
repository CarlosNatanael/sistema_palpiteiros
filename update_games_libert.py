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
        # === SEMI FINAIS (IDA) - Rodada 5 ===
        {
          "id": 3025, "rodada": 5, "fase": "mata-mata", "confronto_id": 13,
          "time1_nome": "Flamengo", "time1_sigla": "FLA", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png",
          "time2_nome": "Racing", "time2_sigla": "RAC", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/wi-J-3U7th2bpIB_Uy9Euw_48x48.png",
          "data_hora": "2025-10-22 21:30", "local": "Maracanã"
        },
        {
          "id": 3026, "rodada": 5, "fase": "mata-mata", "confronto_id": 14,
          "time1_nome": "LDU", "time1_sigla": "LDU", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/Iuk3Emwfmii37cXTu4qJEQ_48x48.png",
          "time2_nome": "Palmeiras", "time2_sigla": "PAL", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png",
          "data_hora": "2025-10-23 21:30", "local": "Estadio Rodrigo Paz Delgado"
        },
        # === SEMI FINAIS (IDA) - Rodada 6 ===
        {
          "id": 3027, "rodada": 6, "fase": "mata-mata", "confronto_id": 13,
          "time1_nome": "Racing", "time1_sigla": "RAC", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/wi-J-3U7th2bpIB_Uy9Euw_48x48.png",
          "time2_nome": "Flamengo", "time2_sigla": "FLA", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png",
          "data_hora": "2025-10-29 21:30", "local": "El Cilindro"
        },
        {
          "id": 3028, "rodada": 6, "fase": "mata-mata", "confronto_id": 14,
          "time1_nome": "Palmeiras", "time1_sigla": "PAL", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png",
          "time2_nome": "LDU", "time2_sigla": "LDU", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/Iuk3Emwfmii37cXTu4qJEQ_48x48.png",
          "data_hora": "2025-10-30 21:30", "local": "Allianz Parque"
        },
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