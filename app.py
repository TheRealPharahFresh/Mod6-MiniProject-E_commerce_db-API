from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Initialize extensions 
db = SQLAlchemy()
ma = Marshmallow()

def create_app(): 
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:Godswill150@127.0.0.1/e_commerce_db"

    # Initialize for app
    db.init_app(app)
    ma.init_app(app)

    # Import and register routes
    with app.app_context():
        from routes import init_routes
        db.create_all()
        init_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)