from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_migrate import Migrate


db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "hellasdo jspa ojdioashdiOAHWUUHFUSA ND OAISHD UWHETUDSH89WY3Q89WYQ389WURHworld"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_NAME
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024    # 50 Mb limit

    db.init_app(app)
    migrate = Migrate(app,db)


    from .views import views
    #from .models import User,adminAccount



    with app.app_context():
        db.create_all()


    app.register_blueprint(views, url_prefix="/")


    return app




