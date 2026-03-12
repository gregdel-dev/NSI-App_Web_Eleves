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
    c.execute(commande, argument)
    
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

def convert_en_dico(donnes):
    dico={}
    for i in donnes: 
        dico[i[0]]=i
    return dico
def remplacer_elements(element, donnes):
    print(donnes)
    for i in donnes:
        d=donnes.pop(0)
        donnes.append(list(d))
    if element=="Matiere" or element=="Classe":
        profs=convert_en_dico(execute_sql("SELECT * FROM Professeur"))
        for i in donnes:
            i[3]=profs[i[3]][1]+" "+profs[i[3]][2]
    if element=="Eleve":
        classes=convert_en_dico(execute_sql("SELECT * FROM Classe"))
        for i in donnes:
            i[4]=classes[i[4]][1]

    if element=="Inscription":
        eleves=convert_en_dico(execute_sql("SELECT * FROM Eleve"))
        for i in donnes:
            i[1]=eleves[i[1]][2]+" "+ eleves[i[1]][1]
        
        matieres=convert_en_dico(execute_sql("SELECT * FROM Matiere"))
        for i in donnes:
            i[2]=matieres[i[2]][1]
    for i in donnes:
        d=donnes.pop(0)
        donnes.append(tuple(d))
    return donnes

#colonnes
colonnes_eleve=({"titre" : "Prénom", "id":"Prenom", "type" : "text", "order": 1},{"titre" : "Nom", "id":"Nom", "type" : "text", "order": 2},{"titre" : "Date de Naissance", "id":"Date_de_Naissance", "type" : "date", "order": 3})
colonnes_prof=({"titre" : "Nom", "id":"Nom", "type" : "text", "order": 1},{"titre" : "Prénom", "id":"Prenom", "type" : "text", "order": 2})
colonnes_classe=({"titre" : "Nom", "id" : "Nom", "type" : "text", "order" : 1},{"titre" : "Nom Lycée", "id":"Nom_Lycee", "type" : "text", "order": 2}, {"titre" : "Professeur", "id" : "Professeur", "type" : "dropdown", "order" : 3})
colonnes_matiere=({"titre" : "Nom", "id" : "Nom", "type" : "text", "order" : 1},{"titre" : "Nombre d'heures", "id":"Nombre_Heures", "type" : "number", "order": 2}, {"titre" : "Professeur", "id" : "Professeur", "type" : "dropdown", "order" : 3})
colonnes_inscription=({"titre" : "Eleve", "id" : "Id_Eleve", "type" : "dropdown", "order" : 1},{"titre" : "Matière", "id" : "Id_Matiere", "type" : "dropdown", "order" : 2})

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
            edit_sql("DELETE FROM Eleve WHERE Id = ?", (str(id),))

        
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
    
    return render_template('update.html', valeurs=execute_sql("SELECT * FROM Eleve WHERE id = ?", (str(id),))[0], colonnes=colonnes_eleve, infos={"element": "élève","URL_liste": "/eleve/liste"})


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
            edit_sql("DELETE FROM Professeur WHERE Id=?", (str(id),))
    if request.args.get("type")=="recherche":
        chaine=request.args.get("recherche")
        return render_template('liste.html', valeurs=execute_sql("SELECT * FROM Professeur WHERE Nom LIKE ? OR Prenom LIKE ?",(f"%{chaine}%", f"%{chaine}%")), colonnes=colonnes_prof, infos= {"element" : "professeur","URL_ajout": "/prof/ajout", "titre": "Ajouter des Professeurs", "ajout_boutton": "Ajouter des Professeurs" }, recherche=chaine)
    return render_template('liste.html', valeurs=execute_sql("SELECT * FROM Professeur", ()), colonnes=colonnes_prof, infos= {"element" : "professeur","URL_ajout": "/prof/ajout", "titre": "Ajouter des Professeurs", "ajout_boutton": "Ajouter des Professeurs","URL_update": "/prof/update" })

@app.route('/prof/update', methods=["POST","GET"])
def update2():
    id = request.args.get('id')
    if id is None:
        return "Aucun ID fourni", 400
    if request.method=="POST":
        prenom=request.form["Prenom"]
        nom=request.form["Nom"]
        edit_sql("UPDATE Professeur SET Prenom = ?, Nom = ? WHERE Id = ?", (prenom, nom, id))
        return redirect("/prof/liste")
    
    return render_template('update.html', valeurs=execute_sql("SELECT * FROM Professeur WHERE id = ?", (str(id),))[0], colonnes=colonnes_prof, infos={"element": "professeur", "URL_liste": "/prof/liste",})





