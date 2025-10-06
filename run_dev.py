from livereload import Server
from Backend import app
import os

if __name__ == "__main__":
    
    server = Server(app.wsgi_app)
    server.watch('*.py')          
    server.watch('pages/*.html')  
    server.serve(debug=True, port=5000)
