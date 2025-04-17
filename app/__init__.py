"""Stock Portfolio Aggregator app package."""
from flask import Flask
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)

from .main import app as main_app
app = main_app

from .cli import cli
