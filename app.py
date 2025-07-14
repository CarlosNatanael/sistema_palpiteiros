from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from collections import defaultdict
from datetime import datetime
from functools import wraps
import requests
import sqlite3
import socket
import re

# --- Configurações de Administrador ---
app = Flask(__name__)
app.secret_key = 'ALJDHA76797#%*#JKOL'
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "pokemar16#" 

API_BASE_URL = "http://127.0.0.1:5001/api/v1"

TEMPORADA_ATUAL = "2ª Temporada" 

# --- Conexão com o Banco de Dados ---
def get_db():
    """Abre uma nova conexão com o banco de dados se não houver uma no contexto da requisição."""
    if 'db' not in g:
        g.db = sqlite3.connect('palpites.db', timeout=10)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Fecha a conexão com o banco de dados no final da requisição."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Cria/Verifica TODAS as tabelas no banco de dados local, incluindo as novas."""
    print("[LOG - app.py]: Verificando e inicializando TODAS as tabelas...")
    with get_db() as conn:
        # Tabela para armazenar resultados inseridos pelo Admin
        conn.execute('''
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY, placar_time1 INTEGER, placar_time2 INTEGER,
            status TEXT DEFAULT 'Pendente', time_que_avancou TEXT
        )''')
        # Tabela para a pontuação geral dos usuários
        conn.execute('''
        CREATE TABLE IF NOT EXISTS pontuacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE,
            pontos INTEGER DEFAULT 0, acertos INTEGER DEFAULT 0, erros INTEGER DEFAULT 0,
            pontos_bonus INTEGER DEFAULT 0
        )''')
        # Tabela para os palpites individuais dos usuários
        conn.execute('''
        CREATE TABLE IF NOT EXISTS palpites (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, rodada INTEGER, game_id INTEGER,
            time1 TEXT, time2 TEXT, gol_time1 INTEGER, gol_time2 INTEGER, resultado TEXT,
            status TEXT, quem_avanca TEXT
        )''')
        
        # CORREÇÃO APLICADA AQUI: Adicionada a coluna 'campeonato'
        conn.execute('''
        CREATE TABLE IF NOT EXISTS palpite_campeao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            campeonato TEXT NOT NULL,
            time_campeao TEXT,
            time_campeao_img TEXT,
            data_palpite TEXT
        )''')
        
        # Tabelas de Campeões
        conn.execute('''
        CREATE TABLE IF NOT EXISTS campeao_real (
            id INTEGER PRIMARY KEY AUTOINCREMENT, campeonato TEXT UNIQUE, 
            time_campeao TEXT, time_campeao_img TEXT, data_definicao TEXT
        )''')

        conn.execute('''
        CREATE TABLE IF NOT EXISTS campeao_palpiteiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temporada TEXT NOT NULL UNIQUE,
            competicao TEXT,
            nome TEXT NOT NULL, 
            pontos INTEGER, 
            acertos INTEGER,
            erros INTEGER, 
            data_definicao TEXT NOT NULL
        )''')

    print("[LOG - app.py]: Banco de dados de palpites pronto e atualizado.")

# --- Função Mágica: Busca dados da nossa API ---
def get_jogos_from_api(as_dict=True):
    """Busca os jogos da api.py. Retorna um dicionário por padrão para performance."""
    try:
        response = requests.get(f"{API_BASE_URL}/jogos")
        response.raise_for_status()
        jogos = response.json()
        if as_dict:
            return {jogo['id']: jogo for jogo in jogos}
        return jogos
    except requests.exceptions.RequestException:
        return {} if as_dict else []

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Filtro Jinja2 para formatar datas no template
@app.template_filter('format_date_br')
def format_date_br_filter(date_str):
    if not date_str: return ""
    try:
        return datetime.strptime(date_str.split(' ')[0], '%Y-%m-%d').strftime('%d/%m/%Y')
    except (ValueError, IndexError):
        return date_str
    
