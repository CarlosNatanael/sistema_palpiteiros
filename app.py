from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from collections import defaultdict
from datetime import datetime
from functools import wraps
from config import API_BASE_URL, MODERADORES
import requests
import sqlite3
import pytz
import os


# ==== TESTE LOCAL =======
# API_BASE_URL = "http://127.0.0.1:5001/api/v1"

# --- Configurações ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'palpites.db')

app = Flask(__name__)
app.secret_key = 'ALJDHA76797#%*#JKOL'
TEMPORADA_ATUAL = "3ª Temporada"
PALPITEIROS = ["Ariel", "Arthur", "Carlos", "Celso", "Gabriel", "Lucas"]

# --- Banco de Dados ---
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH, timeout=10)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- Helpers da API ---
def get_api_data(endpoint="jogos"):
    """Função auxiliar para fazer chamadas à API."""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None if endpoint == "jogos" else []

def get_jogos_from_api(as_dict=True):
    """Busca os jogos da API."""
    jogos = get_api_data("jogos") or []
    if as_dict:
        return {jogo['id']: jogo for jogo in jogos}
    return jogos

# --- Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Filtros Jinja2 ---
@app.template_filter('format_date_br')
def format_date_br_filter(date_str):
    if not date_str:
        return ""
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

# --- Helpers de Data/Hora ---
def get_brasil_time():
    """Retorna o horário atual no fuso do Brasil."""
    fuso_horario_brasil = pytz.timezone('America/Sao_Paulo')
    return datetime.now(fuso_horario_brasil)

# --- Rotas Principais ---
@app.route('/')
def index():
    conn = get_db()
    
    # Anúncios
    anuncios = conn.execute("SELECT * FROM anuncios ORDER BY data_criacao DESC LIMIT 3").fetchall()
    
    # Jogos da API
    jogos_api_map = get_jogos_from_api()
    if not jogos_api_map:
        flash("Atenção: A API de jogos parece estar offline.", "warning")
        return render_template('index.html', anuncios=anuncios)
    
    # Lógica de rodadas
    todas_rodadas = sorted(set(j['rodada'] for j in jogos_api_map.values()))
    rodada_ativa = request.args.get('rodada', type=int)
    
    if not rodada_ativa or rodada_ativa not in todas_rodadas:
        rodada_ativa = todas_rodadas[-1] if todas_rodadas else 1
    
    # Navegação entre rodadas
    idx_rodada = todas_rodadas.index(rodada_ativa)
    tem_anterior = idx_rodada > 0
    tem_proxima = idx_rodada < len(todas_rodadas) - 1
    anterior_rodada = todas_rodadas[idx_rodada - 1] if tem_anterior else None
    proxima_rodada = todas_rodadas[idx_rodada + 1] if tem_proxima else None
    
    # Resultados do banco
    resultados_db = conn.execute("SELECT * FROM jogos").fetchall()
    resultados_map = {res['id']: dict(res) for res in resultados_db}
    
    # Separar jogos por status
    agora_brasil = get_brasil_time()
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
    
    # Pontuação
    pontuacao = conn.execute("""
        SELECT nome, (pontos + pontos_bonus) as total_pontos, acertos, erros 
        FROM pontuacao ORDER BY total_pontos DESC, acertos DESC
    """).fetchall()
    
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

@app.route('/adicionar_palpites', methods=['GET', 'POST'])
def adicionar_palpites():
    conn = get_db()
    
    if request.method == 'POST':
        return processar_palpites(conn)
    
    return renderizar_pagina_palpites(conn)

