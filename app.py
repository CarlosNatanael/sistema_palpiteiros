# sistema_palpiteiros/app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

API_BASE_URL = "http://apifutebol.footstats.com.br/3.1"
API_TOKEN = "Bearer_client_token"

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
        resultado TEXT,
        status TEXT
    )''')

    conn.commit()
    conn.close()

init_db()


# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/nIdbR6qIUDyZUBO9vojSPw_48x48.png" alt="Bahia">
# Bahia >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/tCMSqgXVHROpdCpQhzTo1g_48x48.png" alt="Corinthians">
# Corinthians >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/u_L7Mkp33uNmFTv3uUlXeQ_48x48.png" alt="Criciúma">
# Criciúma >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/hHwT8LwRmYCAGxQ-STLxYA_48x48.png" alt="Vasco">
# Vasco >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/9mqMGndwoR9og_Z0uEl2kw_48x48.png" alt="Atlético-GO">
# Atlético-GO >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/Ku-73v_TW9kpex-IEGb0ZA_48x48.png" alt="Grêmio">
# Grêmio >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/4w2Z97Hf9CSOqICK3a8AxQ_48x48.png" alt="São Paulo">
# São Paulo >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png" alt="Flamengo">
# Flamengo >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/OWVFKuHrQuf4q2Wk0hEmSA_48x48.png" alt="Internacional">
# Internacional >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/9LkdBR4L5plovKM8eIy7nQ_48x48.png" alt="Atlético-PR">
# Atlético-PR >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/fCMxMMDF2AZPU7LzYKSlig_48x48.png" alt="Fluminense">
# Fluminense >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/LHSM6VchpkI4NIptoSTHOg_48x48.png" alt="Vitória">
# Vitória >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/me10ephzRxdj45zVq1Risg_48x48.png" alt="Fortaleza">
# Fortaleza >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/q9fhEsgpuyRq58OgmSndcQ_48x48.png" alt="Atlético-MG">
# Atlético-MG >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png" alt="Botafogo">
# Botafogo >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/JrXw-m4Dov0gE2Sh6XJQMQ_48x48.png" alt="Juventude">
# Juventude >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png" alt="Palmeiras">
# Palmeiras >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/Tcv9X__nIh-6wFNJPMwIXQ_48x48.png" alt="Cruzeiro">
# Cruzeiro >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/j6U8Rgt_6yyf0Egs9nREXw_48x48.png" alt="Cuiabá">
# Cuiabá >

# <img src="https://ssl.gstatic.com/onebox/media/sports/logos/lMyw2zn1Z4cdkaxKJWnsQw_48x48.png" alt="Bragantino">
# Bragantino >

# Função auxiliar para extrair nomes e URLs de imagens dos times
def get_teams_from_file():
    teams = []
    # Usaremos uma abordagem para ler o arquivo diretamente aqui,
    # ou você pode pré-processar e armazenar isso em um lugar mais acessível.
    # Por simplicidade, vou simular a leitura do arquivo 'Imagems times.txt'
    # com os dados que você já me forneceu.
    team_data = """
=================== Mundial ======================================
<img src="https://ssl.gstatic.com/onebox/media/sports/logos/7spurne-xDt2p6C0imYYNA_48x48.png" alt="Palmeiras">
Palmeiras >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/orE554NToSkH6nuwofe7Yg_48x48.png" alt="Flamengo">
Flamengo >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/fCMxMMDF2AZPU7LzYKSlig_48x48.png" alt="Fluminense">
Fluminense >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/KLDWYp-H8CAOT9H_JgizRg_48x48.png" alt="Botafogo">
Botafogo >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/-_cmntP5q_pHL7g5LfkRiw_96x96.png" alt="Bayern">
Bayern >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/ydlyVc6hUPBXoaT3wR_lFg_96x96.png" alt="Auckland City">
Auckland City >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/JdNbaaw7JlDHvPHZaX2V2A_48x48.png" alt="Al Ahly">
Al Ahly >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/dn0bMtTbbpx7v3Ieq6TZtQ_48x48.png" alt="Inter Miami">
Inter Miami >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/QkkllEKwkj60jEVtOEZWAg_48x48.png" alt="Porto">
Porto >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/pEqmA7CL-VRo4Llq3rwIPA_48x48.png" alt="Atlético Madrid">
Atlético Madrid >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/mcpMspef1hwHwi9qrfp4YQ_48x48.png" alt="PSG">
PSG >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/k6m3hoy4Rn3KRrMYSYDjog_48x48.png" alt="Seattle Sounders">
Seattle Sounders >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/nFwABZ-4n_A3BGXT9A7Adg_48x48.png" alt="Benfica">
Benfica >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/YO1impuFJT2hex6wvCd9Pw_48x48.png" alt="Boca Juniors">
Boca Juniors >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/fhBITrIlbQxhVB6IjxUO6Q_48x48.png" alt="Chelsea">
Chelsea >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/Kf32x8gh5SCMEqvKjVGLfg_48x48.png" alt="Espérance">
Espérance >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/waD0z1CWx6_r4UT_hgb7nA_96x96.png" alt="LAFC">
LAFC >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/l2-icwsMhIvsbRw8AwC1yg_48x48.png" alt="Inter">
Inter >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/LXZ8fEgzf0_FwSyq15buPw_48x48.png" alt="Monterrey">
Monterrey >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/700Mj6lUNkbBdvOVEbjC3g_48x48.png" alt="River Plate">
River Plate >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/F-09rxdgECid61-Rj8Uxrw_48x48.png" alt="Urawa Reds">
Urawa Reds >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/FZnTSH2rbHFos4BnlWAItw_48x48.png" alt="Borussia">
Borussia >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/Lmp8fUABWWKRwNrHf71m5w_48x48.png" alt="Sundowns">
Sundowns >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/-K1h8OOTItUmjKqR2g5Nnw_48x48.png" alt="Ulsan Hyundai">
Ulsan Hyundai >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/vA9sLyDeHX3q7pn8QTmoeQ_48x48.png" alt="Al Ain">
Al Ain >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/6lal-0xwWtos5HI99HRvuQ_48x48.png" alt="Juventus">
Juventus >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/z44l-a0W1v5FmgPnemV6Xw_48x48.png" alt="City">
City >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/JxwBeJ9HrjZX_vRqTPwY6A_48x48.png" alt="Wydad AC">
Wydad AC >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/HGVsnyWvMiGVotxhgicdSQ_48x48.png" alt="Al-Hilal">
Al-Hilal >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/9dscoX8iYhzbjSNxXVp2gQ_48x48.png" alt="Pachuca">
Pachuca >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/Th4fAVAZeCJWRcKoLW7koA_48x48.png" alt="Real Madrid">
Real Madrid >

<img src="https://ssl.gstatic.com/onebox/media/sports/logos/vQhr4NoE_4Yg1IhUZvbRNw_48x48.png" alt="RB Salzburg">
RB Salzburg >
    """
    import re
    # Expressão regular para encontrar a URL da imagem e o nome do time
    pattern = r'<img src="(.*?)" alt="(.*?)">\s*(.*?)\s*>'
    matches = re.findall(pattern, team_data)

    for match in matches:
        img_src = match[0]
        alt_text = match[1]
        team_name = match[2].strip() # O nome do time está no terceiro grupo de captura

        # Alguns nomes podem ter > no final, vamos remover
        if team_name.endswith('>'):
            team_name = team_name[:-1].strip()

        teams.append({'name': team_name, 'img_src': img_src})
    return teams


@app.route('/')
def index():
    conn = get_db_connection()
    pontuacao = conn.execute("SELECT * FROM pontuacao ORDER BY pontos DESC, acertos DESC, erros ASC").fetchall() # Ordenar por pontos, acertos e erros
    conn.close()
    return render_template('index.html', pontuacao=pontuacao)

@app.route('/palpites')
def exibir_palpites():
    conn = get_db_connection()
    palpites = conn.execute("SELECT * FROM palpites").fetchall()
    conn.close()

    palpites_agrupados = {}
    for palpite in palpites:
        nome = palpite['nome']
        if nome not in palpites_agrupados:
            palpites_agrupados[nome] = []
        palpites_agrupados[nome].append(palpite)

    return render_template('palpites.html', palpites_agrupados=palpites_agrupados)

@app.route('/adicionar_palpites', methods=['GET', 'POST'])
def adicionar_palpites():
    teams = get_teams_from_file() # Obter a lista de times
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
            "INSERT INTO palpites (nome, time1, time2, gol_time1, gol_time2, resultado, status) VALUES (?, ?, ?, ?, ?, ?, ?)", # Adicionado 'status'
            (nome, time1, time2, gol_time1, gol_time2, resultado, 'Pendente') # Status inicial
        )
        conn.commit()
        # Inserir o nome do palpiteiro na tabela de pontuação se ele não existir
        try:
            cursor.execute("INSERT INTO pontuacao (nome, pontos, acertos, erros, posicao) VALUES (?, ?, ?, ?, ?)", (nome, 0, 0, 0, 99)) # Posição temporária
            conn.commit()
        except sqlite3.IntegrityError:
            # Se o nome já existe, não faz nada (já está na tabela pontuacao)
            pass
        conn.close()
        return redirect('/palpites')
    return render_template('adicionar_palpites.html', teams=teams) # Passar a lista de times para o template

@app.route('/estatisticas')
def estatisticas():
    conn = get_db_connection()
    # Lógica para obter o maior pontuador e quem acertou mais
    maior_pontuador = conn.execute("SELECT nome, pontos FROM pontuacao ORDER BY pontos DESC LIMIT 1").fetchone()
    quem_acertou_mais = conn.execute("SELECT nome, acertos FROM pontuacao ORDER BY acertos DESC LIMIT 1").fetchone()
    conn.close()
    return render_template('estatisticas.html', maior_pontuador=maior_pontuador, quem_acertou_mais=quem_acertou_mais)

@app.route('/regras')
def regra():
    return render_template('regras.html')

@app.route('/rodadas')
def exibir_rodadas():
     # Para o Mundial, talvez tenhamos um número fixo de rodadas ou uma lógica diferente.
     # Por enquanto, vou manter o que você tinha e ajustar se necessário.
     rodadas = [f"Rodada {i}" for i in range(1, 2)] # Exemplo: 3 rodadas para o Mundial
     return render_template('rodadas.html', rodadas=rodadas)

@app.route('/rodada/<int:numero>')
def exibir_rodada(numero):
    nome_banco = f"rodada_{numero}.db"

    import os
    if not os.path.exists(nome_banco):
        # Se o banco da rodada não existir, podemos exibir palpites da rodada principal
        # ou uma mensagem de erro mais amigável.
        # Por agora, vamos retornar uma mensagem.
        return f"Banco de dados para a rodada {numero} não encontrado.", 404

    conn = sqlite3.connect(nome_banco)
    conn.row_factory = sqlite3.Row
    palpites = conn.execute("SELECT * FROM palpites").fetchall()
    conn.close()

    palpites_agrupados = {}
    for palpite in palpites:
        nome = palpite['nome']
        if nome not in palpites_agrupados:
            palpites_agrupados[nome] = []
        palpites_agrupados[nome].append({
            'time1': palpite['time1'],
            'gol_time1': palpite['gol_time1'],
            'time2': palpite['time2'],
            'gol_time2': palpite['gol_time2'],
            'resultado': palpite['resultado'],
            'status': palpite['status']
        })

    return render_template('rodada.html', rodada=numero, palpites_agrupados=palpites_agrupados)



@app.route('/atualizar_pontuacao')
def atualizar_pontuacao():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Resultados jogos
    # resultados_reais = {
    #     ('Al Ahly', 'Inter Miami'): (1, 2),
    #     ('Bayern', 'Auckland City'): (3, 0),
    #     ('PSG', 'Atlético Madrid'): (1, 1),
    #     ('Palmeiras', 'Porto'): (0, 1),
    #     ('Botafogo', 'Seattle Sounders'): (2, 0),
    #     ('Chelsea', 'LAFC'): (2, 2),
    #     ('Boca Juniors', 'Benfica'): (1, 0),
    #     ('Flamengo', 'Espérance'): (4, 1),
    #     ('Fluminense', 'Borussia'): (0, 2),
    #     ('River Plate', 'Urawa Reds'): (3, 1),
    #     ('Ulsan Hyundai', 'Sundowns'): (1, 1),
    #     ('Monterrey', 'Inter'): (0, 1),
    #     ('City', 'Wydad AC'): (3, 0),
    #     ('Real Madrid', 'Al-Hilal'): (2, 0),
    #     ('Pachuca', 'RB Salzburg'): (1, 0),
    #     ('Al Ain', 'Juventus'): (0, 3)
    # }
    # Você precisará atualizar isso manualmente ou integrar uma API
    resultados_reais = {
        ('Al Ahly', 'Inter Miami'): (1, 2)
    }

    # Zera a pontuação e acertos/erros para recalcular
    cursor.execute("UPDATE pontuacao SET pontos = 0, acertos = 0, erros = 0")

    cursor.execute("SELECT * FROM palpites")
    palpites = cursor.fetchall()

    for palpite in palpites:
        nome = palpite['nome']
        time1 = palpite['time1']
        time2 = palpite['time2']
        gol_time1 = palpite['gol_time1']
        gol_time2 = palpite['gol_time2']
        palpite_id = palpite['id'] # Para atualizar o status do palpite

        resultado_real = resultados_reais.get((time1, time2))
        if resultado_real:
            gol_real_time1, gol_real_time2 = resultado_real

            pontos_ganhos = 0
            status_palpite = "Erro" # Status padrão

            # Lógica de pontuação detalhada (ajustada conforme suas regras)
            # Regras de Pontuação:
            # Acerto do Placar + Resultado com Especificação = 4 pts
            # Acerto do Placar + Resultado geral = 3 pts
            # Acerto do Placar = 2 pts
            # Resultado com Especificação = 2 pts
            # Resultado geral = 1 pts

            # 1. Acerto do Placar Completo
            if gol_time1 == gol_real_time1 and gol_time2 == gol_real_time2:
                # Acertou o placar exato
                if (gol_real_time1 > gol_real_time2 and palpite['resultado'] == 'Vitória (Casa)') or \
                   (gol_real_time1 < gol_real_time2 and palpite['resultado'] == 'Vitória (Fora)') or \
                   (gol_real_time1 == gol_real_time2 and palpite['resultado'] == 'Empate'):
                    pontos_ganhos = 4 # Acerto do Placar + Resultado com Especificação
                    status_palpite = "Acerto Total (4 pts)"
                else:
                    pontos_ganhos = 3 # Acerto do Placar + Resultado geral
                    status_palpite = "Acerto Placar (3 pts)"
                cursor.execute("UPDATE pontuacao SET acertos = acertos + 1 WHERE nome = ?", (nome,))
            else:
                # Verifica o resultado (vitória/empate/derrota)
                palpite_vitoria_casa = gol_time1 > gol_time2
                palpite_vitoria_fora = gol_time1 < gol_time2
                palpite_empate = gol_time1 == gol_time2

                real_vitoria_casa = gol_real_time1 > gol_real_time2
                real_vitoria_fora = gol_real_time1 < gol_real_time2
                real_empate = gol_real_time1 == gol_real_time2

                if (palpite_vitoria_casa and real_vitoria_casa) or \
                   (palpite_vitoria_fora and real_vitoria_fora) or \
                   (palpite_empate and real_empate):

                    # Acertou o resultado geral
                    if (real_vitoria_casa and palpite['resultado'] == 'Vitória (Casa)') or \
                       (real_vitoria_fora and palpite['resultado'] == 'Vitória (Fora)') or \
                       (real_empate and palpite['resultado'] == 'Empate'):
                        pontos_ganhos = 2 # Resultado com Especificação
                        status_palpite = "Acerto Resultado Específico (2 pts)"
                    else:
                        pontos_ganhos = 1 # Resultado geral
                        status_palpite = "Acerto Resultado Geral (1 pt)"
                    cursor.execute("UPDATE pontuacao SET acertos = acertos + 1 WHERE nome = ?", (nome,))
                else:
                    cursor.execute("UPDATE pontuacao SET erros = erros + 1 WHERE nome = ?", (nome,))
                    status_palpite = "Erro (0 pts)"

            cursor.execute("UPDATE pontuacao SET pontos = pontos + ? WHERE nome = ?", (pontos_ganhos, nome))
            cursor.execute("UPDATE palpites SET status = ? WHERE id = ?", (status_palpite, palpite_id))

        else:
            # Se não houver resultado real, o palpite pode permanecer como 'Pendente' ou 'Não Jogado'
            # cursor.execute("UPDATE palpites SET status = ? WHERE id = ?", ('Não Jogado', palpite_id))
            pass # Manter como pendente se não há resultado real


    # Atualizar posições baseado na nova pontuação
    pontuacao_atualizada = conn.execute("SELECT nome, pontos FROM pontuacao ORDER BY pontos DESC, acertos DESC, erros ASC").fetchall()
    for i, jogador in enumerate(pontuacao_atualizada):
        cursor.execute("UPDATE pontuacao SET posicao = ? WHERE nome = ?", (i + 1, jogador['nome']))


    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)