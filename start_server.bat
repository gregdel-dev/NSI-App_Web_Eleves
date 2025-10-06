@echo off
start firefox http://127.0.0.1:5000/
:A
echo "Lancement de app.py..."
python run_dev.py
echo "app.py s'est arrêté avec le code $?. Relance dans 2 secondes..."
sleep 2
goto A
