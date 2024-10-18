from flask import Flask
import os
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, 
            static_url_path='/static', 
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static'),
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}")
    return "Internal Server Error", 500

from app import routes




