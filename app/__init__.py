from flask import Flask
import os

app = Flask(__name__, 
            static_url_path='/static', 
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static'),
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

from app import routes




