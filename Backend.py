from flask import Flask,render_template, send_from_directory, request
from os import path
app=Flask(__name__)
#Adam: C'est la base temporaire, t'y touche pas. Et au passage dépèche toi
base_temporaire = [(1,"prenom1","nom1", 17)]
@app.route('/')
def home():
    return render_template('index.html', eleves=base_temporaire)
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