from flask import Flask,render_template, send_from_directory, request
from os import path
app=Flask(__name__)

#Adam tu devra remplir ces fonctions 
def creer_eleve(id,prenom,nom,age):
    return

def lire_eleves():
    return #renvoie les élèves

def lire_eleve(id):
    return #renvoie un tuple avec les données de l'élève demandé (par son id)

def supprimer_eleve(id):
    return 

def update(id, prenom, nom ,age):
    #si possible tu modifie les données de l'élève (selon son id) sinnon juste tu le supprime et tu le recréé
    return

def recherche_nom(chaine):
    return #renvoie les élèves dont le nom ou prenom correspnd ou contient la chaine de caractères

def lire_eleve_tri(argument): #argument contient soit "prenom" soit "nom" soit "age"
    return #renvoie les élèves triés selon l'arguement (trié par age, par prenom etc...)
def lire_eleve_filtre_age(debut, fin):
    return #renvoie les élèves selon l'intervale (entre début et fin)




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