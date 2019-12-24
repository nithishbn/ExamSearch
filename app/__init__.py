from flask import Flask
from flask_bootstrap import Bootstrap

from config import Config

app = Flask(__name__, static_folder="static", static_url_path="/static")

app.config.from_object(Config)
bootstrap = Bootstrap(app)
from app import routes
