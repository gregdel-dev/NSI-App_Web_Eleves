from livereload import Server
from Backend import app

if __name__ == "__main__":
    server = Server(app.wsgi_app)
    server.watch('templates/**/*.html', delay=0.1, ignore=lambda p: False)
    server.watch('static/**/*.css', delay=0.1, ignore=lambda p: False)
    server.watch('*.py', delay=0.1, ignore=lambda p: False)
    server.serve(debug=True, port=5000, liveport=35729)

