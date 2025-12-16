import sqlite3
from flask import Flask,render_template, send_from_directory, request, Response, redirect
from os import path
from io import BytesIO
from json import dumps


#creation de l'app flask
app=Flask(__name__)

#récupèration du chemin d'accès de la base de données
BASE_DIR = path.dirname(path.abspath(__file__))
DB_NAME = path.join(BASE_DIR,"base_de_donnees", "Base_de_donnees.sqlite")

#on enregistre le contenu des fichiers .sql dans des variables
with open("base_de_donnees/creer_tables.sql", "r", encoding="utf-8") as f:
    sql_creation = f.read()
with open("base_de_donnees/supprimer_tables.sql", "r", encoding="utf-8") as f:
    sql_suppression = f.read() 

#initialisation de la base de données
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.executescript(sql_creation)
conn.commit()
conn.close()

#fonctions de gestion de la base de donnée : 
def creer_eleve(prenom, nom, Date_de_Naissance):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO Eleve (Prenom, Nom, Date_de_Naissance) VALUES (?, ?, ?)", (prenom, nom, Date_de_Naissance))
    except sqlite3.IntegrityError:
        conn.close()
        return False
    conn.commit()
    conn.close()
    return 

def lire_eleves():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM Eleve")
    eleves = c.fetchall()
    conn.commit()
    conn.close()
    return eleves

def lire_eleve(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM Eleve WHERE id = ?", (str(id),))
    eleve = c.fetchone()
    conn.commit()
    conn.close()
    return eleve

def supprimer_eleve(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM Eleve WHERE id = ?", (str(id),))
    conn.commit()
    conn.close()
    return 

def modifier(id, prenom, nom, Date_de_Naissance):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE Eleve SET Prenom = ?, Nom = ?, Date_de_Naissance = ? WHERE Id = ?", (prenom, nom, Date_de_Naissance, id))
    if c.rowcount == 0:
        c.execute("INSERT INTO Eleve (Id, Prenom, Nom, Date_de_Naissance) VALUES (?, ?, ?, ?)", (id, prenom, nom, Date_de_Naissance))
    conn.commit()
    conn.close()
    return 

def recherche_nom(chaine):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM Eleve WHERE Prenom LIKE ? OR Nom LIKE ?", (f"%{chaine}%", f"%{chaine}%"))
    resultats = c.fetchall()
    conn.commit()
    conn.close()
    return resultats

def lire_eleve_tri(argument):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if argument not in ["Prenom", "Nom", "Date_de_Naissance"]:
        conn.close()
        return []
    c.execute(f"SELECT * FROM Eleve ORDER BY {argument}")
    eleves = c.fetchall()
    conn.commit()
    conn.close()
    return eleves

def lire_eleve_filtre_Date_de_Naissance(debut, fin):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM Eleve WHERE Date_de_Naissance BETWEEN ? AND ?", (debut, fin))
    eleves = c.fetchall()
    conn.commit()
    conn.close()
    return eleves

colonnes_eleve=({"titre" : "Prénom", "id":"Prenom", "type" : "text", "order": 1},{"titre" : "Nom", "id":"Nom", "type" : "text", "order": 2},{"titre" : "Date de Naissance", "id":"Date_de_Naissance", "type" : "date", "order": 3})



#routes :

@app.route('/')
def home():
    return render_template('index.html')




@app.route('/eleve/liste', methods=["POST","GET"])
def liste():
    if request.method=="POST":

        if request.form.get("type")=="tri":
            critere=request.form.get("tri")
            return render_template('liste.html', valeurs=lire_eleve_tri(critere), colonnes=colonnes_eleve, infos= {"URL_ajout": "/eleve/ajout", "titre": "Ajouter des élèves", "ajout_boutton": "Ajouter des élèves", "URL_actuelle": "/eleve/liste" })
        
        if request.form.get("type")=="supprimer":
            id=request.form["id"]
            supprimer_eleve(id)

        if request.form.get("type")=="filtre":
            debut=request.form["debut"]
            fin=request.form["fin"]
            return render_template('liste.html', valeurs=lire_eleve_filtre_Date_de_Naissance(debut, fin), colonnes=colonnes_eleve,infos= {"URL_ajout": "/eleve/ajout", "titre": "Ajouter des élèves", "ajout_boutton": "Ajouter des élèves" })
        
    if request.args.get("type")=="recherche":
        chaine=request.args.get("recherche")
        return render_template('liste.html', valeurs=recherche_nom(chaine), colonnes=colonnes_eleve, infos= {"URL_ajout": "/eleve/ajout", "titre": "Ajouter des élèves", "ajout_boutton": "Ajouter des élèves" }, recherche=chaine)
    
    return render_template('liste.html', valeurs=lire_eleves(), colonnes=colonnes_eleve, infos= {"URL_ajout": "/eleve/ajout", "titre": "Ajouter des élèves", "ajout_boutton": "Ajouter des élèves" })



@app.route('/eleve/update', methods=["POST","GET"])
def update():

    id = request.args.get('id')
    if id is None:
        return "Aucun ID fourni", 400
    
    if request.method=="POST":
        prenom=request.form["prenom"]
        nom=request.form["nom"]
        Date_de_Naissance=request.form["Date_de_Naissance"]
        modifier(id,prenom,nom,Date_de_Naissance)
        return redirect("/liste")
    
    return render_template('update.html', valeurs=lire_eleve(id), colonnes=colonnes_eleve)



@app.route('/eleve/ajout', methods=["POST","GET"])
def ajout():
    if request.method=="POST":
        prenom=request.form["Prenom"]
        nom=request.form["Nom"]
        Date_de_Naissance=request.form["Date_de_Naissance"]
        creer_eleve(prenom,nom,Date_de_Naissance)

    return render_template('ajout.html', colonnes=colonnes_eleve, infos= {"URL_liste": "/eleve/liste", "titre": "Ajouter des élèves", })

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='imDate_de_Naissance/vnd.microsoft.icon'
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
            "Date_de_Naissance": eleve[3]
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
