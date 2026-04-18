# Archivo puente para Render
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Importa y ejecuta el verdadero main
from ia_app import main as ia_main
from ia_app import app as ia_app

# Render busca 'app' o 'main' como punto de entrada
app = ia_app
main = ia_main

if __name__ == "__main__":
    ia_main()
