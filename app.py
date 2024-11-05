from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_sessao'

def get_db_connection():
    conn = sqlite3.connect('palpites.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()  
    conn.execute('''
    CREATE TABLE IF NOT EXISTS pontuacao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        posicao INTEGER,
        nome TEXT UNIQUE,
        pontos INTEGER DEFAULT 0,
        acertos INTEGER DEFAULT 0,
        erros INTEGER DEFAULT 0
    )''')
    
    conn.execute('''
    CREATE TABLE IF NOT EXISTS palpites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        time1 TEXT,
        time2 TEXT,
        gol_time1 INTEGER,
        gol_time2 INTEGER,
        resultado TEXT
    )''')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/pontuacao')
def exibir_pontuacao():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pontuacao ORDER BY posicao ASC")
    pontuacao = cursor.fetchall()
    conn.close()
    return render_template('pontuacao.html', pontuacao=pontuacao)

@app.route('/palpites')
def exibir_palpites():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM palpites")
    palpites = cursor.fetchall()
    conn.close()
    return render_template('palpites.html', palpites=palpites)

@app.route('/palpites', methods=['GET', 'POST'])
def adicionar_palpites():
    if request.method == 'POST':
        nome = request.form['nome']
        time1 = request.form['time1']
        time2 = request.form['time2']
        gol_time1 = int(request.form['gol_time1'])
        gol_time2 = int(request.form['gol_time2'])
        resultado = request.form['resultado']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO palpites (nome, time1, time2, gol_time1, gol_time2, resultado) VALUES (?, ?, ?, ?, ?, ?)",
            (nome, time1, time2, gol_time1, gol_time2, resultado)
        )
        conn.commit()
        conn.close()
        return redirect('/palpites')
    return render_template('adicionar_palpites.html')

@app.route('/atualizar_pontuacao')
def atualizar_pontuacao():
    conn = get_db_connection()
    cursor = conn.cursor()
    resultados_reais = {
        ('COR', 'PAL'): (2, 1),
    }

    cursor.execute("UPDATE pontuacao SET acertos = 0, erros = 0")

    cursor.execute("SELECT * FROM palpites")
    palpites = cursor.fetchall()

    for palpite in palpites:
        nome = palpite['nome']
        time1 = palpite['time1']
        time2 = palpite['time2']
        gol_time1 = palpite['gol_time1']
        gol_time2 = palpite['gol_time2']


        resultado_real = resultados_reais.get((time1, time2))
        if resultado_real:
            gol_real_time1, gol_real_time2 = resultado_real


            if gol_time1 == gol_real_time1 and gol_time2 == gol_real_time2:
                cursor.execute("UPDATE pontuacao SET pontos = pontos + 3, acertos = acertos + 1 WHERE nome = ?", (nome,))
            else:
                cursor.execute("UPDATE pontuacao SET erros = erros + 1 WHERE nome = ?", (nome,))

    conn.commit()
    conn.close()
    return redirect('/pontuacao')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)