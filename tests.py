import os
import json
from unittest import TestCase
from models import db, connect_db, User, Like, Dislike
os.environ['DATABASE_URL'] = 'postgres:///food-recommender-test'
from app import app
from routes import CURR_USER_KEY
db.create_all()
app.config['WTF_CSRF_ENABLED'] = False

class AppTestCase(TestCase):
    """Tests for the application."""

    def setUp(self):
        """Create test client and sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.register(username="testuser",
                                      email="testuser@test.com",
                                      password="password123")

        db.session.commit()

        self.food_api_id = '1003464'

    def test_homepage(self):
        """Ensures the homepage is displayed."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.get('/')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<div id="home-container">', html)

    def test_user_profile(self):
        """Tests user page."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            res = c.get(f'/user/{self.testuser.username}')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>Your Profile</h1>', html)

    def test_display_food(self):
        """Tests display food page."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.get(f'/foods/{self.food_api_id}')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1 id="food-name">Blueberry Rhubarb Pie</h1>', html)

    def test_new_mealplan(self):
        """Tests new mealplan page."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.get('/foods/new_mealplan')
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>Create a Meal Plan</h1>', html)

    def test_like_dislike_toggle(self):
        """Ensures likes and dislikes are toggled properly."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.post(f'/foods/like/{self.food_api_id}')
            self.assertEqual(res.status_code, 200)
            liked_post = Like.query.filter_by(food_api_id=self.food_api_id, user_id=self.testuser.id).first()
            self.assertEqual(liked_post.food_api_id, int(self.food_api_id))
            self.assertEqual(liked_post.user_id, self.testuser.id)
            res = c.post(f'/foods/dislike/{self.food_api_id}')
            liked_post = Like.query.filter_by(food_api_id=self.food_api_id, user_id=self.testuser.id).first()
            disliked_post = Dislike.query.filter_by(food_api_id=self.food_api_id, user_id=self.testuser.id).first()
            self.assertFalse(bool(liked_post))
            self.assertEqual(disliked_post.food_api_id, int(self.food_api_id))
            self.assertEqual(disliked_post.user_id, self.testuser.id)

    def test_get_food(self):
        """Ensures a food is received."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.get('/api/get_food?diet=None&exclude=')
            self.assertEqual(res.status_code, 200)
    
    def test_gen_mealplan(self):
        """Tests mealplan creation."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            res = c.post('/api/mealplans/gen_mealplan', data=json.dumps({
                    "diet": None,
                    "exclude": [],
                    "days": "5",
                    "meals": ["breakfast", "lunch", "dinner"]
                }),content_type='application/json')
            self.assertEqual(res.status_code, 200)
            loaded=json.loads(res.data)
            self.assertEqual(len(loaded["generatedMP"]["mealplan"]["days"]), 5)
    
    def test_update_prefs(self):
        """Tests update user preferences."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.post('/api/update_prefs', data=json.dumps({
                "diet": "Vegetarian",
                "exclude": []
            }), content_type='application/json')
            user = User.query.get(self.testuser.id)
            self.assertEqual(res.status_code, 200)
            loaded = json.loads(user.preferences)
            self.assertEqual(loaded["diet"], "Vegetarian");

    def test_register_user(self):
        """Tests user registration page."""

        with self.client as c:

            res = c.get('/register')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>Register</h1>', html)

    def test_login_user(self):
        """Tests user login page."""

        with self.client as c:

            res = c.get('/login')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>Login</h1>', html)
    
    def test_logout(self):
        """Tests user logout."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.get('/logout', follow_redirects=True)
            self.assertEqual(res.status_code, 200)