@app.template_filter('format_date')
def format_date_filter(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except:
        return date_str

@app.route('/')
def index():
    conn = get_db()
    jogos_api_map = get_jogos_from_api() # Retorna um dicionário {id: jogo}
    if not jogos_api_map:
        flash("Atenção: A API de jogos parece estar offline.", "warning")

    # Mescla resultados do banco local com os dados da API
    resultados_db = conn.execute("SELECT * FROM jogos").fetchall()
    for res in resultados_db:
        if res['id'] in jogos_api_map:
            jogos_api_map[res['id']].update(dict(res))

    # --- LÓGICA DE AGRUPAMENTO POR CAMPEONATO ---
    agora = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    jogos_futuros_por_campeonato = defaultdict(list)
    jogos_passados_por_campeonato = defaultdict(list)

    # Itera sobre todos os jogos e os agrupa
    for jogo in jogos_api_map.values():
        campeonato = jogo.get('campeonato', 'Sem Campeonato')
        if jogo.get('data_hora', 'Z') > agora:
            jogos_futuros_por_campeonato[campeonato].append(jogo)
        else:
            jogos_passados_por_campeonato[campeonato].append(jogo)
    # --- FIM DA LÓGICA DE AGRUPAMENTO ---
    
    pontuacao = conn.execute("SELECT nome, (pontos + pontos_bonus) as total_pontos, acertos, erros FROM pontuacao ORDER BY total_pontos DESC, acertos DESC").fetchall()
    
    # Passa os dicionários agrupados para o template
    return render_template('index.html', 
        pontuacao=pontuacao,
        jogos_futuros_por_campeonato=jogos_futuros_por_campeonato,
        jogos_passados_por_campeonato=jogos_passados_por_campeonato
    )

@app.route('/chaveamento')
def chaveamento():
    jogos_api = get_jogos_from_api(as_dict=False) # Pega como lista
    
    # Filtra apenas jogos de mata-mata direto da API
    jogos_mata_mata = [j for j in jogos_api if j.get('fase') == 'mata-mata']
    
    # Restante da lógica para montar o chaveamento
    oitavas = [j for j in jogos_mata_mata if j['rodada'] == 1] # Exemplo
    #... (sua lógica para quartas, semis, etc. continua aqui) ...

    return render_template('chaveamento.html', oitavas=oitavas, quartas=[], semis=[], final=[], campeao={'nome': 'A definir'})

@app.route('/palpites')
def exibir_palpites():
    conn = get_db()
    
    # 1. Obter todos os jogos da API e criar o 'jogos_map'
    jogos_api_map = get_jogos_from_api(as_dict=True) # as_dict=True é importante aqui
    if not jogos_api_map:
        flash("Atenção: Não foi possível carregar a lista de jogos. A API pode estar offline.", "warning")

    # 2. Obter as rodadas disponíveis a partir dos dados da API
    rodadas_existentes = sorted(list(set(j['rodada'] for j in jogos_api_map.values())))
    
    rodada_param = request.args.get('rodada', type=int)
    
    # Define a rodada a ser exibida (a mais recente com palpites, ou a primeira disponível)
    rodada_para_exibir = rodada_param
    if not rodada_para_exibir or rodada_para_exibir not in rodadas_existentes:
        rodada_recente_row = conn.execute("SELECT MAX(rodada) as max_rodada FROM palpites").fetchone()
        if rodada_recente_row and rodada_recente_row['max_rodada'] in rodadas_existentes:
            rodada_para_exibir = rodada_recente_row['max_rodada']
        else:
            rodada_para_exibir = rodadas_existentes[0] if rodadas_existentes else 1

    # 3. Buscar palpites do banco de dados local para a rodada selecionada
    palpites_db = conn.execute("SELECT * FROM palpites WHERE rodada = ? ORDER BY nome", (rodada_para_exibir,)).fetchall()

    # 4. Agrupar os palpites por jogador
    palpites_agrupados = defaultdict(list)
    for palpite in palpites_db:
        palpites_agrupados[palpite['nome']].append(dict(palpite))

    # Lógica de navegação entre rodadas
    idx_rodada = rodadas_existentes.index(rodada_para_exibir) if rodada_para_exibir in rodadas_existentes else -1
    tem_proxima = idx_rodada != -1 and idx_rodada < len(rodadas_existentes) - 1
    tem_anterior = idx_rodada > 0
    proxima_rodada = rodadas_existentes[idx_rodada + 1] if tem_proxima else None
    anterior_rodada = rodadas_existentes[idx_rodada - 1] if tem_anterior else None

    # 5. Passar TODOS os dados necessários para o template, incluindo o jogos_map
    return render_template(
        'palpites.html',
        palpites_agrupados=palpites_agrupados,
        jogos_map=jogos_api_map,  # <-- CORREÇÃO PRINCIPAL AQUI
        rodada_exibida_num=rodada_para_exibir,
        tem_proxima=tem_proxima,
        proxima_rodada=proxima_rodada,
        tem_anterior=tem_anterior,
        anterior_rodada=anterior_rodada
    )


def get_api_data(endpoint="jogos"):
    """Função auxiliar para fazer chamadas à API."""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao acessar API no endpoint '{endpoint}': {e}")
        return None

@app.route('/adicionar_palpites', methods=['GET', 'POST'])
def adicionar_palpites():
    conn = get_db()
    
    if request.method == 'POST':
        conn = get_db()
        nome = request.form.get('nome')
        rodada_selecionada = int(request.form.get('rodada_selecionada'))
        campeonato = request.form.get('campeonato_selecionado')

        # --- CORREÇÃO APLICADA AQUI ---
        # 1. Verifica se o palpiteiro já existe na tabela de pontuação
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM pontuacao WHERE nome = ?", (nome,))
        palpiteiro_existente = cursor.fetchone()

        # 2. Se não existir, insere o nome na tabela de pontuação para que ele apareça no ranking
        if not palpiteiro_existente:
            conn.execute("INSERT INTO pontuacao (nome) VALUES (?)", (nome,))
        # --- FIM DA CORREÇÃO ---

        jogos_api = get_api_data("jogos") or []
        agora_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        jogos_da_rodada_para_palpite = [
            j for j in jogos_api if 
            j['campeonato'] == campeonato and 
            j['rodada'] == rodada_selecionada and 
            j.get('data_hora', '') > agora_str
        ]

        for jogo in jogos_da_rodada_para_palpite:
            game_id = jogo['id']
            if f'gol_time1_{game_id}' in request.form:
                gol_time1 = int(request.form[f'gol_time1_{game_id}'])
                gol_time2 = int(request.form[f'gol_time2_{game_id}'])
                resultado_palpite = request.form[f'resultado_{game_id}']
                quem_avanca = request.form.get(f'quem_avanca_{game_id}')

                conn.execute("DELETE FROM palpites WHERE nome = ? AND game_id = ?", (nome, game_id))
                conn.execute(
                    "INSERT INTO palpites (nome, rodada, game_id, time1, time2, gol_time1, gol_time2, resultado, status, quem_avanca) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (nome, rodada_selecionada, game_id, jogo['time1_nome'], jogo['time2_nome'], gol_time1, gol_time2, resultado_palpite, 'Pendente', quem_avanca)
                )
        
        conn.commit()
        flash('Palpites registrados com sucesso!', 'success')
        return redirect(url_for('adicionar_palpites', campeonato_selecionado=campeonato, rodada_selecionada=rodada_selecionada))

    # --- LÓGICA DO GET ---
    campeonato_selecionado = request.args.get('campeonato_selecionado')
    rodada_selecionada = request.args.get('rodada_selecionada', type=int)

    campeonatos = get_api_data("campeonatos") or []
    
    rodadas_disponiveis = []
    jogos_filtrados = []
    
    if campeonato_selecionado:
        jogos_api = get_api_data() or []
        agora_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        jogos_do_campeonato = [
            j for j in jogos_api if 
            j['campeonato'] == campeonato_selecionado and 
            j.get('data_hora', '') > agora_str
        ]
        
        if jogos_do_campeonato:
            rodadas_disponiveis = sorted(list(set(j['rodada'] for j in jogos_do_campeonato)))

        if rodada_selecionada and rodada_selecionada in rodadas_disponiveis:
            jogos_filtrados = [j for j in jogos_do_campeonato if j['rodada'] == rodada_selecionada]

    palpiteiros = ["Ariel", "Arthur", "Carlos", "Celso", "Gabriel", "Lucas"]

    return render_template('adicionar_palpites.html',
        campeonatos=campeonatos,
        campeonato_selecionado=campeonato_selecionado,
        rodadas=rodadas_disponiveis,
        rodada_selecionada=rodada_selecionada,
        jogos=jogos_filtrados,
        palpiteiros=palpiteiros
    )

@app.route('/estatisticas')
def estatisticas():
    conn = get_db()

    # 1. Busca estatísticas e calcula o percentual (sem alterações aqui)
    estatisticas_completas = conn.execute('''
        SELECT nome, pontos, acertos, erros,
               CASE WHEN (acertos + erros) = 0 THEN 0.0 ELSE ROUND((acertos * 100.0 / (acertos + erros)), 1) END as percentual_acertos
        FROM pontuacao ORDER BY pontos DESC, acertos DESC
    ''').fetchall()

    maior_pontuador = estatisticas_completas[0] if estatisticas_completas else None
    quem_acertou_mais = sorted(estatisticas_completas, key=lambda x: x['acertos'], reverse=True)[0] if estatisticas_completas else None

    # --- LÓGICA ATUALIZADA PARA SEQUÊNCIA ATUAL NA RODADA ---
    
    # 2. Descobre a última rodada com palpites avaliados
    rodada_atual_row = conn.execute("SELECT MAX(rodada) as rodada FROM palpites WHERE status != 'Pendente'").fetchone()
    rodada_atual_bonus = rodada_atual_row['rodada'] if rodada_atual_row and rodada_atual_row['rodada'] else 0
    sequencias_info = defaultdict(int)
    
    if rodada_atual_bonus > 0:
        palpites_rodada_atual = conn.execute("""
            SELECT p.nome, p.status, j.data_hora FROM palpites p
            JOIN jogos j ON p.game_id = j.id
            WHERE p.status != 'Pendente' AND p.rodada = ?
            ORDER BY p.nome, j.data_hora
        """, (rodada_atual_bonus,)).fetchall()

        # 3. Calcula a SEQUÊNCIA ATUAL para cada jogador
        for jogador in estatisticas_completas:
            nome = jogador['nome']
            palpites_do_jogador_na_rodada = [p for p in palpites_rodada_atual if p['nome'] == nome]
            
            sequencia_atual = 0
            for palpite in palpites_do_jogador_na_rodada:
                if "Erro" not in palpite['status']:
                    sequencia_atual += 1
                else:
                    # Se errar, a sequência atual é zerada imediatamente.
                    sequencia_atual = 0
            
            # O valor final é a sequência atual, contada até o último jogo avaliado.
            sequencias_info[nome] = sequencia_atual

    # 4. Prepara os dados para o template (sem alterações aqui)
    sequencias_para_template = []
    for jogador in estatisticas_completas:
        nome = jogador['nome']
        max_streak = sequencias_info[nome]
        sequencias_para_template.append({
            'nome': nome,
            'sequencia': max_streak,
            'bonus': '🔥 Bônus Disponível!' if max_streak >= 3 else '--'
        })

    

    print(f"\n[LOG - estatisticas]: Rodada atual para cálculo de bônus: {rodada_atual_bonus}")
    print(f"[LOG - estatisticas]: Estatísticas carregadas para {len(estatisticas_completas)} jogadores.\n")

    return render_template('estatisticas.html',
                           maior_pontuador=maior_pontuador,
                           quem_acertou_mais=quem_acertou_mais,
                           estatisticas_completas=estatisticas_completas,
                           sequencias=sequencias_para_template,
                           rodada_atual_bonus=rodada_atual_bonus)

# --- ROTA COMPLETAMENTE NOVA PARA O ADMIN CONCEDER O BÔNUS ---
@app.route('/admin/award_bonus', methods=['POST'])
@login_required
def award_bonus():
    if request.form.get('password') != ADMIN_PASSWORD:
        print("\n[LOG] Tentativa de conceder bônus com senha incorreta")
        flash('Senha de administrador incorreta!', 'danger')
        return redirect(url_for('admin_dashboard'))

    nome_jogador = request.form.get('nome_jogador')
    pontos_bonus = 3

    if not nome_jogador:
        print("\n[LOG] Nenhum jogador selecionado para bônus")
        flash('Você precisa selecionar um jogador para conceder o bônus.', 'warning')
        return redirect(url_for('admin_dashboard'))

    conn = get_db()
    cursor = conn.cursor()
    
    print(f"\n[LOG] Tentando conceder bônus para {nome_jogador}")

    try:
        cursor.execute("UPDATE pontuacao SET pontos_bonus = pontos_bonus + ? WHERE nome = ?", (pontos_bonus, nome_jogador))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"\n[LOG] Bônus concedido com sucesso para {nome_jogador}")
            flash(f'Bônus de {pontos_bonus} pontos concedido para {nome_jogador} com sucesso!', 'success')
        else:
            print(f"\n[LOG] Jogador {nome_jogador} não encontrado")
            flash(f'Jogador {nome_jogador} não encontrado na tabela de pontuação.', 'danger')
    except Exception as e:
        print(f"\n[LOG] Erro ao conceder bônus: {str(e)}")
        conn.rollback()
        flash(f'Erro ao conceder bônus: {e}', 'danger')
        

    return redirect(url_for('admin_dashboard'))

