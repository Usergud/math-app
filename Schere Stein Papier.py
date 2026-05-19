import random

while True:
    computor=random.choice(["schere","stein","papier"])
    guess=input("Schere,Stein,Papier:").lower()
    if guess=="q":
        break
    elif guess==computor:
        print("Unentschieden")
    elif (guess=="papier" and computor=="stein") or \
         (guess=="stein" and computor=="schere") or \
         (guess=="schere" and computor=="papier"):
            print("Gewonnen")
    else:
        print("Verloren")
    print("Ich hatte",computor,"GG")