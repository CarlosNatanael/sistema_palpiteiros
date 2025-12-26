from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from collections import defaultdict
from datetime import datetime
from functools import wraps
from config import API_BASE_URL
import requests
import sqlite3
import pytz
import os

# --- Adicione esta linha perto do topo ---
# Define o caminho completo para o diretório do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'palpites.db')

# --- Configurações de Administrador ---
app = Flask(__name__)
app.secret_key = 'ALJDHA76797#%*#JKOL'
MODERADORES = {
    "admin" : "pokemar16",
    "gabriel" : "25dez01"
}
TEMPORADA_ATUAL = "3ª Temporada" 

# ==== TESTE LOCAL =======
# API_BASE_URL = "http://127.0.0.1:5001/api/v1"

# --- Conexão com o Banco de Dados ---
def get_db():
    if 'db' not in g:
        # Use a variável DB_PATH com o caminho completo
        g.db = sqlite3.connect(DB_PATH, timeout=10)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

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
    anuncios = conn.execute("SELECT * FROM anuncios ORDER BY data_criacao DESC LIMIT 3").fetchall()
    jogos_api_map = get_jogos_from_api()
    if not jogos_api_map:
        flash("Atenção: A API de jogos parece estar offline.", "warning")

    todas_rodadas = sorted(list(set(j['rodada'] for j in jogos_api_map.values())))
    rodada_ativa_str = request.args.get('rodada')
    try:
        rodada_ativa = int(rodada_ativa_str) if rodada_ativa_str else todas_rodadas[-1]
    except (ValueError, IndexError):
        rodada_ativa = todas_rodadas[0] if todas_rodadas else 1

    if rodada_ativa not in todas_rodadas and todas_rodadas:
        rodada_ativa = todas_rodadas[-1]

    idx_rodada_ativa = todas_rodadas.index(rodada_ativa) if rodada_ativa in todas_rodadas else -1
    tem_anterior = idx_rodada_ativa > 0
    anterior_rodada = todas_rodadas[idx_rodada_ativa - 1] if tem_anterior else None
    tem_proxima = idx_rodada_ativa != -1 and idx_rodada_ativa < len(todas_rodadas) - 1
    proxima_rodada = todas_rodadas[idx_rodada_ativa + 1] if tem_proxima else None

    resultados_db = conn.execute("SELECT * FROM jogos").fetchall()
    resultados_map = {res['id']: dict(res) for res in resultados_db}

    fuso_horario_brasil = pytz.timezone('America/Sao_Paulo')
    agora_brasil = datetime.now(fuso_horario_brasil)
    agora_str = agora_brasil.strftime('%Y-%m-%d %H:%M')

    jogos_futuros_por_campeonato = defaultdict(list)
    jogos_passados_por_campeonato = defaultdict(list)

    for jogo_id, jogo_base in jogos_api_map.items():
        if jogo_base.get('rodada') == rodada_ativa:
            jogo = jogo_base.copy()
            if jogo_id in resultados_map:
                jogo.update(resultados_map[jogo_id])

            campeonato = jogo.get('campeonato', 'Sem Campeonato')
            if jogo.get('data_hora', 'Z') > agora_str:
                jogos_futuros_por_campeonato[campeonato].append(jogo)
            else:
                jogos_passados_por_campeonato[campeonato].append(jogo)

    pontuacao = conn.execute("SELECT nome, (pontos + pontos_bonus) as total_pontos, acertos, erros FROM pontuacao ORDER BY total_pontos DESC, acertos DESC").fetchall()

    return render_template('index.html', 
        pontuacao=pontuacao,
        jogos_futuros_por_campeonato=jogos_futuros_por_campeonato,
        jogos_passados_por_campeonato=jogos_passados_por_campeonato,
        rodada_ativa=rodada_ativa,
        tem_anterior=tem_anterior,
        anterior_rodada=anterior_rodada,
        tem_proxima=tem_proxima,
        proxima_rodada=proxima_rodada,
        anuncios=anuncios
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
        nome = request.form.get('nome')
        rodada_selecionada = int(request.form.get('rodada_selecionada'))
        campeonato = request.form.get('campeonato_selecionado')

        if not nome:
            flash('Você precisa selecionar o seu nome para salvar os palpites.', 'warning')
            return redirect(url_for('adicionar_palpites', campeonato_selecionado=campeonato, rodada_selecionada=rodada_selecionada))

        cursor = conn.cursor()
        cursor.execute("SELECT id FROM pontuacao WHERE nome = ?", (nome,))
        if not cursor.fetchone():
            conn.execute("INSERT INTO pontuacao (nome) VALUES (?)", (nome,))

        jogos_api = get_api_data("jogos") or []
        
        fuso_horario_brasil = pytz.timezone('America/Sao_Paulo')
        agora_brasil = datetime.now(fuso_horario_brasil)
        agora_str = agora_brasil.strftime('%Y-%m-%d %H:%M')

        jogos_da_rodada_para_palpite = [
            j for j in jogos_api if 
            j['campeonato'] == campeonato and 
            j['rodada'] == rodada_selecionada and 
            j.get('data_hora', '') > agora_str
        ]
        
        palpites_feitos = 0
        for jogo in jogos_da_rodada_para_palpite:
            game_id = jogo['id']
            
            # --- CÓDIGO CORRIGIDO AQUI ---
            gol_time1_str = request.form.get(f'gol_time1_{game_id}')
            gol_time2_str = request.form.get(f'gol_time2_{game_id}')
            resultado_palpite = request.form.get(f'resultado_{game_id}')

            if gol_time1_str and gol_time2_str and resultado_palpite:
                gol_time1 = int(gol_time1_str)
                gol_time2 = int(gol_time2_str)
                quem_avanca = request.form.get(f'quem_avanca_{game_id}')

                conn.execute("DELETE FROM palpites WHERE nome = ? AND game_id = ?", (nome, game_id))
                
                conn.execute(
                    "INSERT INTO palpites (nome, rodada, game_id, time1, time2, gol_time1, gol_time2, resultado, status, quem_avanca) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (nome, rodada_selecionada, game_id, jogo['time1_nome'], jogo['time2_nome'], gol_time1, gol_time2, resultado_palpite, 'Pendente', quem_avanca)
                )
                palpites_feitos += 1
        
        conn.commit()
        if palpites_feitos > 0:
            flash(f'{palpites_feitos} palpite(s) registrado(s) com sucesso!', 'success')
        else:
            flash('Nenhum palpite novo foi preenchido para salvar.', 'info')

        return redirect(url_for('adicionar_palpites', campeonato_selecionado=campeonato, rodada_selecionada=rodada_selecionada))

    # A lógica do GET (para exibir a página) permanece a mesma
    campeonato_selecionado = request.args.get('campeonato_selecionado')
    rodada_selecionada = request.args.get('rodada_selecionada', type=int)
    campeonatos = get_api_data("campeonatos") or []
    rodadas_disponiveis = []
    jogos_filtrados = []
    if campeonato_selecionado:
        jogos_api = get_api_data() or []
        fuso_horario_brasil = pytz.timezone('America/Sao_Paulo')
        agora_brasil = datetime.now(fuso_horario_brasil)
        agora_str = agora_brasil.strftime('%Y-%m-%d %H:%M')
        jogos_do_campeonato = [j for j in jogos_api if j['campeonato'] == campeonato_selecionado]
        if jogos_do_campeonato:
            rodadas_disponiveis = sorted(list(set(j['rodada'] for j in jogos_do_campeonato if j.get('data_hora', '') > agora_str)))
        if rodada_selecionada:
            jogos_filtrados = [j for j in jogos_do_campeonato if j['rodada'] == rodada_selecionada and j.get('data_hora', '') > agora_str]

    palpiteiros = ["Ariel", "Arthur", "Carlos", "Celso", "Gabriel", "Lucas"]
    return render_template('adicionar_palpites.html',
        campeonatos=campeonatos,
        campeonato_selecionado=campeonato_selecionado,
        rodadas=rodadas_disponiveis,
        rodada_selecionada=rodada_selecionada,
        jogos=jogos_filtrados,
        palpiteiros=palpiteiros
    )

@app.route('/chaveamento')
def chaveamento():
    conn = get_db()
    jogos_api_map = get_jogos_from_api(as_dict=True)
    
    resultados_db = conn.execute("SELECT * FROM jogos").fetchall()
    resultados_map = {res['id']: dict(res) for res in resultados_db}
    
    palpites_db = conn.execute("SELECT * FROM palpites").fetchall()
    palpites_por_jogo = defaultdict(list)
    for palpite in palpites_db:
        palpites_por_jogo[palpite['game_id']].append(dict(palpite))

    confrontos_mata_mata = defaultdict(lambda: {'ida': None, 'volta': None})
    for game_id, jogo_api in jogos_api_map.items():
        if jogo_api.get('fase') == 'mata-mata' and jogo_api.get('confronto_id'):
            jogo_completo = jogo_api.copy()
            if game_id in resultados_map:
                jogo_completo.update(resultados_map[game_id])
            jogo_completo['palpites'] = sorted(palpites_por_jogo.get(game_id, []), key=lambda p: p['nome'])
            
            if jogo_completo['rodada'] % 2 != 0:
                confrontos_mata_mata[jogo_completo['confronto_id']]['ida'] = jogo_completo
            else:
                confrontos_mata_mata[jogo_completo['confronto_id']]['volta'] = jogo_completo
    
    confrontos_ordenados = sorted(confrontos_mata_mata.values(), key=lambda c: c['ida']['id'] if c.get('ida') else 0)

    oitavas = [c for c in confrontos_ordenados if c.get('ida') and 1 <= c['ida']['confronto_id'] <= 8]
    quartas = [c for c in confrontos_ordenados if c.get('ida') and 9 <= c['ida']['confronto_id'] <= 12]
    semis =   [c for c in confrontos_ordenados if c.get('ida') and 13 <= c['ida']['confronto_id'] <= 14]
    final =   [c for c in confrontos_ordenados if c.get('ida') and c['ida']['confronto_id'] == 15]
    
    campeao = {'nome': 'A definir', 'img': 'https://placehold.co/80x80/eee/006400?text=?'}
    if final and final[0].get('ida') and final[0]['ida'].get('time_que_avancou'):
        winner_name = final[0]['ida']['time_que_avancou']
        winner_img = ''
        if final[0]['ida']['time1_nome'] == winner_name:
            winner_img = final[0]['ida']['time1_img']
        else:
            winner_img = final[0]['ida']['time2_img']
        campeao = {'nome': winner_name, 'img': winner_img}

    return render_template('chaveamento.html', 
                           oitavas=oitavas,
                           quartas=quartas,
                           semis=semis,
                           final=final,
                           campeao=campeao)

@app.route('/estatisticas')
def estatisticas():
    conn = get_db()

    # Busca estatísticas gerais (sem alterações aqui)
    estatisticas_completas = conn.execute('''
        SELECT nome, (pontos + pontos_bonus) as total_pontos, pontos, acertos, erros,
               CASE WHEN (acertos + erros) = 0 THEN 0.0 ELSE ROUND((acertos * 100.0 / (acertos + erros)), 1) END as percentual_acertos
        FROM pontuacao ORDER BY total_pontos DESC, acertos DESC
    ''').fetchall()

    maior_pontuador = estatisticas_completas[0] if estatisticas_completas else None
    quem_acertou_mais = sorted(estatisticas_completas, key=lambda x: x['acertos'], reverse=True)[0] if estatisticas_completas else None

    # --- INÍCIO DA LÓGICA CORRIGIDA PARA SEQUÊNCIAS ---
    
    # 1. Busca os dados dos jogos da API para obter a data e hora
    jogos_api_map = get_jogos_from_api(as_dict=True)

    # 2. Descobre a última rodada com palpites avaliados
    rodada_atual_row = conn.execute("SELECT MAX(rodada) as rodada FROM palpites WHERE status != 'Pendente'").fetchone()
    rodada_atual_bonus = rodada_atual_row['rodada'] if rodada_atual_row and rodada_atual_row['rodada'] else 0
    
    sequencias_info = defaultdict(int)
    
    if rodada_atual_bonus > 0:
        # 3. Pega os palpites do banco de dados local
        palpites_da_rodada_db = conn.execute("""
            SELECT nome, status, game_id 
            FROM palpites 
            WHERE status != 'Pendente' AND rodada = ?
        """, (rodada_atual_bonus,)).fetchall()

        # 4. Adiciona a data e hora da API a cada palpite
        palpites_com_data = []
        for palpite in palpites_da_rodada_db:
            palpite_dict = dict(palpite)
            jogo_info = jogos_api_map.get(palpite['game_id'])
            if jogo_info:
                palpite_dict['data_hora'] = jogo_info.get('data_hora', '')
                palpites_com_data.append(palpite_dict)
        
        # 5. Ordena a lista de palpites pelo nome e pela data/hora do jogo
        palpites_ordenados = sorted(palpites_com_data, key=lambda p: (p['nome'], p['data_hora']))

        # 6. Calcula a SEQUÊNCIA ATUAL para cada jogador usando a lista ordenada
        jogadores = {jogador['nome'] for jogador in estatisticas_completas}
        for nome_jogador in jogadores:
            palpites_do_jogador = [p for p in palpites_ordenados if p['nome'] == nome_jogador]
            
            sequencia_atual = 0
            for palpite in palpites_do_jogador:
                if "Erro" not in palpite['status']:
                    sequencia_atual += 1
                else:
                    sequencia_atual = 0 # Zera a sequência no primeiro erro
            
            sequencias_info[nome_jogador] = sequencia_atual

    # Prepara os dados para o template
    sequencias_para_template = []
    for jogador in estatisticas_completas:
        nome = jogador['nome']
        max_streak = sequencias_info[nome]
        sequencias_para_template.append({
            'nome': nome,
            'sequencia': max_streak,
            'bonus': '🔥 Bônus Disponível!' if max_streak >= 3 else '--'
        })
    
    # --- FIM DA LÓGICA CORRIGIDA ---

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
    # Pega o usuário que está logado
    usuario_atual = session.get('username')
    senha_digitada = request.form.get('password')

    # Verifica se a senha digitada é a senha correta DESTE usuário
    if not usuario_atual or MODERADORES.get(usuario_atual) != senha_digitada:
        print("\n[LOG] Tentativa de bônus com senha incorreta")
        flash('Senha incorreta!', 'danger')
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

@app.route('/palpites')
def exibir_palpites():
    conn = get_db()
    
    # 1. Obter todos os jogos da API e criar o 'jogos_map'
    jogos_api_map = get_jogos_from_api(as_dict=True)
    if not jogos_api_map:
        flash("Atenção: Não foi possível carregar a lista de jogos. A API pode estar offline.", "warning")
        jogos_api_map = {}

    # 2. Mescla os resultados do banco de palpites no mapa de jogos
    resultados_db = conn.execute("SELECT * FROM jogos").fetchall()
    for res in resultados_db:
        if res['id'] in jogos_api_map:
            jogos_api_map[res['id']].update(dict(res))

    # 3. Obter as rodadas disponíveis a partir dos dados da API
    rodadas_existentes = sorted(list(set(j['rodada'] for j in jogos_api_map.values())))
    
    rodada_param = request.args.get('rodada', type=int)
    
    # Define a rodada a ser exibida
    rodada_para_exibir = rodada_param
    if not rodada_para_exibir or rodada_para_exibir not in rodadas_existentes:
        rodada_recente_row = conn.execute("SELECT MAX(rodada) as max_rodada FROM palpites").fetchone()
        if rodada_recente_row and rodada_recente_row['max_rodada'] in rodadas_existentes:
            rodada_para_exibir = rodada_recente_row['max_rodada']
        else:
            rodada_para_exibir = rodadas_existentes[0] if rodadas_existentes else 1

    # 4. Buscar palpites do banco de dados local para a rodada selecionada
    palpites_db = conn.execute("SELECT * FROM palpites WHERE rodada = ? ORDER BY nome", (rodada_para_exibir,)).fetchall()

    # 5. Agrupar os palpites por jogador
    palpites_agrupados = defaultdict(list)
    for palpite in palpites_db:
        palpites_agrupados[palpite['nome']].append(dict(palpite))

    # Lógica de navegação entre rodadas
    idx_rodada = rodadas_existentes.index(rodada_para_exibir) if rodada_para_exibir in rodadas_existentes else -1
    tem_proxima = idx_rodada != -1 and idx_rodada < len(rodadas_existentes) - 1
    tem_anterior = idx_rodada > 0
    proxima_rodada = rodadas_existentes[idx_rodada + 1] if tem_proxima else None
    anterior_rodada = rodadas_existentes[idx_rodada - 1] if tem_anterior else None

    # 6. Passar TODOS os dados necessários para o template, incluindo o jogos_map
    return render_template(
        'palpites.html',
        palpites_agrupados=palpites_agrupados,
        jogos_map=jogos_api_map,
        rodada_exibida_num=rodada_para_exibir,
        tem_proxima=tem_proxima,
        proxima_rodada=proxima_rodada,
        tem_anterior=tem_anterior,
        anterior_rodada=anterior_rodada
    )

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
        password = request.form.get('password')
        ip_cliente = request.remote_addr
        
        # VERIFICAÇÃO NOVA: Olha se o usuário existe na lista e se a senha bate
        if username in MODERADORES and MODERADORES[username] == password:
            session['logged_in'] = True
            session['username'] = username  # Guardamos quem logou para usar depois
            print(f"\n[LOG - login]: Login BEM-SUCEDIDO para '{username}' IP {ip_cliente}.\n")
            flash(f'Bem-vindo, {username}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            print(f"\n[LOG - login]: Falha para '{username}' IP {ip_cliente}.\n")
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
        game_id = int(request.form['game_id'])
        placar1 = int(request.form['placar_time1'])
        placar2 = int(request.form['placar_time2'])
        avancou = request.form.get('time_que_avancou')
        
        # --- LÓGICA DO NOVO STATUS ---
        # Verifica se a checkbox foi marcada. Se sim, o status é 'Finalizado'.
        # Se não, o status é 'Ao Vivo' (para placares parciais).
        status_jogo = 'Finalizado' if request.form.get('status_finalizado') else 'Ao Vivo'
        # --- FIM DA LÓGICA ---

        cursor = conn.cursor()
        cursor.execute("SELECT id FROM jogos WHERE id = ?", (game_id,))
        if cursor.fetchone():
            # Atualiza o jogo existente com o novo status
            cursor.execute("UPDATE jogos SET placar_time1=?, placar_time2=?, status=?, time_que_avancou=? WHERE id=?", (placar1, placar2, status_jogo, avancou, game_id))
        else:
            # Insere um novo jogo com o novo status
            cursor.execute("INSERT INTO jogos (id, placar_time1, placar_time2, status, time_que_avancou) VALUES (?, ?, ?, ?, ?)", (game_id, placar1, placar2, status_jogo, avancou))
        
        conn.commit()
        flash(f'Resultado do jogo {game_id} salvo como "{status_jogo}".', 'success')
        return redirect(url_for('set_game_result', 
                                campeonato_selecionado=request.form.get('campeonato_selecionado'), 
                                rodada_selecionada=request.form.get('rodada_selecionada')))

    # --- LÓGICA DO GET (permanece a mesma) ---
    campeonato_selecionado = request.args.get('campeonato_selecionado')
    rodada_selecionada = request.args.get('rodada_selecionada', type=int)
    campeonatos = get_api_data("campeonatos") or []
    rodadas_disponiveis = []
    jogos_filtrados = []
    
    if campeonato_selecionado:
        jogos_api = get_api_data("jogos") or []
        jogos_do_campeonato = [j for j in jogos_api if j['campeonato'] == campeonato_selecionado]
        if jogos_do_campeonato:
            rodadas_disponiveis = sorted(list(set(j['rodada'] for j in jogos_do_campeonato)))
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
    jogos_api_map = get_jogos_from_api(as_dict=True)

    # Busca apenas os jogos que o admin marcou como 'Finalizado'
    resultados_db = conn.execute("SELECT * FROM jogos WHERE status = 'Finalizado'").fetchall()
    
    if not resultados_db:
        flash('Nenhum jogo novo marcado como "Finalizado" para calcular a pontuação.', 'info')
        return redirect(url_for('admin_dashboard'))

    palpites = conn.execute("SELECT * FROM palpites").fetchall()
    resultados_map = {r['id']: dict(r) for r in resultados_db}

    atualizacao_pontos = defaultdict(lambda: {'pontos': 0, 'acertos': 0, 'erros': 0})

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
                # --- NOVA LÓGICA HIERÁRQUICA PARA MATA-MATA ---
                if acerto_placar and acerto_resultado and acerto_avanco: # Placar + Resultado + Avanço
                    pontos_ganhos, status_palpite = 5, "Acerto Total! (5 pts)"
                elif acerto_placar and acerto_resultado: # Placar + Resultado, mas errou o avanço
                    pontos_ganhos, status_palpite = 4, "Acerto Placar + Resultado (4 pts)"
                elif acerto_resultado and acerto_avanco: # Errou o placar, mas acertou o resto
                    pontos_ganhos, status_palpite = 2, "Acerto Resultado + Avanço (2 pts)"
                elif acerto_placar: # Errou o resultado, mas acertou o placar
                    pontos_ganhos, status_palpite = 2, "Acerto Placar (2 pts)"
                elif acerto_resultado: # Acertou apenas o resultado
                    pontos_ganhos, status_palpite = 1, "Acerto Apenas Resultado (1 pt)"
                elif acerto_avanco: # Acertou apenas quem avança
                    pontos_ganhos, status_palpite = 1, "Acerto Apenas Avanço (1 pt)"
            
            else: # --- LÓGICA PARA FASE DE GRUPOS ---
                if acerto_placar and acerto_resultado: # Placar + Resultado
                    pontos_ganhos, status_palpite = 4, "Acerto Total (4 pts)"
                elif acerto_placar: # Apenas o placar
                    pontos_ganhos, status_palpite = 2, "Acerto Placar (2 pts)"
                elif acerto_resultado: # Apenas o resultado
                    pontos_ganhos, status_palpite = 1, "Acerto Resultado (1 pt)"
            
            if pontos_ganhos > 0:
                atualizacao_pontos[nome_palpiteiro]['pontos'] += pontos_ganhos
                atualizacao_pontos[nome_palpiteiro]['acertos'] += 1
            else:
                atualizacao_pontos[nome_palpiteiro]['erros'] += 1
            
            conn.execute("UPDATE palpites SET status = ? WHERE id = ?", (status_palpite, palpite['id']))

    for nome, stats in atualizacao_pontos.items():
        conn.execute("""
            UPDATE pontuacao 
            SET pontos = pontos + ?, 
                acertos = acertos + ?, 
                erros = erros + ?
            WHERE nome = ?
        """, (stats['pontos'], stats['acertos'], stats['erros'], nome))

    ids_processados = list(resultados_map.keys())
    if ids_processados:
        placeholders = ','.join('?' for _ in ids_processados)
        conn.execute(f"UPDATE jogos SET status = 'Processado' WHERE id IN ({placeholders})", ids_processados)
    
    conn.commit()
    flash('Pontuação acumulada e atualizada com sucesso!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/palpite_campeao', methods=['GET', 'POST'])
def palpite_campeao():
    conn = get_db()
    
    if request.method == 'POST':
        nome = request.form['nome']
        campeonato = request.form['campeonato_selecionado']
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
    campeonatos = get_api_data("campeonatos") or []
    
    times_filtrados = []
    if campeonato_selecionado:
        jogos_api = get_api_data() or []
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
    
    # 1. Garante que a tabela de palpites existe (para não dar erro)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS palpite_campeao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            campeonato TEXT,
            time_campeao TEXT,
            time_campeao_img TEXT,
            data_palpite TEXT
        )
    ''')
    
    # 2. Busca os palpites dos usuários
    palpites = conn.execute('''
        SELECT p.nome, p.campeonato, p.time_campeao, p.data_palpite, p.time_campeao_img
        FROM palpite_campeao p
        ORDER BY p.campeonato ASC, p.nome ASC
    ''').fetchall()
    
    # 3. Busca os campeões oficiais definidos pelo Admin
    # Se a tabela não existir (admin nunca definiu), cria vazia ou ignora
    try:
        campeoes_db = conn.execute('SELECT * FROM campeao_real').fetchall()
    except sqlite3.OperationalError:
        campeoes_db = []

    # Cria o mapa para conferência (usado para pintar de verde quem acertou)
    campeoes_map = {c['campeonato']: dict(c) for c in campeoes_db}

    return render_template('ver_palpites_campeao.html', 
                           palpites=palpites, 
                           campeoes_reais=campeoes_map)

@app.route('/admin/set_champion', methods=['GET', 'POST'])
@login_required
def set_champion():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Garante que a tabela correta (campeao_real) existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campeao_real (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campeonato TEXT NOT NULL UNIQUE,
            time_campeao TEXT,
            time_campeao_img TEXT,
            data_definicao TEXT
        )
    ''')
    conn.commit()

    # 2. Busca lista de times da API para o dropdown
    jogos_api = get_api_data("jogos") or []
    teams_dict = {}
    for jogo in jogos_api:
        if jogo['time1_nome'] not in teams_dict:
            teams_dict[jogo['time1_nome']] = {'name': jogo['time1_nome'], 'img_src': jogo['time1_img']}
        if jogo['time2_nome'] not in teams_dict:
            teams_dict[jogo['time2_nome']] = {'name': jogo['time2_nome'], 'img_src': jogo['time2_img']}
    
    all_teams_list = sorted(teams_dict.values(), key=lambda t: t['name'])
    
    # 3. Busca lista de campeonatos da API
    campeonatos_list = get_api_data("campeonatos") or []

    if request.method == 'POST':
        campeonato_selecionado = request.form.get('campeonato_selecionado')
        campeao_nome = request.form.get('campeao_nome')
        
        if not campeonato_selecionado or not campeao_nome:
            flash('Por favor, selecione o campeonato e o time campeão.', 'warning')
            return redirect(url_for('set_champion'))

        # Encontra a imagem do time
        campeao_info = next((team for team in all_teams_list if team['name'] == campeao_nome), None)
        campeao_img = campeao_info['img_src'] if campeao_info else None
        data_hoje = datetime.now().strftime('%Y-%m-%d %H:%M')

        try:
            # Usa INSERT OR REPLACE para atualizar se já existir um campeão para esse campeonato
            cursor.execute('''
                INSERT OR REPLACE INTO campeao_real (campeonato, time_campeao, time_campeao_img, data_definicao)
                VALUES (?, ?, ?, ?)
            ''', (campeonato_selecionado, campeao_nome, campeao_img, data_hoje))
            
            conn.commit()
            flash(f'Campeão do {campeonato_selecionado} definido como {campeao_nome}!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao definir campeão: {e}', 'danger')
            
        return redirect(url_for('set_champion'))

    # Busca os campeões atuais para exibir na lista
    campeoes_atuais = conn.execute('SELECT * FROM campeao_real').fetchall()

    return render_template('set_champion.html', 
                           teams=all_teams_list, 
                           campeonatos=campeonatos_list,
                           campeoes_atuais=campeoes_atuais)

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