@app.route('/regras')
def regra():
    print("\n[LOG] Acessando página de regras\n")
    return render_template('regras.html')

@app.route('/rodadas')
def exibir_rodadas():
     rodadas = [f"Rodada {i}" for i in sorted()]
     return render_template('rodadas.html', rodadas=rodadas)

@app.route('/rodada/<int:numero>')
def exibir_rodada(numero):
    conn = get_db()
    # A busca de palpites já pega a coluna 'quem_avanca', então está correta.
    palpites = conn.execute("SELECT * FROM palpites WHERE rodada = ?", (numero,)).fetchall()

    # CORREÇÃO: A busca de jogos agora inclui as colunas 'fase' e 'time_que_avancou'
    jogos_da_rodada = conn.execute(
        "SELECT * FROM jogos WHERE rodada = ? ORDER BY data_hora",
        (numero,)
    ).fetchall()
    

    palpites_agrupados = {}
    for palpite in palpites:
        nome = palpite['nome']
        if nome not in palpites_agrupados:
            palpites_agrupados[nome] = []
        # O palpite completo já é adicionado, o que é perfeito.
        palpites_agrupados[nome].append(palpite)

    return render_template('rodada.html', 
                           rodada=numero, 
                           palpites_agrupados=palpites_agrupados, 
                           jogos_da_rodada=jogos_da_rodada)

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        ip_cliente = request.remote_addr
        
        if username == ADMIN_USERNAME and request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            print(f"\n[LOG - login]: Login BEM-SUCEDIDO para '{username}' a partir do IP {ip_cliente}.\n")
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            print(f"\n[LOG - login]: Tentativa de login FALHOU para '{username}' a partir do IP {ip_cliente}.\n")
            flash('Nome de usuário ou senha incorretos.', 'danger')
    return render_template('login.html')

