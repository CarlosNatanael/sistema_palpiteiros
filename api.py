import sqlite3
import os
from flask import Flask, jsonify

DB_NAME = "api_data.db"
api_app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'api_data.db')

def get_db_connection():
    # Use a variável DB_PATH com o caminho completo
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@api_app.route('/api/v1/jogos', methods=['GET'])
def get_todos_jogos():
    conn = get_db_connection()
    jogos = conn.execute('SELECT * FROM jogos ORDER BY data_hora').fetchall()
    conn.close()
    return jsonify([dict(row) for row in jogos])

@api_app.route('/api/v1/campeonatos', methods=['GET'])
def get_campeonatos():
    conn = get_db_connection()
    campeonatos = conn.execute('SELECT DISTINCT campeonato FROM jogos ORDER BY campeonato').fetchall()
    conn.close()
    return jsonify([row['campeonato'] for row in campeonatos])

# if __name__ == '__main__':
#     api_app.run(port=5001)