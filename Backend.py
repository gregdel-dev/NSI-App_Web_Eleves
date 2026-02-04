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
with open(path.join(BASE_DIR,"base_de_donnees", "creer_tables.sql"), "r", encoding="utf-8") as f:
    sql_creation = f.read()
with open(path.join(BASE_DIR,"base_de_donnees", "supprimer_tables.sql"), "r", encoding="utf-8") as f:
    sql_suppression = f.read() 

#initialisation de la base de données
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.executescript(sql_creation)
conn.commit()
conn.close()

#fonctions pour l'execution d'actions sur la base de données
def edit_sql(commande, argument=()):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute(commande, argument)
    except sqlite3.IntegrityError:
        conn.close()
        return False
    conn.commit()
    conn.close()
    return 

def execute_sql(commande, argument=()):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(commande, argument)
    valeurs = c.fetchall()
    conn.commit()
    conn.close()
    return valeurs


#colonnes
colonnes_eleve=({"titre" : "Prénom", "id":"Prenom", "type" : "text", "order": 1},{"titre" : "Nom", "id":"Nom", "type" : "text", "order": 2},{"titre" : "Date de Naissance", "id":"Date_de_Naissance", "type" : "date", "order": 3})
colonnes_prof=({"titre" : "Nom", "id":"Nom", "type" : "text", "order": 1},{"titre" : "Prénom", "id":"Prenom", "type" : "text", "order": 2})


#routes :

@app.route('/')
def home():
    return render_template('index.html', infos={'element' : None})


@app.route('/eleve/liste', methods=["POST","GET"])
def liste():
    if request.method=="POST":

        if request.form.get("type")=="tri":
            critere=request.form.get("tri")
            return render_template('liste.html', valeurs=execute_sql(f"SELECT * FROM Eleve ORDER BY {critere}"), colonnes=colonnes_eleve, infos= {"element" : "élève","URL_ajout": "/eleve/ajout", "titre": "Ajouter des élèves", "ajout_boutton": "Ajouter des élèves", "URL_actuelle": "/eleve/liste" })
        
        if request.form.get("type")=="supprimer":
            id=request.form["id"]
            edit_sql("DELETE FROM Eleve WHERE id = ?", (str(id),))

        
    if request.args.get("type")=="recherche":
        chaine=request.args.get("recherche")
        return render_template('liste.html', valeurs=execute_sql("SELECT * FROM Eleve WHERE Prenom LIKE ? OR Nom LIKE ?", (f"%{chaine}%", f"%{chaine}%")), colonnes=colonnes_eleve, infos= {"element" : "élève","URL_ajout": "/eleve/ajout", "titre": "Ajouter des élèves", "ajout_boutton": "Ajouter des élèves" }, recherche=chaine)
    
    return render_template('liste.html', valeurs=execute_sql("SELECT * FROM Eleve"), colonnes=colonnes_eleve, infos= {"element" : "élève","URL_ajout": "/eleve/ajout", "titre": "Ajouter des élèves", "ajout_boutton": "Ajouter des élèves","URL_update": "/eleve/update" })


@app.route('/eleve/update', methods=["POST","GET"])
def update():

    id = request.args.get('id')
    if id is None:
        return "Aucun ID fourni", 400
    
    if request.method=="POST":
        prenom=request.form["Prenom"]
        nom=request.form["Nom"]
        Date_de_Naissance=request.form["Date_de_Naissance"]
        edit_sql("UPDATE Eleve SET Prenom = ?, Nom = ?, Date_de_Naissance = ? WHERE Id = ?", (prenom, nom, Date_de_Naissance, id))
        return redirect("/eleve/liste")
    
    return render_template('update.html', valeurs=execute_sql("SELECT * FROM Eleve WHERE id = ?", (str(id),)), colonnes=colonnes_eleve, infos={"element": "élève"})


@app.route('/eleve/ajout', methods=["POST","GET"])
def ajout():
    if request.method=="POST":
        prenom=request.form["Prenom"]
        nom=request.form["Nom"]
        Date_de_Naissance=request.form["Date_de_Naissance"]
        edit_sql("INSERT INTO Eleve (Prenom, Nom, Date_de_Naissance) VALUES (?, ?, ?)", (prenom, nom, Date_de_Naissance))

    return render_template('ajout.html', colonnes=colonnes_eleve, infos= {"element" : "élève","URL_liste": "/eleve/liste", "titre": "Ajouter des élèves", })


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='imDate_de_Naissance/vnd.microsoft.icon'
    )


@app.route('/prof/ajout', methods=["POST","GET"])
def ajout_prof():
    if request.method=="POST":
        prenom=request.form["Prenom"]
        nom=request.form["Nom"]
        edit_sql("INSERT INTO Professeur(Nom, Prenom) VALUES (?,?)",(nom, prenom))

    return render_template('ajout.html', colonnes=colonnes_prof, infos= {"element" : "professeur","URL_liste": "/prof/liste", "titre": "Ajouter des professeurs", })

@app.route('/prof/liste', methods=["POST","GET"])
def liste_prof():
    if request.method=="POST":

        if request.form.get("type")=="tri":
            critere=request.form.get("tri")
            if critere not in ['Nom', 'Prenom', 'Date_de_Naissance']:
                return "Critère de tri invalide", 400
            return render_template('liste.html', valeurs=execute_sql(f"SELECT * FROM Professeur ORDER BY {critere}", ()), colonnes=colonnes_prof, infos={"element" : "professeur","URL_ajout": "/prof/ajout", "titre": "Ajouter des Professeurs", "ajout_boutton": "Ajouter des Professeurs", "URL_actuelle": "/prof/liste" })
        
        if request.form.get("type")=="supprimer":
            id=request.form["id"]
            edit_sql("DELETE FROM Eleve WHERE id=?", (str(id),))
  
    if request.args.get("type")=="recherche":
        chaine=request.args.get("recherche")
        
        return render_template('liste.html', valeurs=execute_sql("SELECT * FROM Professeur WHERE Nom LIKE ? OR Prenom LIKE ?",(f"%{chaine}%", f"%{chaine}%")), colonnes=colonnes_prof, infos= {"element" : "professeur","URL_ajout": "/prof/ajout", "titre": "Ajouter des Professeurs", "ajout_boutton": "Ajouter des Professeurs" }, recherche=chaine)
    return render_template('liste.html', valeurs=execute_sql("SELECT * FROM Professeur", ()), colonnes=colonnes_prof, infos= {"element" : "professeur","URL_ajout": "/prof/ajout", "titre": "Ajouter des Professeurs", "ajout_boutton": "Ajouter des Professeurs","URL_update": "/prof/update" })

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
