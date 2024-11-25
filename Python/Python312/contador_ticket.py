# pyinstaller --noconsole --name="" --icon="icone.ico" --add-data="icone.ico;." --onefile  .\contador_ticket.py

import tkinter as tk

# Pontuação dos atendentes
Arthur = 0
Carlos = 0
Celso = 0
Joao = 0
Lucas = 0

# Função para atualizar pontuação
def atualizar_pontuacao(atendente):
    global Arthur, Carlos, Celso, Joao, Lucas

    if atendente == "Arthur":
        Arthur += 1
    elif atendente == "Carlos":
        Carlos += 1
    elif atendente == "João":
        Joao += 1
    elif atendente == "Celso":
        Celso += 1
    elif atendente == "Lucas":
        Lucas += 1
    
    # Atualizar labels com a nova pontuação
    label_arthur.config(text=f"Arthur: {Arthur}")
    label_carlos.config(text=f"Carlos: {Carlos}")
    label_joao.config(text=f"João: {Joao}")
    label_mateus.config(text=f"Celso: {Celso}")
    label_lucas.config(text=f"Lucas: {Lucas}")

# Criando a janela principal
janela = tk.Tk()
janela.title("Pontuação de Tickets")
janela.geometry("400x400")
janela.iconbitmap('ticket.ico')
janela.configure(bg="#f0f0f0")  # Cor de fundo da janela

# Criando um frame para centralizar os elementos
frame = tk.Frame(janela, bg="#f0f0f0")
frame.pack(pady=20)

# Título
titulo = tk.Label(frame, text="Pontuação de Tickets", font=("Helvetica", 18, "bold"), bg="#f0f0f0")
titulo.grid(row=0, column=0, columnspan=2, pady=10)

# Criando os botões e labels para a pontuação
botao_arthur = tk.Button(frame, text="Arthur", width=15, height=2, bg="#4CAF50", fg="white",
                         font=("Helvetica", 12, "bold"), command=lambda: atualizar_pontuacao("Arthur"))
botao_arthur.grid(row=1, column=0, padx=10, pady=5)

label_arthur = tk.Label(frame, text=f"Arthur: {Arthur}", font=("Helvetica", 12), bg="#f0f0f0")
label_arthur.grid(row=1, column=1)

botao_carlos = tk.Button(frame, text="Carlos", width=15, height=2, bg="#4CAF50", fg="white",
                         font=("Helvetica", 12, "bold"), command=lambda: atualizar_pontuacao("Carlos"))
botao_carlos.grid(row=2, column=0, padx=10, pady=5)

label_carlos = tk.Label(frame, text=f"Carlos: {Carlos}", font=("Helvetica", 12), bg="#f0f0f0")
label_carlos.grid(row=2, column=1)

botao_joao = tk.Button(frame, text="João", width=15, height=2, bg="#4CAF50", fg="white",
                       font=("Helvetica", 12, "bold"), command=lambda: atualizar_pontuacao("João"))
botao_joao.grid(row=4, column=0, padx=10, pady=5)

label_joao = tk.Label(frame, text=f"João: {Joao}", font=("Helvetica", 12), bg="#f0f0f0")
label_joao.grid(row=4, column=1)

botao_mateus = tk.Button(frame, text="Celso", width=15, height=2, bg="#4CAF50", fg="white",
                         font=("Helvetica", 12, "bold"), command=lambda: atualizar_pontuacao("Celso"))
botao_mateus.grid(row=3, column=0, padx=10, pady=5)

label_mateus = tk.Label(frame, text=f"Celso: {Celso}", font=("Helvetica", 12), bg="#f0f0f0")
label_mateus.grid(row=3, column=1)

botao_lucas = tk.Button(frame, text="Lucas", width=15, height=2, bg="#4CAF50", fg="white",
                        font=("Helvetica", 12, "bold"), command=lambda: atualizar_pontuacao("Lucas"))
botao_lucas.grid(row=5, column=0, padx=10, pady=5)

label_lucas = tk.Label(frame, text=f"Lucas: {Lucas}", font=("Helvetica", 12), bg="#f0f0f0")
label_lucas.grid(row=5, column=1)

# Iniciando o loop principal
janela.mainloop()