def processar_palpites(conn):
    """Processa o envio de palpites."""
    nome = request.form.get('nome')
    rodada_selecionada = int(request.form.get('rodada_selecionada'))
    campeonato = request.form.get('campeonato_selecionado')
    
    if not nome:
        flash('Você precisa selecionar o seu nome para salvar os palpites.', 'warning')
        return redirect(url_for('adicionar_palpites', 
                               campeonato_selecionado=campeonato, 
                               rodada_selecionada=rodada_selecionada))
    
    # Criar jogador se não existir
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM pontuacao WHERE nome = ?", (nome,))
    if not cursor.fetchone():
        conn.execute("INSERT INTO pontuacao (nome) VALUES (?)", (nome,))
    
    # Processar palpites
    jogos_api = get_api_data("jogos") or []
    agora_str = get_brasil_time().strftime('%Y-%m-%d %H:%M')
    
    jogos_disponiveis = [
        j for j in jogos_api 
        if j['campeonato'] == campeonato and 
           j['rodada'] == rodada_selecionada and 
           j.get('data_hora', '') > agora_str
    ]
    
    palpites_feitos = 0
    for jogo in jogos_disponiveis:
        game_id = jogo['id']
        gol_time1 = request.form.get(f'gol_time1_{game_id}')
        gol_time2 = request.form.get(f'gol_time2_{game_id}')
        resultado = request.form.get(f'resultado_{game_id}')
        
        if gol_time1 and gol_time2 and resultado:
            gol_time1 = int(gol_time1)
            gol_time2 = int(gol_time2)
            quem_avanca = request.form.get(f'quem_avanca_{game_id}')
            
            # Remove palpite existente
            conn.execute("DELETE FROM palpites WHERE nome = ? AND game_id = ?", (nome, game_id))
            
            # Insere novo palpite
            conn.execute("""
                INSERT INTO palpites (nome, rodada, game_id, time1, time2, 
                                     gol_time1, gol_time2, resultado, status, quem_avanca) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, rodada_selecionada, game_id, jogo['time1_nome'], 
                  jogo['time2_nome'], gol_time1, gol_time2, resultado, 'Pendente', quem_avanca))
            palpites_feitos += 1
    
    conn.commit()
    
    if palpites_feitos > 0:
        flash(f'{palpites_feitos} palpite(s) registrado(s) com sucesso!', 'success')
    else:
        flash('Nenhum palpite novo foi preenchido para salvar.', 'info')
    
    return redirect(url_for('adicionar_palpites', 
                           campeonato_selecionado=campeonato, 
                           rodada_selecionada=rodada_selecionada))

def renderizar_pagina_palpites(conn):
    """Renderiza a página de adicionar palpites."""
    campeonato_selecionado = request.args.get('campeonato_selecionado')
    rodada_selecionada = request.args.get('rodada_selecionada', type=int)
    
    campeonatos = get_api_data("campeonatos") or []
    rodadas_disponiveis = []
    jogos_filtrados = []
    
    if campeonato_selecionado:
        jogos_api = get_api_data() or []
        agora_str = get_brasil_time().strftime('%Y-%m-%d %H:%M')
        
        jogos_do_campeonato = [j for j in jogos_api if j['campeonato'] == campeonato_selecionado]
        
        if jogos_do_campeonato:
            rodadas_disponiveis = sorted(set(
                j['rodada'] for j in jogos_do_campeonato 
                if j.get('data_hora', '') > agora_str
            ))
        
        if rodada_selecionada:
            jogos_filtrados = [
                j for j in jogos_do_campeonato 
                if j['rodada'] == rodada_selecionada and j.get('data_hora', '') > agora_str
            ]
    
    return render_template('adicionar_palpites.html',
        campeonatos=campeonatos,
        campeonato_selecionado=campeonato_selecionado,
        rodadas=rodadas_disponiveis,
        rodada_selecionada=rodada_selecionada,
        jogos=jogos_filtrados,
        palpiteiros=PALPITEIROS
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
    
    # Organizar confrontos do mata-mata
    confrontos_mata_mata = defaultdict(lambda: {'ida': None, 'volta': None})
    for game_id, jogo_api in jogos_api_map.items():
        if jogo_api.get('fase') == 'mata-mata' and jogo_api.get('confronto_id'):
            jogo_completo = jogo_api.copy()
            if game_id in resultados_map:
                jogo_completo.update(resultados_map[game_id])
            jogo_completo['palpites'] = sorted(palpites_por_jogo.get(game_id, []), 
                                              key=lambda p: p['nome'])
            
            if jogo_completo['rodada'] % 2 != 0:
                confrontos_mata_mata[jogo_completo['confronto_id']]['ida'] = jogo_completo
            else:
                confrontos_mata_mata[jogo_completo['confronto_id']]['volta'] = jogo_completo
    
    confrontos_ordenados = sorted(confrontos_mata_mata.values(), 
                                 key=lambda c: c['ida']['id'] if c.get('ida') else 0)
    
    # Separar por fases
    oitavas = [c for c in confrontos_ordenados if c.get('ida') and 1 <= c['ida']['confronto_id'] <= 8]
    quartas = [c for c in confrontos_ordenados if c.get('ida') and 9 <= c['ida']['confronto_id'] <= 12]
    semis = [c for c in confrontos_ordenados if c.get('ida') and 13 <= c['ida']['confronto_id'] <= 14]
    final = [c for c in confrontos_ordenados if c.get('ida') and c['ida']['confronto_id'] == 15]
    
    # Determinar campeão
    campeao = {'nome': 'A definir', 'img': 'https://placehold.co/80x80/eee/006400?text=?'}
    if final and final[0].get('ida') and final[0]['ida'].get('time_que_avancou'):
        winner_name = final[0]['ida']['time_que_avancou']
        winner_img = final[0]['ida']['time1_img'] if final[0]['ida']['time1_nome'] == winner_name else final[0]['ida']['time2_img']
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
    
    # Estatísticas gerais
    estatisticas_completas = conn.execute('''
        SELECT nome, (pontos + pontos_bonus) as total_pontos, pontos, acertos, erros,
               CASE WHEN (acertos + erros) = 0 THEN 0.0 
                    ELSE ROUND((acertos * 100.0 / (acertos + erros)), 1) 
               END as percentual_acertos
        FROM pontuacao ORDER BY total_pontos DESC, acertos DESC
    ''').fetchall()
    
    maior_pontuador = estatisticas_completas[0] if estatisticas_completas else None
    quem_acertou_mais = sorted(estatisticas_completas, 
                              key=lambda x: x['acertos'], reverse=True)[0] if estatisticas_completas else None
    
    # Sequências de acertos
    sequencias_info = calcular_sequencias_acertos(conn)
    
    # Preparar dados para template
    sequencias_para_template = []
    for jogador in estatisticas_completas:
        nome = jogador['nome']
        max_streak = sequencias_info.get(nome, 0)
        sequencias_para_template.append({
            'nome': nome,
            'sequencia': max_streak,
            'bonus': '🔥 Bônus Disponível!' if max_streak >= 3 else '--'
        })
    
    rodada_atual_bonus = conn.execute(
        "SELECT MAX(rodada) as rodada FROM palpites WHERE status != 'Pendente'"
    ).fetchone()
    rodada_atual_bonus = rodada_atual_bonus['rodada'] if rodada_atual_bonus and rodada_atual_bonus['rodada'] else 0
    
    return render_template('estatisticas.html',
                           maior_pontuador=maior_pontuador,
                           quem_acertou_mais=quem_acertou_mais,
                           estatisticas_completas=estatisticas_completas,
                           sequencias=sequencias_para_template,
                           rodada_atual_bonus=rodada_atual_bonus)

def calcular_sequencias_acertos(conn):
    """Calcula sequências de acertos para bônus."""
    jogos_api_map = get_jogos_from_api(as_dict=True)
    rodada_atual_row = conn.execute(
        "SELECT MAX(rodada) as rodada FROM palpites WHERE status != 'Pendente'"
    ).fetchone()
    
    rodada_atual = rodada_atual_row['rodada'] if rodada_atual_row and rodada_atual_row['rodada'] else 0
    
    if rodada_atual == 0:
        return {}
    
    # Buscar palpites da rodada atual
    palpites_db = conn.execute("""
        SELECT nome, status, game_id 
        FROM palpites 
        WHERE status != 'Pendente' AND rodada = ?
    """, (rodada_atual,)).fetchall()
    
    # Adicionar data/hora da API
    palpites_com_data = []
    for palpite in palpites_db:
        palpite_dict = dict(palpite)
        jogo_info = jogos_api_map.get(palpite['game_id'])
        if jogo_info:
            palpite_dict['data_hora'] = jogo_info.get('data_hora', '')
            palpites_com_data.append(palpite_dict)
    
    # Ordenar e calcular sequências
    palpites_ordenados = sorted(palpites_com_data, 
                               key=lambda p: (p['nome'], p['data_hora']))
    
    sequencias = {}
    for nome_jogador in set(p['nome'] for p in palpites_ordenados):
        palpites_jogador = [p for p in palpites_ordenados if p['nome'] == nome_jogador]
        sequencia_atual = 0
        
        for palpite in palpites_jogador:
            if "Erro" not in palpite['status']:
                sequencia_atual += 1
            else:
                sequencia_atual = 0
        
        sequencias[nome_jogador] = sequencia_atual
    
    return sequencias

@app.route('/admin/award_bonus', methods=['POST'])
@login_required
def award_bonus():
    """Concede bônus a um jogador."""
    usuario_atual = session.get('username')
    senha_digitada = request.form.get('password')
    
    if not usuario_atual or MODERADORES.get(usuario_atual) != senha_digitada:
        flash('Senha incorreta!', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    nome_jogador = request.form.get('nome_jogador')
    pontos_bonus = 3
    
    if not nome_jogador:
        flash('Você precisa selecionar um jogador para conceder o bônus.', 'warning')
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE pontuacao SET pontos_bonus = pontos_bonus + ? WHERE nome = ?", 
                      (pontos_bonus, nome_jogador))
        conn.commit()
        
        if cursor.rowcount > 0:
            flash(f'Bônus de {pontos_bonus} pontos concedido para {nome_jogador} com sucesso!', 'success')
        else:
            flash(f'Jogador {nome_jogador} não encontrado na tabela de pontuação.', 'danger')
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao conceder bônus: {e}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/regras')
def regra():
    return render_template('regras.html')

@app.route('/palpites')
def exibir_palpites():
    conn = get_db()
    
    # Obter jogos da API
    jogos_api_map = get_jogos_from_api(as_dict=True)
    if not jogos_api_map:
        flash("Atenção: Não foi possível carregar a lista de jogos. A API pode estar offline.", "warning")
        jogos_api_map = {}
    
    # Mesclar resultados
    resultados_db = conn.execute("SELECT * FROM jogos").fetchall()
    for res in resultados_db:
        if res['id'] in jogos_api_map:
            jogos_api_map[res['id']].update(dict(res))
    
    # Lógica de rodadas
    rodadas_existentes = sorted(set(j['rodada'] for j in jogos_api_map.values()))
    rodada_param = request.args.get('rodada', type=int)
    
    if rodada_param and rodada_param in rodadas_existentes:
        rodada_para_exibir = rodada_param
    else:
        rodada_recente_row = conn.execute("SELECT MAX(rodada) as max_rodada FROM palpites").fetchone()
        if rodada_recente_row and rodada_recente_row['max_rodada'] in rodadas_existentes:
            rodada_para_exibir = rodada_recente_row['max_rodada']
        else:
            rodada_para_exibir = rodadas_existentes[0] if rodadas_existentes else 1
    
    # Buscar palpites
    palpites_db = conn.execute("SELECT * FROM palpites WHERE rodada = ? ORDER BY nome", 
                               (rodada_para_exibir,)).fetchall()
    
    # Agrupar palpites
    palpites_agrupados = defaultdict(list)
    for palpite in palpites_db:
        palpites_agrupados[palpite['nome']].append(dict(palpite))
    
    # Navegação entre rodadas
    idx_rodada = rodadas_existentes.index(rodada_para_exibir) if rodada_para_exibir in rodadas_existentes else -1
    tem_proxima = idx_rodada != -1 and idx_rodada < len(rodadas_existentes) - 1
    tem_anterior = idx_rodada > 0
    proxima_rodada = rodadas_existentes[idx_rodada + 1] if tem_proxima else None
    anterior_rodada = rodadas_existentes[idx_rodada - 1] if tem_anterior else None
    
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in MODERADORES and MODERADORES[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash(f'Bem-vindo, {username}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Nome de usuário ou senha incorretos.', 'danger')
    
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('logged_in', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    conn = get_db()
    pontuacao_geral = conn.execute("SELECT nome FROM pontuacao ORDER BY nome").fetchall()
    campeao_atual = conn.execute("SELECT nome FROM campeao_palpiteiros WHERE id = 1").fetchone()
    return render_template('admin_dashboard.html', 
                          pontuacao_geral=pontuacao_geral, 
                          campeao_atual=campeao_atual)

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
    
    conn.execute("""
        INSERT INTO campeao_palpiteiros (temporada, competicao, nome, pontos, acertos, erros, data_definicao) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(temporada) DO UPDATE SET
        competicao=excluded.competicao, nome=excluded.nome, pontos=excluded.pontos, 
        acertos=excluded.acertos, erros=excluded.erros, data_definicao=excluded.data_definicao
    """, (temporada, competicao, jogador_stats['nome'], jogador_stats['total_pontos'], 
          jogador_stats['acertos'], jogador_stats['erros'], 
          datetime.now().strftime('%Y-%m-%d %H:%M')))
    
    conn.commit()
    flash(f'{nome_campeao} foi coroado Campeão da {temporada} ({competicao})!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/historico')
def historico_campeoes():
    conn = get_db()
    campeoes_db = conn.execute("SELECT * FROM campeao_palpiteiros ORDER BY nome ASC, temporada ASC").fetchall()
    
    campeoes_agrupados = defaultdict(list)
    for campeao_data in campeoes_db:
        campeao_dict = dict(campeao_data)
        campeoes_agrupados[campeao_dict['nome']].append(campeao_dict)
    
    return render_template('historico.html', campeoes_agrupados=campeoes_agrupados)

@app.route('/admin/set_game_result', methods=['GET', 'POST'])
@login_required
def set_game_result():
    conn = get_db()
    
    if request.method == 'POST':
        return salvar_resultado_jogo(conn)
    
    return renderizar_pagina_resultados(conn)

def salvar_resultado_jogo(conn):
    """Salva o resultado de um jogo."""
    game_id = int(request.form['game_id'])
    placar1 = int(request.form['placar_time1'])
    placar2 = int(request.form['placar_time2'])
    avancou = request.form.get('time_que_avancou')
    
    status_jogo = 'Finalizado' if request.form.get('status_finalizado') else 'Ao Vivo'
    
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM jogos WHERE id = ?", (game_id,))
    
    if cursor.fetchone():
        cursor.execute("UPDATE jogos SET placar_time1=?, placar_time2=?, status=?, time_que_avancou=? WHERE id=?", 
                      (placar1, placar2, status_jogo, avancou, game_id))
    else:
        cursor.execute("INSERT INTO jogos (id, placar_time1, placar_time2, status, time_que_avancou) VALUES (?, ?, ?, ?, ?)", 
                      (game_id, placar1, placar2, status_jogo, avancou))
    
    conn.commit()
    flash(f'Resultado do jogo {game_id} salvo como "{status_jogo}".', 'success')
    
    return redirect(url_for('set_game_result', 
                           campeonato_selecionado=request.form.get('campeonato_selecionado'), 
                           rodada_selecionada=request.form.get('rodada_selecionada')))

def renderizar_pagina_resultados(conn):
    """Renderiza a página de definir resultados."""
    campeonato_selecionado = request.args.get('campeonato_selecionado')
    rodada_selecionada = request.args.get('rodada_selecionada', type=int)
    
    campeonatos = get_api_data("campeonatos") or []
    rodadas_disponiveis = []
    jogos_filtrados = []
    
    if campeonato_selecionado:
        jogos_api = get_api_data("jogos") or []
        jogos_do_campeonato = [j for j in jogos_api if j['campeonato'] == campeonato_selecionado]
        
        if jogos_do_campeonato:
            rodadas_disponiveis = sorted(set(j['rodada'] for j in jogos_do_campeonato))
        
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
    """Atualiza a pontuação baseada nos jogos finalizados."""
    conn = get_db()
    jogos_api_map = get_jogos_from_api(as_dict=True)
    
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
            pontos_ganhos, status_palpite = calcular_pontuacao_palpite(
                palpite, resultados_map[game_id], jogos_api_map[game_id]
            )
            
            nome_palpiteiro = palpite['nome']
            if pontos_ganhos > 0:
                atualizacao_pontos[nome_palpiteiro]['pontos'] += pontos_ganhos
                atualizacao_pontos[nome_palpiteiro]['acertos'] += 1
            else:
                atualizacao_pontos[nome_palpiteiro]['erros'] += 1
            
            conn.execute("UPDATE palpites SET status = ? WHERE id = ?", 
                        (status_palpite, palpite['id']))
    
    # Atualizar pontuação geral
    for nome, stats in atualizacao_pontos.items():
        conn.execute("""
            UPDATE pontuacao 
            SET pontos = pontos + ?, 
                acertos = acertos + ?, 
                erros = erros + ?
            WHERE nome = ?
        """, (stats['pontos'], stats['acertos'], stats['erros'], nome))
    
    # Marcar jogos como processados
    ids_processados = list(resultados_map.keys())
    if ids_processados:
        placeholders = ','.join('?' for _ in ids_processados)
        conn.execute(f"UPDATE jogos SET status = 'Processado' WHERE id IN ({placeholders})", 
                    ids_processados)
    
    conn.commit()
    flash('Pontuação acumulada e atualizada com sucesso!', 'success')
    return redirect(url_for('admin_dashboard'))

def calcular_pontuacao_palpite(palpite, resultado_jogo, info_jogo):
    """Calcula a pontuação de um palpite individual."""
    # Determinar resultado real
    if resultado_jogo['placar_time1'] > resultado_jogo['placar_time2']:
        resultado_real = 'Vitória (Casa)'
    elif resultado_jogo['placar_time1'] < resultado_jogo['placar_time2']:
        resultado_real = 'Vitória (Fora)'
    else:
        resultado_real = 'Empate'
    
    # Verificar acertos
    acerto_placar = (palpite['gol_time1'] == resultado_jogo['placar_time1'] and 
                     palpite['gol_time2'] == resultado_jogo['placar_time2'])
    acerto_resultado = (palpite['resultado'] == resultado_real)
    acerto_avanco = (palpite['quem_avanca'] is not None and 
                     palpite['quem_avanca'] == resultado_jogo['time_que_avancou'])
    
    # Lógica de pontuação
    if info_jogo['fase'] == 'mata-mata':
        if acerto_placar and acerto_resultado and acerto_avanco:
            return 5, "Acerto Total! (5 pts)"
        elif acerto_placar and acerto_resultado:
            return 4, "Acerto Placar + Resultado (4 pts)"
        elif acerto_resultado and acerto_avanco:
            return 2, "Acerto Resultado + Avanço (2 pts)"
        elif acerto_placar:
            return 2, "Acerto Placar (2 pts)"
        elif acerto_resultado:
            return 1, "Acerto Apenas Resultado (1 pt)"
        elif acerto_avanco:
            return 1, "Acerto Apenas Avanço (1 pt)"
    else:  # Fase de grupos
        if acerto_placar and acerto_resultado:
            return 4, "Acerto Total (4 pts)"
        elif acerto_placar:
            return 2, "Acerto Placar (2 pts)"
        elif acerto_resultado:
            return 1, "Acerto Resultado (1 pt)"
    
    return 0, "Erro (0 pts)"

@app.route('/palpite_campeao', methods=['GET', 'POST'])
def palpite_campeao():
    conn = get_db()
    
    if request.method == 'POST':
        return registrar_palpite_campeao(conn)
    
    return renderizar_pagina_palpite_campeao()

def registrar_palpite_campeao(conn):
    """Registra palpite para campeão."""
    nome = request.form['nome']
    campeonato = request.form['campeonato_selecionado']
    time_campeao = request.form['time_campeao']
    
    # Buscar imagem do time
    jogos_api = get_api_data() or []
    time_campeao_img = None
    for jogo in jogos_api:
        if jogo['time1_nome'] == time_campeao:
            time_campeao_img = jogo['time1_img']
            break
        if jogo['time2_nome'] == time_campeao:
            time_campeao_img = jogo['time2_img']
            break
    
    # Verificar se já existe palpite
    existente = conn.execute('SELECT id FROM palpite_campeao WHERE nome = ? AND campeonato = ?', 
                            (nome, campeonato)).fetchone()
    
    if existente:
        conn.execute('''UPDATE palpite_campeao SET time_campeao = ?, time_campeao_img = ?, 
                      data_palpite = ? WHERE id = ?''', 
                    (time_campeao, time_campeao_img, datetime.now().strftime('%Y-%m-%d %H:%M'), 
                     existente['id']))
    else:
        conn.execute('''INSERT INTO palpite_campeao (nome, campeonato, time_campeao, 
                      time_campeao_img, data_palpite) VALUES (?, ?, ?, ?, ?)''', 
                    (nome, campeonato, time_campeao, time_campeao_img, 
                     datetime.now().strftime('%Y-%m-%d %H:%M')))
    
    conn.commit()
    flash('Seu palpite para campeão foi registrado!', 'success')
    return redirect(url_for('ver_palpites_campeao'))

def renderizar_pagina_palpite_campeao():
    """Renderiza a página de palpite para campeão."""
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
        
        times_filtrados = [{'name': nome, 'img_src': img} 
                          for nome, img in sorted(times_do_campeonato.items())]
    
    return render_template('palpite_campeao.html', 
        palpiteiros=PALPITEIROS, 
        campeonatos=campeonatos,
        campeonato_selecionado=campeonato_selecionado,
        times=times_filtrados
    )

@app.route('/ver_palpites_campeao')
def ver_palpites_campeao():
    conn = get_db()
    
    # Criar tabela se não existir
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
    
    # Buscar palpites
    palpites = conn.execute('''
        SELECT p.nome, p.campeonato, p.time_campeao, p.data_palpite, p.time_campeao_img
        FROM palpite_campeao p
        ORDER BY p.campeonato ASC, p.nome ASC
    ''').fetchall()
    
    # Buscar campeões reais
    try:
        campeoes_db = conn.execute('SELECT * FROM campeao_real').fetchall()
    except sqlite3.OperationalError:
        campeoes_db = []
    
    campeoes_map = {c['campeonato']: dict(c) for c in campeoes_db}
    
    return render_template('ver_palpites_campeao.html', 
                           palpites=palpites, 
                           campeoes_reais=campeoes_map)

@app.route('/admin/set_champion', methods=['GET', 'POST'])
@login_required
def set_champion():
    conn = get_db()
    cursor = conn.cursor()
    
    # Criar tabela se não existir
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
    
    # Buscar times e campeonatos
    jogos_api = get_api_data("jogos") or []
    times_dict = {}
    
    for jogo in jogos_api:
        times_dict[jogo['time1_nome']] = {'name': jogo['time1_nome'], 'img_src': jogo['time1_img']}
        times_dict[jogo['time2_nome']] = {'name': jogo['time2_nome'], 'img_src': jogo['time2_img']}
    
    all_teams_list = sorted(times_dict.values(), key=lambda t: t['name'])
    campeonatos_list = get_api_data("campeonatos") or []
    
    if request.method == 'POST':
        campeonato_selecionado = request.form.get('campeonato_selecionado')
        campeao_nome = request.form.get('campeao_nome')
        
        if not campeonato_selecionado or not campeao_nome:
            flash('Por favor, selecione o campeonato e o time campeão.', 'warning')
            return redirect(url_for('set_champion'))
        
        # Encontrar imagem do time
        campeao_info = next((team for team in all_teams_list if team['name'] == campeao_nome), None)
        campeao_img = campeao_info['img_src'] if campeao_info else None
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO campeao_real (campeonato, time_campeao, time_campeao_img, data_definicao)
                VALUES (?, ?, ?, ?)
            ''', (campeonato_selecionado, campeao_nome, campeao_img, 
                  datetime.now().strftime('%Y-%m-%d %H:%M')))
            
            conn.commit()
            flash(f'Campeão do {campeonato_selecionado} definido como {campeao_nome}!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao definir campeão: {e}', 'danger')
        
        return redirect(url_for('set_champion'))
    
    # Buscar campeões atuais
    campeoes_atuais = conn.execute('SELECT * FROM campeao_real').fetchall()
    
    return render_template('set_champion.html', 
                           teams=all_teams_list, 
                           campeonatos=campeonatos_list,
                           campeoes_atuais=campeoes_atuais)

@app.route('/campeao_geral')
def campeao_geral():
    conn = get_db()
    campeao_data = conn.execute(
        "SELECT * FROM campeao_palpiteiros WHERE temporada = ?", 
        (TEMPORADA_ATUAL,)
    ).fetchone()
    
    campeao = None
    if campeao_data:
        campeao = dict(campeao_data)
        total_jogos = campeao['acertos'] + campeao['erros']
        campeao['percentual_acertos'] = round((campeao['acertos'] / total_jogos) * 100, 1) if total_jogos > 0 else 0
    
    return render_template('campeao_geral.html', 
                          campeao=campeao, 
                          temporada_atual=TEMPORADA_ATUAL)

@app.route('/admin/manage_games', methods=['GET', 'POST'])
@login_required
def manage_games():
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
        
        conn.execute('''
            INSERT INTO anuncios (titulo, mensagem, tipo, data_criacao) 
            VALUES (?, ?, ?, ?)
        ''', (titulo, mensagem, tipo, data_criacao))
        
        conn.commit()
        flash('Anúncio adicionado com sucesso!', 'success')
        return redirect(url_for('gerenciar_anuncios'))
    
    anuncios = conn.execute('SELECT * FROM anuncios ORDER BY data_criacao DESC').fetchall()
    return render_template('gerenciar_anuncios.html', anuncios=anuncios)

@app.route('/admin/anuncios/delete/<int:anuncio_id>', methods=['POST'])
@login_required
def deletar_anuncio(anuncio_id):
    conn = get_db()
    conn.execute('DELETE FROM anuncios WHERE id = ?', (anuncio_id,))
    conn.commit()
    flash('Anúncio apagado com sucesso!', 'success')
    return redirect(url_for('gerenciar_anuncios'))

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
        
        flash('Temporada reiniciada com sucesso! Pontos zerados e jogos antigos removidos.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao reiniciar temporada: {e}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

# Rotas removidas/simplificadas (comentadas para referência):
# - /rodadas (estava incompleta)
# - /rodada/<int:numero> (redundante com outras rotas)
# - Funções duplicadas

# if __name__ == '__main__':
#     app.run(debug=True, host="0.0.0.0", port=5000)