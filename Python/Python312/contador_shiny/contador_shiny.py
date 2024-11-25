import tkinter as tk
from tkinter import PhotoImage

# Pontuação dos atendentes
Growlithe = 0
Pidgey = 0
Stantler = 0


def atualizar_pontuacao(atendente):
    global Growlithe, Pidgey, Stantler

    if atendente == "Growlithe":
        Growlithe += 1
    elif atendente == "Pidgey":
        Pidgey += 1
    elif atendente == "Stantler":
        Stantler += 1

    label_arthur.config(text=f"Growlithe: {Growlithe}")
    label_carlos.config(text=f"Pidgey: {Pidgey}")
    label_joao.config(text=f"Stantler: {Stantler}")


janela = tk.Tk()
janela.title("Contagem Pokemon")
janela.geometry("400x400")
janela.configure(bg="#f0f0f0")
janela.iconbitmap('icone.ico')

# Carregar as imagens (substitua os caminhos pelos arquivos corretos)
growlithe_img = PhotoImage(file="growlithe.png")
pidgey_img = PhotoImage(file="pidgey.png")
stantler_img = PhotoImage(file="stantler.png")

frame = tk.Frame(janela, bg="#f0f0f0")
frame.pack(pady=20)

titulo = tk.Label(frame, text="Contagem Pokemon Shiny", font=("Helvetica", 18, "bold"), bg="#f0f0f0")
titulo.grid(row=0, column=0, columnspan=2, pady=10)

# Adicionar botões com imagens dos Pokémons
botao_arthur = tk.Button(frame, text="Growlithe", width=15, height=2, bg="#4CAF50", fg="white",
                         font=("Helvetica", 12, "bold"), command=lambda: atualizar_pontuacao("Growlithe"))
botao_arthur.grid(row=1, column=0, padx=10, pady=5)

# Label com imagem e pontuação para Growlithe
label_arthur = tk.Label(frame, text=f"Growlithe: {Growlithe}", font=("Helvetica", 12), bg="#f0f0f0", image=growlithe_img, compound="left")
label_arthur.grid(row=1, column=1)

botao_carlos = tk.Button(frame, text="Pidgey", width=15, height=2, bg="#4CAF50", fg="white",
                         font=("Helvetica", 12, "bold"), command=lambda: atualizar_pontuacao("Pidgey"))
botao_carlos.grid(row=2, column=0, padx=10, pady=5)

# Label com imagem e pontuação para Pidgey
label_carlos = tk.Label(frame, text=f"Pidgey: {Pidgey}", font=("Helvetica", 12), bg="#f0f0f0", image=pidgey_img, compound="left")
label_carlos.grid(row=2, column=1)

botao_joao = tk.Button(frame, text="Stantler", width=15, height=2, bg="#4CAF50", fg="white",
                       font=("Helvetica", 12, "bold"), command=lambda: atualizar_pontuacao("Stantler"))
botao_joao.grid(row=3, column=0, padx=10, pady=5)

# Label com imagem e pontuação para Stantler
label_joao = tk.Label(frame, text=f"Stantler: {Stantler}", font=("Helvetica", 12), bg="#f0f0f0", image=stantler_img, compound="left")
label_joao.grid(row=3, column=1)

janela.mainloop()
