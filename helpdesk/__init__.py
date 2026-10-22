from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFError, CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import Engine
from .models import db

csrf = CSRFProtect()


@event.listens_for(Engine, "connect")
def sqlite_settings(connection, _):
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA busy_timeout=15000")
    cursor.close()


def create_app(test_config=None):
    app = Flask(__name__)
    if test_config is None:
        from .config import configuration
        app.config.from_mapping(configuration())
    else:
        app.config.from_mapping(test_config)
    db.init_app(app)
    Migrate(app, db)
    csrf.init_app(app)
    from .routes import bp, load_user
    app.register_blueprint(bp)
    app.before_request(load_user)
    from .cli import register_commands
    register_commands(app)

    @app.after_request
    def headers(response):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; script-src 'none'; "
            "img-src 'self' data:; font-src 'self'; frame-ancestors 'none'; "
            "form-action 'self'; base-uri 'self'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["X-Frame-Options"] = "DENY"
        if request.endpoint != "static":
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(CSRFError)
    def csrf_error(_):
        return render_template("error.html", code=400, message="O formulário expirou ou não pôde ser validado. Atualize a página e tente novamente."), 400

    for code, message in {
        403: "Seu perfil não tem permissão para acessar esta página.",
        404: "Não encontramos esta página ou este chamado.",
        413: "Os dados enviados excedem o tamanho permitido. Reduza o conteúdo e tente novamente.",
        500: "Não foi possível concluir a operação. Tente novamente em instantes.",
    }.items():
        def handler(_, code=code, message=message):
            if code == 500:
                db.session.rollback()
            return render_template("error.html", code=code, message=message), code
        app.register_error_handler(code, handler)
    return app
