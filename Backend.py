import sqlite3
from flask import Flask,render_template, send_from_directory, request, Response, redirect
from os import path
from io import BytesIO
from json import dumps



app=Flask(__name__)
BASE_DIR = path.dirname(path.abspath(__file__))
DB_NAME = path.join(BASE_DIR, "eleves.sqlite")

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
    c.execute("SELECT * FROM eleves WHERE id = ?", (str(id),))
    eleve = c.fetchone()
    conn.commit()
    conn.close()
    return eleve

def supprimer_eleve(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM eleves WHERE id = ?", (str(id),))
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


@app.route('/')
def home():
    return render_template('index.html')




@app.route('/liste', methods=["POST","GET"])
def liste():
    if request.method=="POST":

        if request.form.get("type")=="tri":
            critere=request.form.get("tri")
            return render_template('liste.html', eleves=lire_eleve_tri(critere))
        
        if request.form.get("type")=="supprimer":
            id=request.form["id"]
            supprimer_eleve(id)

        if request.form.get("type")=="filtre":
            debut=request.form["debut"]
            fin=request.form["fin"]
            return render_template('liste.html', eleves=lire_eleve_filtre_age(debut, fin))
        
    if request.args.get("type")=="recherche":
        chaine=request.args.get("recherche")
        return render_template('liste.html', eleves=recherche_nom(chaine))
    
    return render_template('liste.html', eleves=lire_eleves())



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
        return redirect("/liste")
    
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



@app.route('/export')
def export_json():
    data = []
    eleves=lire_eleves()
    for eleve in eleves:
        data.append({
            "id": eleve[0],
            "prenom": eleve[1],
            "nom": eleve[2],
            "age": eleve[3]
        })
    json_data = dumps(data, indent=4, ensure_ascii=False)
    response = Response(
        BytesIO(json_data.encode('utf-8')),
        mimetype="application/json"
    )
    response.headers["Content-Disposition"] = "attachment; filename=eleves.json"
    return response





if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
