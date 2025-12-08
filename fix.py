import sqlite3
import os

# Pega o caminho exato onde este arquivo está, para achar o banco na mesma pasta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'palpites.db')

print(f"Conectando ao banco em: {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Lista dos seus palpiteiros
    palpiteiros = ["Ariel", "Arthur", "Carlos", "Celso", "Gabriel", "Lucas"]

    print("--- Verificando Jogadores ---")
    for nome in palpiteiros:
        # Verifica se o jogador já existe
        cursor.execute("SELECT nome FROM pontuacao WHERE nome = ?", (nome,))
        if not cursor.fetchone():
            print(f"[+] Criando jogador: {nome}")
            # Insere o jogador com tudo zerado
            cursor.execute("""
                INSERT INTO pontuacao (nome, pontos, acertos, erros, pontos_bonus) 
                VALUES (?, 0, 0, 0, 0)
            """, (nome,))
        else:
            print(f"[v] Jogador já existe: {nome}")

    conn.commit()
    print("\nSUCESSO! Todos os jogadores foram verificados.")
    print("Pode voltar no Painel Admin que a lista estará cheia.")

except Exception as e:
    print(f"\nERRO: {e}")
    # Se der erro de "no such table", avisa que a tabela não existe
    if "no such table" in str(e):
        print("A tabela 'pontuacao' não foi encontrada! O banco pode estar vazio ou corrompido.")

finally:
    if 'conn' in locals():
        conn.close()