from flask import Flask

from controllers.game_controller import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app


app = create_app()

if __name__ == "__main__":
    # debug=True apenas para desenvolvimento local.
    app.run(debug=True)
