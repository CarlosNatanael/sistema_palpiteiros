import random
import time


while True:
    Resp = int(input("Digite o numero de 1 a 5: "))
    numero = random.randint(1,6)

    print(f"O numero sorteado foi {numero}")
    time.sleep(1)

    if numero == Resp:
        print("Você acertou !!")
    else:
        print("Você errou")


    novamente = input("Deseja Continuar? (S/N): ")
    if novamente.lower() == "s":
        continue
    elif novamente.lower() == "n":
        print("Obrigado por participar!")
        break
    else:
        print("Opção invalida")
