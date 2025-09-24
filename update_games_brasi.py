import sqlite3
import os

# --- Define o caminho absoluto para o banco de dados da API ---
# Usar o caminho completo evita qualquer erro de diretório no PythonAnywhere
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_DB_PATH = os.path.join(BASE_DIR, 'api_data.db')

# ====================================================================
#  COLOQUE AQUI OS NOVOS JOGOS QUE VOCÊ QUER ADICIONAR OU ATUALIZAR
# ====================================================================
# APENAS OS JOGOS DO BRASILEIRÃO
NOVOS_JOGOS_E_CAMPEONATOS = {
  "Brasileirão 2025": [
    {
      "id": 2100, "rodada": 14, "fase": "grupos",
      "time1_nome": "Vasco da Gama", "time1_sigla": "VAS", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/hHwT8LwRmYCAGxQ-STLxYA_48x48.png",
      "time2_nome": "Bahia", "time2_sigla": "BAH", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/nIdbR6qIUDyZUBO9vojSPw_48x48.png",
      "data_hora": "2025-09-24 19:30", "local": "São Januário"
    },
    {
      "id": 2101, "rodada": 14, "fase": "grupos",
      "time1_nome": "Grêmio", "time1_sigla": "GRE", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/Ku-73v_TW9kpex-IEGb0ZA_48x48.png",
      "time2_nome": "Botafogo", "time2_sigla": "BOT", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png",
      "data_hora": "2025-09-24 19:30", "local": "Arena do Grêmio"
    },
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