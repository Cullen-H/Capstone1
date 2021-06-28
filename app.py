import os
import secrets

from flask import Flask, Blueprint
from routes import routes
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from models import db, connect_db

app = Flask(__name__)
app.register_blueprint(routes, url_prefix="")

db_uri = os.environ.get('DATABASE_URL')
print("+++++++++++++++++++++++++++++++")
print(db_uri)
print("+++++++++++++++++++++++++++++++")

if db_uri:
    db_uri.replace("postgres://", "postgresql://", 1)
    print("==================================")
    print(db_uri)
    print("==================================")
else:
    db_uri = 'postgresql:///food-recommender'

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = secrets.token_hex(20)

connect_db(app)
