####################################################################################
#                                                                                  #
#                  ENSIBS TP : Sécurisation des bases de données                   #
#                                      Server TD2                                  #
####################################################################################

import sys
import requests
import json
import os
import pickle
from pyope.ope import OPE
from phe import paillier

# cle pour la comparaison
OPE_KEY =  os.urandom(32)
with open("ope_key.bin", "wb") as f:
    f.write(OPE_KEY)

cipher_ope = OPE(OPE_KEY)

# Clés Paillier save dans un fichier paillier_keys.bin
PAILLIER_KEY = 'paillier_keys.bin'

def load_or_generate_paillier_keys():
    if os.path.exists(PAILLIER_KEY):
        with open(PAILLIER_KEY, "rb") as f:
            pub_key, priv_key = pickle.load(f)
            return pub_key, priv_key
    else:
        print("Génération d'une nouvelle paire de clés")
        pub_key, priv_key = paillier.generate_paillier_keypair()

        with open(PAILLIER_KEY, "wb") as f:
            pickle.dump((pub_key, priv_key), f)

        return pub_key, priv_key

PUBLIC_KEY, PRIVATE_KEY = load_or_generate_paillier_keys()

def print_menu():
    print("\n" + "-"*40)
    print("1. Ajouter un employé")
    print("2. Afficher la base (Vue Attaquant)")
    print("3. Comparer deux salaires")
    print("4. Obtenir la somme de tous les salaires")
    print("5. Quitter")
    print("-"*40)

def main():
    if len(sys.argv) != 3:
        print("Pas les bon args")
        sys.exit(1)
        
    base_url = f"http://{sys.argv[1]}:{sys.argv[2]}"
    # print(f"Connecté au serveur {base_url} avec succès.")

    while True:
        print_menu()
        choix = input("Votre choix : ")

        if choix == '1':
            emp_id = input("Nom de l'employé (ex: Alice) : ")
            try:
                salary = int(input("Salaire (en clair) : "))
            except ValueError:
                print("Erreur: Le salaire doit être un entier.")
                continue

            # CHIFFREMENT TRANSPARENT
            salary_ope = cipher_ope.encrypt(salary)
            salary_paillier = PUBLIC_KEY.encrypt(salary)
            print("Salaire en clair (non envoyé) : ",salary)
            payload = {
                "emp_id": emp_id,
                "salary_ope": salary_ope,
                "salary_paillier": str(salary_paillier.ciphertext())
            }
            print("Payload envoyé au serveur : ", payload)
            
            r = requests.post(f"{base_url}/add", json=payload)
            if r.status_code == 200:
                print("Employé ajouté dans la base")
            else:
                print(f"Erreur : {r.json().get('message')}")

        elif choix == '2':
            r = requests.get(f"{base_url}/all")
            if r.status_code == 200:
                data = r.json()
                print("\nAffichage de la base - ce que voit un attaquant sur la machine")
                print("DATA = \n", data)
            else:
                print("Erreur lors de la récupération.")

        elif choix == '3':
            id1 = input("Nom de l'employé 1 : ")
            id2 = input("Nom  de l'employé 2 : ")
            r = requests.get(f"{base_url}/compare", params={"id1": id1, "id2": id2})
            if r.status_code == 200:
                print(f"\n[Réponse du serveur] -> {r.json()['result']}")
            else:
                print(f"-> Erreur : {r.json().get('message')}")

        elif choix == '4':
            # On envoie la partie publique `n` pour que le serveur fasse le calcul
            payload = {"pub_key_n": str(PUBLIC_KEY.n)}
            print("\nDemande au serveur de faire la somme des salaires chiffrés...")
            r = requests.post(f"{base_url}/sum", json=payload)
            
            if r.status_code == 200:
                data = r.json()
                if data['sum_ciphertext'] == "0":
                    print("-> La base est vide.")
                else:
                    # DÉCHIFFREMENT TRANSPARENT
                    enc_sum = paillier.EncryptedNumber(PUBLIC_KEY, int(data['sum_ciphertext']))
                    dec_sum = PRIVATE_KEY.decrypt(enc_sum)
                    print(f"Somme totale des salaires : {dec_sum}")
            else:
                print("Erreur serveur.")

        elif choix == '5':
            break
        else:
            print("Choix non valide")

if __name__ == '__main__':
    main()