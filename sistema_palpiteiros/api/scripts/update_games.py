import sqlite3
import os
import json
import unicodedata

# Pega o diretório atual onde o script está rodando (api/scripts)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# O banco está uma pasta para trás (api/)
API_DB_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'api_data.db'))

# O textos.json está duas pastas para trás, e depois entra em utils/
TEXTOS_JSON_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'utils', 'textos.json'))

# O jogos.json vai ficar na mesma pasta que este script (api/scripts/)
JOGOS_JSON_PATH = os.path.join(BASE_DIR, 'jogos.json')


def normalizar_nome(nome):
    """
    Remove acentos, espaços extras e deixa tudo em minúsculo.
    """
    if not nome: return ""
    nome_sem_acento = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    return nome_sem_acento.strip().lower()

def carregar_dicionario_logos():
    try:
        with open(TEXTOS_JSON_PATH, 'r', encoding='utf-8') as f:
            dados_logos = json.load(f)
            
        dicionario = {}
        for item in dados_logos:
            nome_norm = normalizar_nome(item['titulo'])
            link_img = item['texto'][0]
            dicionario[nome_norm] = link_img
            
        return dicionario
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em '{TEXTOS_JSON_PATH}'!")
        return {}

def atualizar_banco_de_jogos():
    logos_corretos = carregar_dicionario_logos()
    if not logos_corretos:
        return 

    try:
        with open(JOGOS_JSON_PATH, 'r', encoding='utf-8') as f:
            novos_jogos_e_campeonatos = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Crie o arquivo '{JOGOS_JSON_PATH}' com os dados do importador primeiro!")
        return

    print(f"--- Conectando ao banco de dados em: {API_DB_PATH} ---")
    try:
        conn = sqlite3.connect(API_DB_PATH)
        cursor = conn.cursor()

        # Garante que a coluna confronto_id existe na tabela (proteção contra
        # bancos antigos que ainda não tinham essa coluna)
        cursor.execute("PRAGMA table_info(jogos)")
        colunas_existentes = [col[1] for col in cursor.fetchall()]
        if 'confronto_id' not in colunas_existentes:
            print("Coluna 'confronto_id' não existe na tabela 'jogos'. Criando agora...")
            cursor.execute("ALTER TABLE jogos ADD COLUMN confronto_id INTEGER")
            conn.commit()

        jogos_inseridos = 0
        jogos_atualizados = 0

        for campeonato, jogos in novos_jogos_e_campeonatos.items():
            for jogo in jogos:
                
                # Cruza os nomes para buscar as imagens corretas
                nome_t1_norm = normalizar_nome(jogo['time1_nome'])
                if nome_t1_norm in logos_corretos:
                    jogo['time1_img'] = logos_corretos[nome_t1_norm]
                else:
                    print(f"⚠️ Aviso: Logo não encontrado no textos.json para: '{jogo['time1_nome']}'")

                nome_t2_norm = normalizar_nome(jogo['time2_nome'])
                if nome_t2_norm in logos_corretos:
                    jogo['time2_img'] = logos_corretos[nome_t2_norm]
                else:
                    print(f"⚠️ Aviso: Logo não encontrado no textos.json para: '{jogo['time2_nome']}'")

                # Pega o confronto_id do JSON (pode não existir em jogos de fase de grupos)
                confronto_id = jogo.get('confronto_id')

                # Inserção ou Atualização no BD
                cursor.execute("SELECT id FROM jogos WHERE id = ?", (jogo['id'],))
                data = cursor.fetchone()

                if data is None:
                    cursor.execute("""
                        INSERT INTO jogos (id, campeonato, rodada, fase, confronto_id, time1_nome, time1_img, time1_sigla,
                                           time2_nome, time2_img, time2_sigla, data_hora, local)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        jogo['id'], campeonato, jogo['rodada'], jogo['fase'], confronto_id,
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
                        campeonato, jogo['rodada'], jogo['fase'], confronto_id,
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

    except sqlite3.Error as e:
        print(f"Ocorreu um erro no SQLite: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == '__main__':
    atualizar_banco_de_jogos()