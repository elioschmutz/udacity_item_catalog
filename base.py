from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.cfg')
    return app

app = create_app()
