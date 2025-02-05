from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cbc57430ab3776309a656ca0c6db92eb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

from flaskblog import routes # import is here to prevent circular imports


# Code to create database in cmd
    # from project import app, db
    # app.app_context().push()
    # db.create_all()