@app.route('/admin/anuncios', methods=['GET', 'POST'])
@login_required
def gerenciar_anuncios():
    conn = get_db()
    if request.method == 'POST':
        titulo = request.form['titulo']
        mensagem = request.form['mensagem']
        tipo = request.form['tipo']
        data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            'INSERT INTO anuncios (titulo, mensagem, tipo, data_criacao) VALUES (?, ?, ?, ?)',
            (titulo, mensagem, tipo, data_criacao)
        )
        conn.commit()
        flash('Anúncio adicionado com sucesso!', 'success')
        return redirect(url_for('gerenciar_anuncios'))

    anuncios = conn.execute('SELECT * FROM anuncios ORDER BY data_criacao DESC').fetchall()
    return render_template('gerenciar_anuncios.html', anuncios=anuncios)

@app.route('/admin/reset_season', methods=['POST'])
@login_required
def reset_season():
    usuario_atual = session.get('username')
    senha_digitada = request.form.get('password')
    
    if not usuario_atual or MODERADORES.get(usuario_atual) != senha_digitada:
        flash('Senha incorreta! A temporada não foi reiniciada.', 'danger')
        return redirect(url_for('admin_dashboard'))

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE pontuacao SET pontos = 0, acertos = 0, erros = 0, pontos_bonus = 0")
        cursor.execute("DELETE FROM jogos")
        cursor.execute("DELETE FROM palpites")
        cursor.execute("DELETE FROM palpite_campeao")
        cursor.execute("DELETE FROM campeao_real")
        conn.commit()
        
        print("\n[LOG] NOVA TEMPORADA INICIADA! DADOS ANTIGOS APAGADOS.\n")
        flash('Temporada reiniciada com sucesso! Pontos zerados e jogos antigos removidos.', 'success')
    except Exception as e:
        conn.rollback()
        print(f"\n[LOG] Erro ao reiniciar temporada: {e}")
        flash(f'Erro ao reiniciar temporada: {e}', 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/anuncios/delete/<int:anuncio_id>', methods=['POST'])
@login_required
def deletar_anuncio(anuncio_id):
    conn = get_db()
    conn.execute('DELETE FROM anuncios WHERE id = ?', (anuncio_id,))
    conn.commit()
    flash('Anúncio apagado com sucesso!', 'success')
    return redirect(url_for('gerenciar_anuncios'))

# @app.route('/')
# def manutencao():
#     return render_template('manut.html')

# if __name__ == '__main__':
#     app.run(debug=True,host="0.0.0.0",port=5000)