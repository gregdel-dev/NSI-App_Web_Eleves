import sqlite3
from flask import Flask,render_template, send_from_directory, request
from os import path
app=Flask(__name__)
DB_NAME = 'eleves.sqlite'
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute("""
        CREATE TABLE IF NOT EXISTS eleves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prenom TEXT NOT NULL,
            nom TEXT NOT NULL,
            age INTEGER NOT NULL
        )""")
conn.commit()
conn.close()

def creer_eleve(prenom, nom, age):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    

    try:
        c.execute("INSERT INTO eleves (prenom, nom, age) VALUES (?, ?, ?)", (prenom, nom, age))
    except sqlite3.IntegrityError:
        conn.close()
        return False
    conn.commit()
    conn.close()
    return 

def lire_eleves():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM eleves")
    eleves = c.fetchall()
    conn.commit()
    conn.close()
    
    return eleves

def lire_eleve(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM eleves WHERE id = ?", (str(id)))
    eleve = c.fetchone()
    conn.commit()
    conn.close()
    
    return eleve

def supprimer_eleve(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM eleves WHERE id = ?", (str(id)))
    conn.commit()
    conn.close()
    return 

def modifier(id, prenom, nom, age):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE eleves SET prenom = ?, nom = ?, age = ? WHERE id = ?", (prenom, nom, age, id))
    if c.rowcount == 0:
        c.execute("INSERT INTO eleves (id, prenom, nom, age) VALUES (?, ?, ?, ?)", (id, prenom, nom, age))
    conn.commit()
    conn.close()
    return 

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

#série de tests
###
    import time
    supprimer_eleve(1)
    time.sleep(2)
    supprimer_eleve(2)
    time.sleep(2)
    creer_eleve(1,"prenom1","nom1",11)
    creer_eleve(2,"prenom2","nom2",12)
    time.sleep(2)
    print(lire_eleves())
    print(lire_eleve(1))
    time.sleep(2)
    update(1,"prenome1","nome1",122)
    time.sleep(2)
    print(lire_eleves())
    time.sleep(2)
    print(recherche_nom("nome"))
    print(lire_eleve_tri("nom"))
    print(lire_eleve_filtre_age(10,12))
###




@app.route('/', methods=["POST","GET"])
def home():
    if request.method=="POST":
        if request.form.get("type")=="supprimer":
            id=request.form["id"]
            supprimer_eleve(id)
        elif request.form.get("type")=="number":
            return render_template('index.html', eleves=lire_eleve_tri('age'))
    return render_template('index.html', eleves=lire_eleves())
@app.route('/update', methods=["POST","GET"])
def update():
    id = request.args.get('id')
    if id is None:
        return "Aucun ID fourni", 400
    if request.method=="POST":
        prenom=request.form["prenom"]
        nom=request.form["nom"]
        age=request.form["age"]
        modifier(id,prenom,nom,age)
    return render_template('update.html', eleve=lire_eleve(id))

@app.route('/ajout', methods=["POST","GET"])
def ajout():
    if request.method=="POST":
        prenom=request.form["prenom"]
        nom=request.form["nom"]
        age=request.form["age"]
        creer_eleve(prenom,nom,age)
    return render_template('ajout.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

if __name__=="__main__":
    app.run()