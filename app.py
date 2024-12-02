from flask import Flask
from extensions import db, ma  # Import shared db and ma instances


def create_app():
    # Create Flask app instance
    app = Flask(__name__)

    # Configure the app
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:Godswill150@127.0.0.1/e_commerce_db1"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)

    # Register routes
    with app.app_context():
        from routes import init_routes  # Import route initialization function
        init_routes(app)  # Initialize routes

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from models import *
        db.create_all()  # Create database tables
    app.run(debug=True)
