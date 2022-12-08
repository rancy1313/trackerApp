from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET KEY'] = 'iudsdbciud ccdoi'
    # tells flask where our sql database is located
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    # initialize database by giving it the app
    db.init_app(app)

    from .features import features
    from .authorization import authorization

    app.register_blueprint(features, url_prefix='/')
    app.register_blueprint(authorization, url_prefix='/')
    # its empty in the decorator if it had something it would be /auth/hello
    #app.register_blueprint(auth, url_prefix='/auth/hello')
    # we need to import to make sure it defines the databases before you create them
    from .models import User

    # this is new code stack overflow
    # db was not created in same directory take note
    with app.app_context():
        db.create_all()

    # where does flask redirect us if user is not logged and login is not required
    login_manager = LoginManager()
    login_manager.login_view = 'authorization.login'
    login_manager.init_app(app)

    # load user(TRY REMOVING THIS PART TO SEE IF IT GETS RID OF BUG WHEN YOU RESTART SESSION AND IT SHOWS BLANK SCREEN)
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

