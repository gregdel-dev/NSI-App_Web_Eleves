import sqlite3
from flask import Flask,render_template, send_from_directory, request
from os import path
app=Flask(__name__)

DB_NAME = 'eleves.sqlite'
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute("""
        CREATE TABLE IF NOT EXISTS eleves (
            id INTEGER PRIMARY KEY,
            prenom TEXT NOT NULL,
            nom TEXT NOT NULL,
            age INTEGER NOT NULL
        )""")
conn.commit()
conn.close()

def creer_eleve(id, prenom, nom, age):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    

    try:
        c.execute("INSERT INTO eleves (id, prenom, nom, age) VALUES (?, ?, ?, ?)", (id, prenom, nom, age))
    except sqlite3.IntegrityError:
        conn.close()
        return False
    conn.commit()
    conn.close()
    return True

def lire_eleves():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM eleves")
    conn.commit()
    conn.close()
    eleves = c.fetchall()
    return eleves

def lire_eleve(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM eleves WHERE id = ?", (id))
    conn.commit()
    conn.close()
    eleve = c.fetchone()
    return eleve

def supprimer_eleve(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM eleves WHERE id = ?", (id))
    conn.commit()
    conn.close()
    return True

def update(id, prenom, nom, age):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE eleves SET prenom = ?, nom = ?, age = ? WHERE id = ?", (prenom, nom, age, id))
    if c.rowcount == 0:
        c.execute("INSERT INTO eleves (id, prenom, nom, age) VALUES (?, ?, ?, ?)", (id, prenom, nom, age))
    conn.commit()
    conn.close()
    return True

def recherche_nom(chaine):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM eleves WHERE prenom LIKE ? OR nom LIKE ?", (f"%{chaine}%", f"%{chaine}%"))
    resultats = c.fetchall()
    conn.commit()
    conn.close()
    return resultats

def lire_eleve_tri(argument):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if argument not in ["prenom", "nom", "age"]:
        conn.close()
        return []
    c.execute(f"SELECT * FROM eleves ORDER BY {argument}")
    eleves = c.fetchall()
    conn.commit()
    conn.close()
    return eleves

def lire_eleve_filtre_age(debut, fin):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM eleves WHERE age BETWEEN ? AND ?", (debut, fin))
    eleves = c.fetchall()
    conn.commit()
    conn.close()
    return eleves





#Adam: C'est la base temporaire, t'y touche pas. Et au passage dépèche toi
base_temporaire = [(1,"prenom1","nom1", 17)]
@app.route('/')
def home():
    return render_template('index.html', eleves=base_temporaire)
@app.route('/update', methods=["POST","GET"])
def update():
    id = request.args.get('id')
    if id is None:
        return "Aucun ID fourni", 400
    id = int(id)
    current = None
    for i in base_temporaire:
        if i[0] == id:
            current = i
            break
    if current is None:
        return "Élève non trouvé", 404
    if request.method=="POST":
        plusgrand=base_temporaire[0][0]
        for i in base_temporaire:
            if i[0]>plusgrand:
                plusgrand=i[0]
        id=plusgrand+1
        prenom=request.form["prenom"]
        nom=request.form["nom"]
        age=request.form["age"]
        base_temporaire.append((id,prenom,nom,age))
    return render_template('update.html', eleve=current)

@app.route('/ajout', methods=["POST","GET"])
def ajout():
    if request.method=="POST":
        plusgrand=base_temporaire[0][0]
        for i in base_temporaire:
            if i[0]>plusgrand:
                plusgrand=i[0]
        id=plusgrand+1
        prenom=request.form["prenom"]
        nom=request.form["nom"]
        age=request.form["age"]
        base_temporaire.append((id,prenom,nom,age))
        print(base_temporaire)
    return render_template('ajout.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

if __name__=="__main__":
    app.run(debug=True)