@app.route('/classe/ajout', methods=["POST","GET"])
def ajout_classe():
    if request.method=="POST":
        nom=request.form["Nom"]
        nom_lycee=request.form["Nom_Lycee"]
        id_prof=request.form["Professeur_valeur"]
        edit_sql("INSERT INTO Classe (Nom, Nom_Lycee,Id_Professeur) VALUES (?,?,?)",(nom, nom_lycee,id_prof))
    return render_template('ajout.html', colonnes=colonnes_classe,dropdown_values={"Professeur" :execute_sql("SELECT * FROM Professeur")}, infos= {"element" : "classe","URL_liste": "/classe/liste", "titre": "Ajouter des classes", })

@app.route('/classe/liste', methods=["POST","GET"])
def liste_classe():
    if request.method=="POST":
        if request.form.get("type")=="tri":
            critere=request.form.get("tri")
            if critere not in ['Nom','Nom_lycee']:
                return "Critère de tri invalide", 400
            return render_template('liste.html', valeurs=remplacer_elements("Classe",execute_sql(f"SELECT * FROM Classe ORDER BY {critere}", ())), colonnes=colonnes_classe, infos={"element" : "classe","URL_ajout": "/matiere/ajout", "ajout_boutton": "Ajouter des classes", "URL_actuelle": "/classe/liste" })
        if request.form.get("type")=="supprimer":
            id=request.form["id"]
            edit_sql("DELETE FROM Classe WHERE Id=?", (str(id),))
    if request.args.get("type")=="recherche":
        chaine=request.args.get("recherche")
        return render_template('liste.html', valeurs=remplacer_elements("Classe",execute_sql("SELECT * FROM Classe WHERE Nom LIKE ?",(f"%{chaine}%",))), colonnes=colonnes_classe, infos= {"element" : "classe","URL_ajout": "/classe/ajout", "ajout_boutton": "Ajouter des classe" }, recherche=chaine)
    return render_template('liste.html', valeurs=remplacer_elements("Classe",execute_sql("SELECT * FROM Classe", ())), colonnes=colonnes_classe, infos= {"element" : "Classe","URL_ajout": "/classe/ajout", "ajout_boutton": "Ajouter des classes","URL_update": "/classe/update" })

@app.route('/classe/update', methods=["POST","GET"])
def update_classe():
    id = request.args.get('id')
    if id is None:
        return "Aucun ID fourni", 400
    if request.method=="POST":
        nom_lycee=request.form["Nom_Lycee"]
        nom=request.form["Nom"]
        id_prof=request.form["Professeur_valeur"]
        edit_sql("UPDATE Classe SET Nom = ?, Nom_lycee = ?, Id_Professeur = ? WHERE Id = ?", ( nom,nom_lycee, id_prof, id))
        return redirect("/classe/liste")
    
    return render_template('update.html', valeurs=execute_sql("SELECT * FROM Classe WHERE Id = ?", (str(id),))[0],dropdown_values={"Professeur" :execute_sql("SELECT * FROM Professeur")}, colonnes=colonnes_classe, infos={"element": "classe","URL_liste": "/classe/liste"})



@app.route('/matiere/liste', methods=["POST","GET"])
def liste_matiere():
    if request.method=="POST":
        if request.form.get("type")=="tri":
            critere=request.form.get("tri")
            if critere not in ['Nom', 'Nombre_Heures']:
                return "Critère de tri invalide", 400
            return render_template('liste.html', valeurs=execute_sql(f"SELECT * FROM Matiere ORDER BY {critere}", ()), colonnes=colonnes_matiere, infos={"element" : "matières","URL_ajout": "/matiere/ajout", "ajout_boutton": "Ajouter des Matières", "URL_actuelle": "/matiere/liste" })
        if request.form.get("type")=="supprimer":
            id=request.form["id"]
            edit_sql("DELETE FROM Matiere WHERE Id=?", (str(id),))
    if request.args.get("type")=="recherche":
        chaine=request.args.get("recherche")
        return render_template('liste.html', valeurs=execute_sql("SELECT * FROM Matiere WHERE Nom LIKE ?",(f"%{chaine}%",)), colonnes=colonnes_matiere, infos= {"element" : "matières","URL_ajout": "/matiere/ajout", "ajout_boutton": "Ajouter des Matières" }, recherche=chaine)
    return render_template('liste.html', valeurs=remplacer_elements("Matiere",execute_sql("SELECT * FROM Matiere", ())), colonnes=colonnes_matiere, infos= {"element" : "matières","URL_ajout": "/matiere/ajout", "ajout_boutton": "Ajouter des Matières","URL_update": "/matiere/update" })

