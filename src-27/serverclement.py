# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "flask",
#     "phe",
#     "pyope",
# ]
# ///
import socket
from flask import Flask, request, jsonify
import sqlite3
from phe import paillier

# OPE (salary_ope) = Order Preserving Encryption, valeur du salaire à utiliser pour la comparaison

# Paillier (salary_paillier) = valeur du salaire pour la somme
app = Flask(__name__)

def init_db():
    """Initialise la base de données SQLite."""
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    # On stocke l'OPE sous forme d'entier (pour le >, <) 
    # et le Paillier sous forme de texte (car les nombres sont très grands)
    c.execute('''CREATE TABLE IF NOT EXISTS employees
                 (emp_id TEXT PRIMARY KEY, salary_ope INTEGER, salary_paillier TEXT)''')
    conn.commit()
    conn.close()

@app.route('/add', methods=['POST'])
def add_employee():
    data = request.json
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    try:
        # data: em
        c.execute("INSERT INTO employees (emp_id, salary_ope, salary_paillier) VALUES (?, ?, ?)",
                  (data['emp_id'], data['salary_ope'], str(data['salary_paillier'])))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
   
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Employé déjà existant"}), 400
   
        

# route pour la comparaison des salaires
@app.route('/compare', methods=['GET'])
def compare_salaries():

    # id pour la comparaison
    id1 = request.args.get('id1')
    id2 = request.args.get('id2')
    
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute("SELECT salary_ope FROM employees WHERE emp_id=?", (id1,))
    res1 = c.fetchone()
    print(f"Recupération du salaire de {id1} pour comparaison OPE : {res1[0]}")

    c.execute("SELECT salary_ope FROM employees WHERE emp_id=?", (id2,))
    res2 = c.fetchone()
    print(f"Recupération du salaire de {id2} pour comparaison OPE : {res2[0]}")
    conn.close()

    if not res1 or not res2:
        return jsonify({"status": "error", "message": "ID(s) introuvable(s)"}), 404

    # res1[0] = salaire ope 1
    # res2[0] = salaire ope 2
    ope_val1, ope_val2 = res1[0], res2[0]
    
    if ope_val1 > ope_val2:
        result = f"{id1} gagne strictement plus que {id2}"
    elif ope_val1 < ope_val2:
        result = f"{id2} gagne strictement plus que {id1}"
    else:
        result = f"{id1} et {id2} ont le même salaire"

    return jsonify({"status": "success", "result": result})

# route pour la somme de deux salaires
@app.route('/sum', methods=['POST'])
def sum_salaries():
    """Calcule la somme homomorphe des salaires chiffrés."""
    data = request.json
    

    # recupération de la clé public n, obligatoire pour la somme
    pub_key_n = int(data['pub_key_n'])
    # creation de la clé publique
    pub_key = paillier.PaillierPublicKey(n=pub_key_n)

    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute("SELECT salary_paillier FROM employees")

    # rows = recupération de tous les salaires
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("Server : pas de salaires retournés, peut-être pas une erreur.")
        return jsonify({"status": "..."})

    for row in rows:
        print(f"Server : Salaire chiffré dans la base (Paillier) : {row[0][:15]}...")

    # Reconstitution des objets de chiffrement de la librairie phe
    # recup de tous salaires 
    encrypted_salaries = [paillier.EncryptedNumber(pub_key, int(row[0])) for row in rows]

    encrypted_sum = sum(encrypted_salaries)

    return jsonify({"status": "success", "sum_ciphertext": str(encrypted_sum.ciphertext())})

# recup toute la base et l'afficher.
@app.route('/all', methods=['GET'])
def get_all():
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute("SELECT * FROM employees")
    res = c.fetchall()
    conn.close()
    print("Server : all data = ",res)
    return jsonify(res)

if __name__ == '__main__':
    init_db()
    ip = '127.0.0.1'
    port = 5000
    app.run(host=ip, port=port, debug=False)