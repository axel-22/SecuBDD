####################################################################################
#                                                                                  #
#                  ENSIBS TP : Sécurisation des bases de données                   #
#                                       TD2                                        #
####################################################################################

import mysql.connector

from flask import Flask, request, jsonify

app = Flask(__name__)

conn = mysql.connector.connect(
    user='axel',
    password='axel',
    host='172.20.10.2',
    database='TP_SecuBDD_Jemai_HoussinVonthron'
)

cursor = conn.cursor()

# Création table
cursor.execute("""
CREATE TABLE IF NOT EXISTS employes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    salaire_enc TEXT,
    salaire_ore BIGINT
)
""")
conn.commit()


@app.route("/add", methods=["POST"])
def add():
    data = request.json
    enc = data["enc"]
    ore = data["ore"]

    cursor.execute(
        "INSERT INTO employes (salaire_enc, salaire_ore) VALUES (%s, %s)",
        (enc, ore)
    )
    conn.commit()

    return jsonify({"status": "ok"})


@app.route("/compare", methods=["POST"])
def compare():
    id1 = request.json["id1"]
    id2 = request.json["id2"]

    cursor.execute("SELECT salaire_ore FROM employes WHERE id=%s", (id1,))
    s1 = cursor.fetchone()[0]

    cursor.execute("SELECT salaire_ore FROM employes WHERE id=%s", (id2,))
    s2 = cursor.fetchone()[0]

    if s1 > s2:
        return jsonify({"result": "id1 > id2"})
    elif s1 < s2:
        return jsonify({"result": "id1 < id2"})
    else:
        return jsonify({"result": "egal"})


@app.route("/sum", methods=["GET"])
def sum_salaries():
    cursor.execute("SELECT salaire_enc FROM employes")

    total = None

    for (enc,) in cursor.fetchall():
        if total is None:
            total = enc
        else:
            total = str(int(total) + int(enc))  # addition homomorphe simulée

    return jsonify({"sum": total})


if __name__ == "__main__":
    print("Serveur lancé sur http://127.0.0.1:5000")
    app.run(port=5000)