from flask import Flask, jsonify
import sqlite3


# Inicializa a aplicação Flask que servirá como nossa API
api_app = Flask(__name__)
DB_NAME = "api_data.db"


def get_db_connection():
    """Cria uma conexão com o banco de dados da API."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ====================================================================
# ENDPOINTS DA API (AGORA LENDO DO BANCO DE DADOS)
# ====================================================================

@api_app.route('/api/v1/jogos', methods=['GET'])
def get_todos_jogos():
    """Endpoint para retornar TODOS os jogos de TODOS os campeonatos."""
    conn = get_db_connection()
    jogos_do_banco = conn.execute('SELECT * FROM jogos ORDER BY data_hora').fetchall()
    conn.close()
    
    # Converte os resultados do banco para uma lista de dicionários
    lista_de_jogos = [dict(jogo) for jogo in jogos_do_banco]
    return jsonify(lista_de_jogos)

@api_app.route('/api/v1/campeonatos', methods=['GET'])
def get_campeonatos():
    """Retorna a lista de nomes dos campeonatos disponíveis."""
    conn = get_db_connection()
    campeonatos = conn.execute('SELECT DISTINCT campeonato FROM jogos').fetchall()
    conn.close()
    lista_campeonatos = [row['campeonato'] for row in campeonatos]
    return jsonify(lista_campeonatos)

@api_app.route('/api/v1/jogos/<path:nome_campeonato>', methods=['GET'])
def get_jogos_por_campeonato(nome_campeonato):
    """Endpoint para retornar os jogos de um campeonato específico."""
    conn = get_db_connection()
    jogos_do_banco = conn.execute(
        'SELECT * FROM jogos WHERE campeonato = ? ORDER BY data_hora', 
        (nome_campeonato,)
    ).fetchall()
    conn.close()
    
    if not jogos_do_banco:
        return jsonify({"erro": "Campeonato não encontrado"}), 404
        
    lista_de_jogos = [dict(jogo) for jogo in jogos_do_banco]
    return jsonify(lista_de_jogos)

# ====================================================================
# INICIALIZAÇÃO DO SERVIDOR DA API
# ====================================================================