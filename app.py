from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__,template_folder="pages")

# Création de la base si elle n'existe pas
def init_db():
    conn = sqlite3.connect("eleves.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS eleves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prenom TEXT,
            nom TEXT,
            age INTEGER
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = sqlite3.connect("eleves.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM eleves")
    eleves = cur.fetchall()
    conn.close()
    return render_template("index.html", eleves=eleves)

@app.route("/ajout", methods=["GET", "POST"])
def ajout():
    if request.method == "POST":
        prenom = request.form["prenom"]
        nom = request.form["nom"]
        age = request.form["age"]

        conn = sqlite3.connect("eleves.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO eleves (prenom, nom, age) VALUES (?, ?, ?)",
                    (prenom, nom, age))
        conn.commit()
        conn.close()

        return redirect(url_for("index"))
    return render_template("ajout.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
