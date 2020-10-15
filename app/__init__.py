from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder="../hanlearn-react/build", static_url_path="/")

    app.config.from_object(config['dev'])

    db.init_app(app)

    from .main import main
    app.register_blueprint(main)

    from .auth import auth
    app.register_blueprint(auth)
    
    return app