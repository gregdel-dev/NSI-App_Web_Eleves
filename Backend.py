from flask import Flask, send_from_directory
from os import path
app=Flask(__name__)
@app.route('/')
def home():
    return "Bienvenue sur votre première application Flask !"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

if __name__=="__main__":
    app.run(debug=True)