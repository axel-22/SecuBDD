####################################################################################
#                                                                                  #
#                  ENSIBS TP : Sécurisation des bases de données                   #
#                                    Client TD2                                    #
####################################################################################

import requests
from phe import paillier
import pickle
from pyope.ope import OPE, ValueRange

SERVER = input("IP serveur (ex: http://127.0.0.1:5000): ")

KEY_FILE = "keys.pkl"

def load_keys():
    with open(KEY_FILE, "rb") as f:
        return pickle.load(f)

public_key, private_key = load_keys()

# 🔐 clé OPE (à garder côté client uniquement)
OPE_KEY = b"super_secret_ope_key"
cipher_ope = OPE(OPE_KEY, in_range=ValueRange(0, 10_000_000))


def encrypt_salary(s):
    return str(public_key.encrypt(s).ciphertext())


def decrypt_salary(enc):
    return private_key.decrypt(paillier.EncryptedNumber(public_key, int(enc)))


def ore_encrypt(s):
    return cipher_ope.encrypt(s)


def add_employee():
    salaire = int(input("Salaire: "))

    enc = encrypt_salary(salaire)
    ore = ore_encrypt(salaire)

    requests.post(SERVER + "/add", json={
        "enc": enc,
        "ore": ore
    })


def list_employees():
    r = requests.get(SERVER + "/list")
    data = r.json()

    print("\nEmployés :")
    for emp in data:
        id_, enc = emp
        salaire = decrypt_salary(enc)
        print(f"ID {id_} → salaire = {salaire}")


def compare():
    id1 = int(input("ID1: "))
    id2 = int(input("ID2: "))

    r = requests.post(SERVER + "/compare", json={
        "id1": id1,
        "id2": id2
    })

    print("Résultat:", r.json()["result"])


def sum_salaries():
    r = requests.get(SERVER + "/sum")
    enc_sum = int(r.json()["sum"])

    print("Somme chiffrée reçue (démo):", enc_sum)


def menu():
    while True:
        print("\n1. Ajouter")
        print("2. Afficher")
        print("3. Comparer")
        print("4. Somme")
        print("5. Quitter")

        c = input("> ")

        if c == "1":
            add_employee()
        elif c == "2":
            list_employees()
        elif c == "3":
            compare()
        elif c == "4":
            sum_salaries()
        else:
            break

if __name__ == "__main__":
    menu()