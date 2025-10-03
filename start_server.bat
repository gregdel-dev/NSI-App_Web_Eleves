@echo off

while true; do
    echo "Lancement de app.py..."
    python app.py
    echo "app.py s'est arrêté avec le code $?. Relance dans 2 secondes..."
    sleep 2
done
