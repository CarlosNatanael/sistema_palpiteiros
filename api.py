# api.py
import sqlite3
from flask import Flask, jsonify

DB_NAME = "api_data.db"
api_app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
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

# Não há mais nada no final do arquivo