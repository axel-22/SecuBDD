####################################################################################
#                                                                                  #
#                  ENSIBS TP : Sécurisation des bases de données                   #
#                                    Insert TD2                                    #
####################################################################################

import requests
import numpy as np
import os
import pickle
from pyope.ope import OPE, ValueRange
from phe import paillier

SERVER = "http://127.0.0.1:5000"

# 📊 Distribution réaliste
MEAN = 3000
STD = 800
N = 1000

# 🔐 Chargement clés Paillier
with open("paillier_keys.bin", "rb") as f:
    PUBLIC_KEY, PRIVATE_KEY = pickle.load(f)

# 🔐 Clé OPE persistée
OPE_KEY_FILE = "ope_key.bin"

def load_ope_key():
    if os.path.exists(OPE_KEY_FILE):
        with open(OPE_KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = os.urandom(32)
        with open(OPE_KEY_FILE, "wb") as f:
            f.write(key)
        return key

OPE_KEY = load_ope_key()
cipher_ope = OPE(OPE_KEY, in_range=ValueRange(0, 20000))


def populate():
    print("Génération des salaires...")

    salaries = np.random.normal(MEAN, STD, N)

    # éviter valeurs négatives
    salaries = [max(1000, int(s)) for s in salaries]

    for i, salary in enumerate(salaries):
        emp_id = f"user_{i}"

        payload = {
            "emp_id": emp_id,
            "salary_ope": cipher_ope.encrypt(salary),
            "salary_paillier": str(PUBLIC_KEY.encrypt(salary).ciphertext())
        }

        requests.post(SERVER + "/add", json=payload)

    print("Base remplie avec 1000 employés")


if __name__ == "__main__":
    populate()