@app.route('/matiere/update', methods=["POST","GET"])
def update_matiere():
    id = request.args.get('id')
    if id is None:
        return "Aucun ID fourni", 400
    if request.method=="POST":
        nb_heures=request.form["Nombre_Heures"]
        nom=request.form["Nom"]
        id_prof=request.form["Professeur_valeur"]
        edit_sql("UPDATE Matiere SET Nombre_Heures = ?, Nom = ?, Id_Professeur = ? WHERE Id = ?", (nb_heures, nom, id_prof, id))
        return redirect("/matiere/liste")
    
    return render_template('update.html', valeurs=execute_sql("SELECT * FROM Matiere WHERE Id = ?", (str(id),))[0],dropdown_values={"Professeur" :execute_sql("SELECT * FROM Professeur")}, colonnes=colonnes_matiere, infos={"element": "matieres","URL_liste": "/matiere/liste"})



@app.route('/matiere/ajout', methods=["POST","GET"])
def ajout_matiere():
    if request.method=="POST":
        nom=request.form["Nom"]
        nb_heures=request.form["Nombre_Heures"]
        id_prof=request.form["Professeur_valeur"]
        print(nom, nb_heures, execute_sql("SELECT * FROM Matiere", ()))
        edit_sql("INSERT INTO Matiere (Nom, Nombre_Heures, Id_Professeur) VALUES (?,?,?)",(nom, nb_heures, id_prof))
    return render_template('ajout.html', colonnes=colonnes_matiere, dropdown_values={"Professeur" :execute_sql("SELECT * FROM Professeur")}, infos= {"element" : "matière","URL_liste": "/matiere/liste", "titre": "Ajouter des matières", })









@app.route('/inscription/liste', methods=["POST","GET"])
def liste_inscription():
    _infos={"element" : "inscriptions","URL_ajout": "/inscription/ajout", "ajout_boutton": "Ajouter des Inscriptions","URL_update": "/inscription/update" }
    if request.method=="POST":
        if request.form.get("type")=="tri":
            critere=request.form.get("tri")
            if critere not in ['Id_Eleve', 'Id_Professeur']:
                return "Critère de tri invalide", 400
            return render_template('liste.html', valeurs=execute_sql(f"SELECT * FROM Inscription ORDER BY {critere}", ()), colonnes=colonnes_inscription, infos=_infos)
        if request.form.get("type")=="supprimer":
            id=request.form["id"]
            edit_sql("DELETE FROM Inscription WHERE Id=?", (str(id),))
    if request.args.get("type")=="recherche":
        chaine=request.args.get("recherche")
        return render_template('liste.html', valeurs=execute_sql("SELECT * FROM Inscription WHERE Nom LIKE ?",(f"%{chaine}%",)), colonnes=colonnes_inscription, infos= _infos, recherche=chaine)
    return render_template('liste.html', valeurs=remplacer_elements("Inscription",execute_sql("SELECT * FROM Inscription", ())), colonnes=colonnes_inscription, infos= _infos)

@app.route('/inscription/update', methods=["POST","GET"])
def update_inscription():
    id = request.args.get('id')
    if id is None:
        return "Aucun ID fourni", 400
    if request.method=="POST":
        id_eleve=request.form["Id_Eleve_valeur"]
        id_matiere=request.form["Id_Matiere_valeur"]
        edit_sql("UPDATE Inscription SET Id_Eleve = ?, Id_Matiere = ? WHERE Id = ?", (id_eleve, id_matiere, id))
        return redirect("/inscription/liste")
    
    return render_template('update.html', valeurs=execute_sql("SELECT * FROM Inscription WHERE Id = ?", (str(id),))[0],dropdown_values={"Id_Eleve" :execute_sql("SELECT * FROM Eleve"),"Id_Matiere" :execute_sql("SELECT * FROM Matiere")}, colonnes=colonnes_inscription, infos={"element": "inscriptions","URL_liste": "/inscription/liste"})



@app.route('/inscription/ajout', methods=["POST","GET"])
def ajout_inscription():
    if request.method=="POST":
        id_eleve=request.form["Id_Eleve_valeur"]
        id_matiere=request.form["Id_Matiere_valeur"]
        edit_sql("INSERT INTO Inscription (Id_Eleve, Id_Matiere) VALUES (?,?)",(id_eleve, id_matiere))
    return render_template('ajout.html', colonnes=colonnes_inscription, dropdown_values={"Id_Eleve" :execute_sql("SELECT * FROM Eleve"),"Id_Matiere" :execute_sql("SELECT * FROM Matiere")}, infos= {"element" : "inscriptions","URL_liste": "/inscription/liste", "titre": "Ajouter des inscription", })


if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)