from flask import Flask, render_template
import socket

app = Flask(__name__)

@app.route('/')
def manutencao():
    return render_template('manutencao.html')

@app.route('/<path:path>')
def todas_as_rotas(path):
    return render_template('manutencao.html')

if __name__ == '__main__':
    print("\n" + "="*50)
    print("      INICIANDO APLICAÇÃO DE PALPITES")
    print("="*50 + "\n")
    try:
        hostname = socket.gethostname()
        ip_server = socket.gethostbyname(hostname)
    except socket.error as e:
        ip_server = '127.0.0.1' # IP de fallback caso não consiga encontrar
        print(f"[AVISO] Não foi possível obter o IP local: {e}. Usando {ip_server} como fallback.")
    print(f"[LOG - Main]: Servidor de Manutenção Flask rodando. Acesse nos seguintes endereços:")
    print(f"   - Na mesma máquina: http://127.0.0.1:3000")
    print(f"   - Em outros dispositivos na mesma rede: http://{ip_server}:3000")
    print("\nPressione CTRL+C para parar o servidor.")

    app.run(host="0.0.0.0", port=3000, debug=True)