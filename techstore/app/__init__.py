from flask import Flask
import config
from .extensions import appbuilder, db

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    # 🔸 Se crea el contexto antes de inicializar AppBuilder
    with app.app_context():
        appbuilder.init_app(app, db.session)

        # 🔹 Importar vistas y modelos para que se registren
        from . import views, models

    return app

from .extensions import appbuilder , db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    
    db.init_app(app)
    with app.app_context():
        from .models import Paciente
        db.create_all()
        appbuilder.init_app(app, db.session)
        from . import views
        
    return app
