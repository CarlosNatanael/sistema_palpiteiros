import random

while True:
    sup_list = ["Lucas","Mateus","Arthur"]
    sort = random.choice(sup_list)
    print(sort)

    cont = input("S/N: ")
    if cont.lower() == "s":
        continue
    elif cont.lower() == "n":
        print(".")
        break
    else:
        print("")
    
                 
