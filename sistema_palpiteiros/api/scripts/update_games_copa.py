import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_DB_PATH = os.path.join(BASE_DIR, '..', 'api_data.db')


NOVOS_JOGOS_E_CAMPEONATOS = {
  "Copa do Mundo 2026": [
{
      "id": 2001, "rodada": 1, "fase": "grupos",
      "time1_nome": "México", "time1_sigla": "MEX", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/yJF9xqmUGenD8108FJbg9A_48x48.png",
      "time2_nome": "África do Sul", "time2_sigla": "RSA", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/EGwD4_SUlmwZWbnHhcmTPA_48x48.png",
      "data_hora": "2026-06-11 16:00", "local": "A definir"
    },
    {
      "id": 2002, "rodada": 1, "fase": "grupos",
      "time1_nome": "Coreia do Sul", "time1_sigla": "KOR", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/Uu5pwNmMHGd5bCooKrS3Lw_48x48.png",
      "time2_nome": "Tchéquia", "time2_sigla": "CZE", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/8AluO-WxpcHtC0KKHmFgvg_48x48.png",
      "data_hora": "2026-06-11 23:00", "local": "A definir"
    },
    {
      "id": 2003, "rodada": 2, "fase": "grupos",
      "time1_nome": "Canadá", "time1_sigla": "CAN", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/H23oIEP6qK-zNc3O8abnIA_48x48.png",
      "time2_nome": "Bósnia e Herzegovina", "time2_sigla": "BIH", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/em3xOvyKQEgz1IIYI8GO9w_48x48.png",
      "data_hora": "2026-06-12 16:00", "local": "A definir"
    },
    {
      "id": 2004, "rodada": 2, "fase": "grupos",
      "time1_nome": "Estados Unidos", "time1_sigla": "USA", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/wj9uZvn_vZrelLFGH8fnPA_48x48.png",
      "time2_nome": "Paraguai", "time2_sigla": "PAR", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/-FN-y84Al3dbth0hW1t5Qg_48x48.png",
      "data_hora": "2026-06-12 22:00", "local": "A definir"
    },
    {
      "id": 2005, "rodada": 3, "fase": "grupos",
      "time1_nome": "Catar", "time1_sigla": "QAT", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/h0FNA5YxLzWChHS5K0o4gw_48x48.png",
      "time2_nome": "Suíça", "time2_sigla": "SUI", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/1hy9ek4dOIffYULM6k1fqg_48x48.png",
      "data_hora": "2026-06-13 16:00", "local": "A definir"
    },
    {
      "id": 2006, "rodada": 3, "fase": "grupos",
      "time1_nome": "Brasil", "time1_sigla": "BRA", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/zKLzoJVYz0bb6oAnPUdwWQ_48x48.png",
      "time2_nome": "Marrocos", "time2_sigla": "MAR", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/I3gt2Ew39ux3GGdZ-4JE3g_48x48.png",
      "data_hora": "2026-06-13 19:00", "local": "A definir"
    },
    {
      "id": 2007, "rodada": 3, "fase": "grupos",
      "time1_nome": "Haiti", "time1_sigla": "HAI", "time1_img": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/AkMdqELoXN2wfYDvtMIQBQ_48x48.png",
      "time2_nome": "Escócia", "time2_sigla": "SCO", "time2_img": "https://ssl.gstatic.com/onebox/media/sports/logos/optimized/KNmWgtzC7DeN0X-OJEDsMA_48x48.png",
      "data_hora": "2026-06-13 22:00", "local": "A definir"
    }
  ]
}

def atualizar_banco_de_jogos():
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