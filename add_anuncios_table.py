import sqlite3
import os

# Define o caminho completo para o banco de dados do app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'palpites.db')

def criar_tabela_anuncios():
    """Conecta ao banco de dados e cria a tabela 'anuncios' se ela não existir."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("Criando tabela 'anuncios'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anuncios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                tipo TEXT NOT NULL, -- Para a cor do alerta: 'success', 'info', 'warning'
                data_criacao TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        print("Tabela 'anuncios' verificada/criada com sucesso!")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro no banco de dados: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == '__main__':
    criar_tabela_anuncios()