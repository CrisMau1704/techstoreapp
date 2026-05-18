from flask import Flask, redirect
from flask_appbuilder import AppBuilder, expose
from flask_sqlalchemy import SQLAlchemy
from flask_appbuilder.security.views import AuthDBView

db = SQLAlchemy()
appbuilder = AppBuilder()


def create_app() -> Flask:

    app = Flask(__name__)

    app.config.from_object("config")

    # =========================
    # INICIALIZAR DB
    # =========================

    db.init_app(app)

    with app.app_context():

        # IMPORTAR MODELOS
        from .models import (
            Paciente,
            Doctor,
            Tratamiento,
            Cita,
            Pago
        )

        # CREAR TABLAS
        db.create_all()

        print("✅ Base de datos MySQL inicializada correctamente")

        # =========================
        # INICIALIZAR APPBUILDER
        # =========================

        appbuilder.init_app(app, db.session)

        # IMPORTAR VIEWS
        from . import views

        # =========================
        # LOGIN PERSONALIZADO
        # =========================

        class CustomAuthDBView(AuthDBView):

            @expose('/login/', methods=['GET', 'POST'])
            def login(self):

                from flask import flash
                from flask_appbuilder.security.forms import LoginForm_db
                from flask_login import login_user

                form = LoginForm_db()

                if form.validate_on_submit():

                    user = appbuilder.sm.auth_user_db(
                        form.username.data,
                        form.password.data
                    )

                    if user:

                        login_user(
                            user,
                            remember=False
                        )

                        # REDIRECCIÓN AL DASHBOARD
                        return redirect('/dashboard')

                    else:

                        flash(
                            'Usuario o contraseña incorrectos',
                            'warning'
                        )

                return self.render_template(
                    'appbuilder/general/security/login_db.html',
                    form=form
                )

        # =========================
        # REEMPLAZAR LOGIN ORIGINAL
        # =========================

        appbuilder.sm.authdbview = CustomAuthDBView

        # =========================
        # DASHBOARD COMO HOME
        # =========================

        appbuilder.indexview = views.DashboardView()

        # =========================
        # RUTA PRINCIPAL
        # =========================

       

        # =========================
        # LOGOUT
        # =========================

        app.config['LOGOUT_REDIRECT_URL'] = '/login'

    return app

