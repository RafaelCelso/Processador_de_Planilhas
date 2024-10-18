import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

from app import app

# Remova esta linha
# app = app.wsgi_app

if __name__ == '__main__':
    app.run(debug=True)
