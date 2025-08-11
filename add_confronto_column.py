# add_confronto_column.py
import sqlite3
import os

# Define o caminho completo para o banco de dados da API
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_DB_PATH = os.path.join(BASE_DIR, 'api_data.db')

def adicionar_coluna():
    """Conecta ao banco de dados e adiciona a coluna 'confronto_id' se ela não existir."""
    try:
        conn = sqlite3.connect(API_DB_PATH)
        cursor = conn.cursor()

        print("Verificando a tabela 'jogos'...")
        # Verifica se a coluna já existe
        cursor.execute("PRAGMA table_info(jogos)")
        colunas = [col[1] for col in cursor.fetchall()]

        if 'confronto_id' not in colunas:
            print("Adicionando a coluna 'confronto_id' à tabela 'jogos'...")
            # Adiciona a nova coluna, que pode ser nula para jogos de fase de grupo
            cursor.execute('ALTER TABLE jogos ADD COLUMN confronto_id INTEGER')
            conn.commit()
            print("Coluna 'confronto_id' adicionada com sucesso!")
        else:
            print("A coluna 'confronto_id' já existe.")

        conn.close()

    except sqlite3.Error as e:
        print(f"Ocorreu um erro no banco de dados: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == '__main__':
    adicionar_coluna()