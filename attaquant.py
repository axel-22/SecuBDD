####################################################################################
#                                                                                  #
#                  ENSIBS TP : Sécurisation des bases de données                   #
#                                   Attaquant TD2                                  #
####################################################################################

import requests
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import pickle
from phe import paillier

SERVER = "http://127.0.0.1:5000"

# modèle public
MEAN = 3000
STD = 800

# 🔐 clé pour déchiffrer (simulation évaluation)
with open("paillier_keys.bin", "rb") as f:
    PUBLIC_KEY, PRIVATE_KEY = pickle.load(f)


def attack():
    r = requests.get(SERVER + "/all")
    data = r.json()

    employees = [(emp[0], int(emp[1]), emp[2]) for emp in data]

    # tri par OPE
    employees_sorted = sorted(employees, key=lambda x: x[1])

    n = len(employees_sorted)

    real = []
    estimated = []

    for i, (emp_id, ope, enc) in enumerate(employees_sorted):

        # vrai salaire
        enc_obj = paillier.EncryptedNumber(PUBLIC_KEY, int(enc))
        real_salary = PRIVATE_KEY.decrypt(enc_obj)

        # estimation
        percentile = (i + 0.5) / n
        est_salary = stats.norm.ppf(percentile, loc=MEAN, scale=STD)

        real.append(real_salary)
        estimated.append(est_salary)

    return real, estimated


def plot(real, estimated):
    x = range(len(real))

    plt.figure(figsize=(12,6))
    plt.plot(x, real, label="Salaire réel")
    plt.plot(x, estimated, label="Salaire estimé (attaque)")

    plt.title("Attaque statistique sur OPE")
    plt.xlabel("Employés triés")
    plt.ylabel("Salaire (€)")
    plt.legend()
    plt.grid()

    plt.show()


def error(real, estimated):
    errors = [abs(r - e) for r, e in zip(real, estimated)]
    avg_error = sum(errors) / len(errors)

    print(f"\nErreur moyenne : {int(avg_error)} €")

    # pourcentage
    avg_real = sum(real) / len(real)
    percent = (avg_error / avg_real) * 100

    print(f"Erreur relative : {percent:.2f} %")


if __name__ == "__main__":
    real, estimated = attack()
    error(real, estimated)
    plot(real, estimated)