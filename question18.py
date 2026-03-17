import mysql.connector



data_to_insert = [
    ('Fluffy', 'Harold', 'chat', 'f', '2013-02-04', None),
    ('Claws', 'Gwen', 'chat', 'm', '2014-03-17', None),
    ('Buffy', 'Harod', 'chien', 'f', '2019-05-13', None),
    ('Fang', 'Benny', 'chien', 'm', '2010-08-27', None),
    ('Bowser', 'Diane', 'chien', 'm', '2018-08-31', '2021-07-29'),
    ('Chirpy', 'Gwen', 'oiseau', 'f', '2018-09-11', None),
    ('Whistler', 'Gwen', 'oiseau', None, '2017-12-09', None),
    ('Slim', 'Benny', 'serpent', 'm', '2016-04-29', None),
    ('Puffball', 'Diane', 'hamster', 'f', '2019-03-30', None)
]

try:
    conn = mysql.connector.connect(
        user='clement',
        password='clement',
        host='127.0.0.1',
        database='TP_SecuBDD_Jemai_HoussinVonthron'
    )
    cursor = conn.cursor()

    sql = "INSERT INTO animaux (nom, proprietaire, espece, genre, naissance, mort) VALUES (%s, %s, %s, %s, %s, %s)"

    cursor.executemany(sql, data_to_insert)
    conn.commit()
    print(f"{cursor.rowcount} lignes insérées.")

    conn.close()

except mysql.connector.Error as err:
    print(f"Erreur: {err}")