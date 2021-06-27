from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

import json

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """User model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    preferences = db.Column(JSON, nullable=False)

    meal_plans = db.relationship('MealPlan', )
    likes = db.relationship('Like')
    dislikes = db.relationship('Dislike')
    recommend_blacklists = db.relationship('RecommendBlacklist')

    @classmethod
    def register(cls, username, email, password):
        """Registers a user.
            Hashes password and adds it to the database.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
                username=username,
                email=email,
                password=hashed_pwd,
                preferences=json.dumps({'diet': 'None', 'exclude': []}),
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Searches the user model for a user with matching username and password.
            returns user if authentication passes and false if it fails.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False

class MealPlan(db.Model):
    """Meal plan model."""

    __tablename__ = "meal_plans"

    id = db.Column(db.Integer, primary_key=True)
    plan = db.Column(JSON, nullable=False)
    grocery_list = db.Column(JSON, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

class Like(db.Model):
    """Model for liked foods."""

    __tablename__ = "likes"
    
    id = db.Column(db.Integer, primary_key=True)
    food_api_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

class Dislike(db.Model):
    """Model for disliked foods."""

    __tableneame__ = "dislikes"

    id = db.Column(db.Integer, primary_key=True)
    food_api_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

class RecommendBlacklist(db.Model):
    """Model for recommendation blacklisting."""

    __tablename__ = "recommend_blacklists"

    id = db.Column(db.Integer, primary_key=True)
    expire_date = db.Column(db.DateTime, nullable=False)
    food_api_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

def connect_db(app):
    """Connects this database to the Flask application."""

    db.app = app
    db.init_app(app)
