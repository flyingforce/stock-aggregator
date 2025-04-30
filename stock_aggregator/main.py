from flask import Flask
from .config import Config
from .app.routes import init_routes

app = Flask(__name__)
app.config.from_object(Config)

# Initialize routes
init_routes(app)

# Custom filter for formatting dollar amounts
@app.template_filter('formatDollar')
def format_dollar(value):
    if value is None:
        return '$0.00'
    return '${:,.2f}'.format(float(value))

if __name__ == '__main__':
    app.run(debug=True) 