# Rota de Logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    print(f"\n[LOG] Logout realizado por {session.get('username', 'N/A')}\n")
    session.pop('logged_in', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    conn = get_db()
    # Estas consultas precisam que o DB já esteja criado com as tabelas certas.
    pontuacao_geral = conn.execute("SELECT nome FROM pontuacao ORDER BY nome").fetchall()
    campeao_atual = conn.execute("SELECT nome FROM campeao_palpiteiros WHERE id = 1").fetchone()
    return render_template('admin_dashboard.html', pontuacao_geral=pontuacao_geral, campeao_atual=campeao_atual)

@app.route('/admin/set_campeao_palpiteiro', methods=['POST'])
@login_required
def set_campeao_palpiteiro():
    conn = get_db()
    nome_campeao = request.form.get('campeao_nome')
    temporada = request.form.get('temporada')
    competicao = request.form.get('competicao')

    if not all([nome_campeao, temporada, competicao]):
        flash('Todos os campos (campeão, temporada e competição) são obrigatórios.', 'warning')
        return redirect(url_for('admin_dashboard'))

    jogador_stats = conn.execute(
        "SELECT nome, acertos, erros, (pontos + pontos_bonus) as total_pontos FROM pontuacao WHERE nome = ?", 
        (nome_campeao,)
    ).fetchone()
    
    if not jogador_stats:
        flash('Jogador não encontrado.', 'danger')
        return redirect(url_for('admin_dashboard'))
    conn.execute(
        """
        INSERT INTO campeao_palpiteiros (temporada, competicao, nome, pontos, acertos, erros, data_definicao) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(temporada) DO UPDATE SET
        competicao=excluded.competicao, nome=excluded.nome, pontos=excluded.pontos, acertos=excluded.acertos, erros=excluded.erros, data_definicao=excluded.data_definicao
        """,
        (temporada, competicao, jogador_stats['nome'], jogador_stats['total_pontos'], jogador_stats['acertos'], jogador_stats['erros'], datetime.now().strftime('%Y-%m-%d %H:%M'))
    )
    conn.commit()
    flash(f'{nome_campeao} foi coroado Campeão da {temporada} ({competicao})!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/historico')
def historico_campeoes():
    conn = get_db()
    campeoes_db = conn.execute("SELECT * FROM campeao_palpiteiros ORDER BY nome ASC, temporada ASC").fetchall()
    
    # Agrupa todas as informações da vitória por nome de jogador
    campeoes_agrupados = defaultdict(list)
    for campeao_data in campeoes_db:
        # Converte a linha do banco em um dicionário completo
        campeao_dict = dict(campeao_data)
        campeoes_agrupados[campeao_dict['nome']].append(campeao_dict)

    return render_template('historico.html', campeoes_agrupados=campeoes_agrupados)

@app.route('/admin/set_game_result', methods=['GET', 'POST'])
@login_required
def set_game_result():
    conn = get_db()
    if request.method == 'POST':
        # Lógica para salvar o resultado (permanece a mesma)
        game_id = int(request.form['game_id'])
        placar1 = int(request.form['placar_time1'])
        placar2 = int(request.form['placar_time2'])
        avancou = request.form.get('time_que_avancou')

        cursor = conn.cursor()
        cursor.execute("SELECT id FROM jogos WHERE id = ?", (game_id,))
        if cursor.fetchone():
            cursor.execute("UPDATE jogos SET placar_time1=?, placar_time2=?, status='Ao Vivo', time_que_avancou=? WHERE id=?", (placar1, placar2, avancou, game_id))
        else:
            cursor.execute("INSERT INTO jogos (id, placar_time1, placar_time2, status, time_que_avancou) VALUES (?, ?, ?, 'Ao Vivo', ?)", (game_id, placar1, placar2, avancou))
        
        conn.commit()
        flash(f'Resultado do jogo {game_id} salvo. Rode a atualização para calcular os pontos.', 'success')
        # Redireciona mantendo os filtros
        return redirect(url_for('set_game_result', 
                                campeonato_selecionado=request.form.get('campeonato_selecionado'), 
                                rodada_selecionada=request.form.get('rodada_selecionada')))

    # --- LÓGICA DO GET (para exibir a página) ---
    campeonato_selecionado = request.args.get('campeonato_selecionado')
    rodada_selecionada = request.args.get('rodada_selecionada', type=int)

    # 1. Busca todos os campeonatos
    campeonatos = get_api_data("campeonatos") or []
    
    rodadas_disponiveis = []
    jogos_filtrados = []
    
    if campeonato_selecionado:
        # 2. Se um campeonato foi escolhido, busca todos os jogos
        jogos_api = get_api_data("jogos") or []
        
        # Filtra jogos do campeonato selecionado
        jogos_do_campeonato = [j for j in jogos_api if j['campeonato'] == campeonato_selecionado]
        
        if jogos_do_campeonato:
            rodadas_disponiveis = sorted(list(set(j['rodada'] for j in jogos_do_campeonato)))

        # 3. Se uma rodada também foi escolhida, filtra os jogos para o formulário
        if rodada_selecionada and rodada_selecionada in rodadas_disponiveis:
            jogos_filtrados = [j for j in jogos_do_campeonato if j['rodada'] == rodada_selecionada]

    return render_template('set_game_result.html',
        campeonatos=campeonatos,
        campeonato_selecionado=campeonato_selecionado,
        rodadas=rodadas_disponiveis,
        rodada_selecionada=rodada_selecionada,
        jogos_disponiveis=jogos_filtrados
    )


@app.route('/atualizar_pontuacao_admin')
@login_required
def atualizar_pontuacao_admin():
    conn = get_db()
    # CORREÇÃO: Transforma a lista da API em um dicionário para performance
    jogos_api = get_jogos_from_api()
    jogos_api_map = {jogo['id']: jogo for jogo in jogos_api}

    resultados_db = conn.execute("SELECT * FROM jogos WHERE status != 'Pendente'").fetchall()
    palpites = conn.execute("SELECT * FROM palpites").fetchall()
    
    if not resultados_db:
        flash('Nenhum jogo com resultado definido para calcular a pontuação.', 'info')
        return redirect(url_for('admin_dashboard'))

    resultados_map = {r['id']: r for r in resultados_db}
    conn.execute("UPDATE pontuacao SET pontos = 0, acertos = 0, erros = 0")

    for palpite in palpites:
        game_id = palpite['game_id']
        if game_id in resultados_map and game_id in jogos_api_map:
            jogo_res = resultados_map[game_id]
            jogo_api = jogos_api_map[game_id]
            nome_palpiteiro = palpite['nome']
            pontos_ganhos = 0
            
            if jogo_res['placar_time1'] > jogo_res['placar_time2']: j_resultado = 'Vitória (Casa)'
            elif jogo_res['placar_time1'] < jogo_res['placar_time2']: j_resultado = 'Vitória (Fora)'
            else: j_resultado = 'Empate'

            acerto_placar = (palpite['gol_time1'] == jogo_res['placar_time1'] and palpite['gol_time2'] == jogo_res['placar_time2'])
            acerto_resultado = (palpite['resultado'] == j_resultado)
            acerto_avanco = (palpite['quem_avanca'] is not None and palpite['quem_avanca'] == jogo_res['time_que_avancou'])
            
            status_palpite = "Erro (0 pts)"

            if jogo_api['fase'] == 'mata-mata':
                if acerto_placar and acerto_resultado and acerto_avanco: pontos_ganhos, status_palpite = 5, "Acerto Total! (5 pts)"
                elif acerto_placar and acerto_resultado: pontos_ganhos, status_palpite = 4, "Acerto Placar + Resultado (4 pts)"
                elif acerto_placar and acerto_avanco: pontos_ganhos, status_palpite = 3, "Acerto Placar + Avanço (3 pts)"
                elif acerto_placar: pontos_ganhos, status_palpite = 2, "Acerto Placar (2 pts)"
                elif acerto_resultado and acerto_avanco: pontos_ganhos, status_palpite = 2, "Acerto Resultado + Avanço (2 pts)"
                elif acerto_resultado: pontos_ganhos, status_palpite = 1, "Acerto Resultado (1 pt)"
                elif acerto_avanco: pontos_ganhos, status_palpite = 1, "Acerto Avanço (1 pt)"
            else:
                if acerto_placar: pontos_ganhos, status_palpite = 4, "Acerto Total (4 pts)"
                elif acerto_resultado: pontos_ganhos, status_palpite = 1, "Acerto Resultado (1 pt)"

            if pontos_ganhos > 0:
                conn.execute("UPDATE pontuacao SET pontos = pontos + ?, acertos = acertos + 1 WHERE nome = ?", (pontos_ganhos, nome_palpiteiro))
            else:
                conn.execute("UPDATE pontuacao SET erros = erros + 1 WHERE nome = ?", (nome_palpiteiro,))
            
            conn.execute("UPDATE palpites SET status = ? WHERE id = ?", (status_palpite, palpite['id']))

    ids_processados = list(resultados_map.keys())
    if ids_processados:
        placeholders = ','.join('?' for _ in ids_processados)
        conn.execute(f"UPDATE jogos SET status = 'Finalizado' WHERE id IN ({placeholders})", ids_processados)
    
    conn.commit()
    flash('Pontuação atualizada com sucesso!', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/palpite_campeao', methods=['GET', 'POST'])
def palpite_campeao():
    conn = get_db()
    
    if request.method == 'POST':
        nome = request.form['nome']
        campeonato = request.form['campeonato_selecionado'] # Pega o campeonato do campo oculto
        time_campeao = request.form['time_campeao']

        # Busca a imagem do time na API
        jogos_api = get_api_data() or []
        time_campeao_img = None
        for jogo in jogos_api:
            if jogo['time1_nome'] == time_campeao:
                time_campeao_img = jogo['time1_img']
                break
            if jogo['time2_nome'] == time_campeao:
                time_campeao_img = jogo['time2_img']
                break
        
        existente = conn.execute('SELECT id FROM palpite_campeao WHERE nome = ? AND campeonato = ?', (nome, campeonato)).fetchone()
        
        if existente:
            conn.execute('UPDATE palpite_campeao SET time_campeao = ?, time_campeao_img = ?, data_palpite = ? WHERE id = ?', (time_campeao, time_campeao_img, datetime.now().strftime('%Y-%m-%d %H:%M'), existente['id']))
        else:
            conn.execute('INSERT INTO palpite_campeao (nome, campeonato, time_campeao, time_campeao_img, data_palpite) VALUES (?, ?, ?, ?, ?)', (nome, campeonato, time_campeao, time_campeao_img, datetime.now().strftime('%Y-%m-%d %H:%M')))
        
        conn.commit()
        flash('Seu palpite para campeão foi registrado!', 'success')
        return redirect(url_for('ver_palpites_campeao'))

    # --- LÓGICA DO GET ---
    campeonato_selecionado = request.args.get('campeonato_selecionado')
    
    # 1. Busca a lista de campeonatos disponíveis
    campeonatos = get_api_data("campeonatos") or []
    
    times_filtrados = []
    if campeonato_selecionado:
        # 2. Se um campeonato foi escolhido, busca todos os jogos
        jogos_api = get_api_data() or []
        
        # 3. Filtra os times APENAS do campeonato selecionado
        times_do_campeonato = {}
        for jogo in jogos_api:
            if jogo['campeonato'] == campeonato_selecionado:
                times_do_campeonato[jogo['time1_nome']] = jogo['time1_img']
                times_do_campeonato[jogo['time2_nome']] = jogo['time2_img']
        
        times_filtrados = [{'name': nome, 'img_src': img} for nome, img in sorted(times_do_campeonato.items())]

    palpiteiros = ["Ariel", "Arthur", "Carlos", "Celso", "Gabriel", "Lucas"]
    
    return render_template('palpite_campeao.html', 
        palpiteiros=palpiteiros, 
        campeonatos=campeonatos,
        campeonato_selecionado=campeonato_selecionado,
        times=times_filtrados)

@app.route('/ver_palpites_campeao')
def ver_palpites_campeao():
    conn = get_db()
    palpites = conn.execute('''
        SELECT p.nome, p.campeonato, p.time_campeao, p.data_palpite, p.time_campeao_img
        FROM palpite_campeao p
        ORDER BY p.campeonato ASC, p.nome ASC
    ''').fetchall()
    
    campeoes_reais = conn.execute('SELECT * FROM campeao_real').fetchall()
    campeoes_map = {c['campeonato']: dict(c) for c in campeoes_reais}

    return render_template('ver_palpites_campeao.html', palpites=palpites, campeoes_reais=campeoes_map)

@app.route('/admin/set_champion', methods=['GET', 'POST'])
@login_required
def set_champion():
    conn = get_db()
    cursor = conn.cursor()

    all_teams_db = conn.execute('''
        SELECT DISTINCT time1_nome as name, time1_img as img_src FROM jogos
        UNION
        SELECT DISTINCT time2_nome as name, time2_img as img_src FROM jogos
        ORDER BY name
    ''').fetchall()

    if request.method == 'POST':
        campeao_nome = request.form['campeao_nome']
        
        campeao_info = next((team for team in all_teams_db if team['name'] == campeao_nome), None)
        campeao_img = campeao_info['img_src'] if campeao_info else None

        # Limpa o campeão anterior e insere o novo (assumindo apenas 1 campeão mundial)
        try:
            cursor.execute('DELETE FROM campeao_mundial')
            cursor.execute(
                'INSERT INTO campeao_mundial (time_campeao, time_campeao_img, data_definicao) VALUES (?, ?, ?)',
                (campeao_nome, campeao_img, datetime.now().strftime('%Y-%m-%d %H:%M'))
            )
            conn.commit()
            print(f"\n[LOG] Campeão definido: {campeao_nome}\n")
            flash(f'Campeão mundial definido como {campeao_nome}!', 'success')
        except Exception as e:
            conn.rollback()
            print(f"\n[LOG] Erro ao definir campeão: {str(e)}\n")
            flash(f'Erro ao definir campeão: {e}', 'danger')
            
        return redirect(url_for('set_champion'))

    campeao_atual = conn.execute('SELECT time_campeao, time_campeao_img FROM campeao_mundial LIMIT 1').fetchone()
    

    print("\n[LOG] Acessando página de definição de campeão\n")
    return render_template('set_champion.html', teams=all_teams_db, campeao_atual=campeao_atual)

@app.route('/campeao_geral')
def campeao_geral():
    conn = get_db()
    # A consulta agora busca especificamente o campeão da TEMPORADA_ATUAL
    campeao_data = conn.execute(
        "SELECT * FROM campeao_palpiteiros WHERE temporada = ?", 
        (TEMPORADA_ATUAL,)
    ).fetchone()
    
    campeao = None
    if campeao_data:
        campeao = dict(campeao_data)
        total_jogos = campeao['acertos'] + campeao['erros']
        if total_jogos > 0:
            percentual = (campeao['acertos'] / total_jogos) * 100
            campeao['percentual_acertos'] = round(percentual, 1)
        else:
            campeao['percentual_acertos'] = 0
    
    # Adicionamos a temporada atual ao template para poder exibi-la
    return render_template('campeao_geral.html', campeao=campeao, temporada_atual=TEMPORADA_ATUAL)

@app.route('/admin/manage_games', methods=['GET', 'POST'])
@login_required
def manage_games():
    # Esta rota, criada anteriormente, é agora a principal forma de gerenciar fases
    conn = get_db()
    if request.method == 'POST':
        game_id = request.form.get('game_id')
        nova_fase = request.form.get('fase')
        conn.execute("UPDATE jogos SET fase = ? WHERE id = ?", (nova_fase, game_id))
        conn.commit()
        flash(f'Fase do jogo ID {game_id} atualizada!', 'success')
        return redirect(url_for('manage_games'))

    jogos = conn.execute("SELECT * FROM jogos ORDER BY rodada, data_hora").fetchall()
    return render_template('manage_games.html', jogos=jogos)

if __name__ == '__main__':
    with app.app_context():
        init_db()  # Apenas garante que as tabelas locais existem

    print("\n" + "="*50)
    print("      INICIANDO APLICAÇÃO PRINCIPAL (APP.PY)")
    print("      Certifique-se que a API (api.py) está rodando.")
    print("="*50)
    
    app.run(host="0.0.0.0", port=3000, debug=True)