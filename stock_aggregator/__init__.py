"""Stock Portfolio Aggregator package."""
from flask import Flask
from stock_aggregator.config import Config

app = Flask(__name__)
app.config.from_object(Config)

from stock_aggregator.main import app as main_app
app = main_app

from stock_aggregator.cli import cli
