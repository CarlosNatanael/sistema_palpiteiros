from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def manutencao():
    return render_template('manutencao.html')

@app.route('/<path:path>')
def todas_as_rotas(path):
    return render_template('manutencao.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)