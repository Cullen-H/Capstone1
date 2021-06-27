import requests
import json
import math

from datetime import datetime, timedelta
from collections import Counter
from random import randint

from flask import Blueprint, jsonify, render_template, request, flash, redirect, session, g
from forms import RegisterForm, LoginForm
from models import db, connect_db, User, MealPlan, Like, Dislike, RecommendBlacklist
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import func

try:
    from apikeys import KeyRing
except:
    pass

routes = Blueprint("routes", __name__, static_folder="static", template_folder="templates")

CURR_USER_KEY = "curr_user"

# api-key for testing
keys = KeyRing()

@routes.before_request
def add_user_to_g():
    """If user is currently logged in, adds curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Logs a user in."""

    session[CURR_USER_KEY] = user.id

def do_logout(user):
    """Logs a user out."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def add_ingredient_vals(ingredients):
    """Takes an array of ingredients and adds the amount together into a new dict."""
    
    ingredients_total = {}

    for ingredient in ingredients:
        ingredients_total[f"{ingredient['name']}"] = {}
        ingredients_total[f"{ingredient['name']}"]["amount"] = ingredient["amount"]
        ingredients_total[f"{ingredient['name']}"]["unit"] = ingredient["unit"]
    
    return ingredients_total

def add_food_to_blacklist(food_api_id, user_id):
    """Adds a food to the black recommendation blacklist. Sets a time for when that cooldown expires(10 days)."""
    
    blacklistItem = RecommendBlacklist(
            expire_date = datetime.utcnow() + timedelta(days=10),
            food_api_id = food_api_id,
            user_id = user_id,
            )

    db.session.add(blacklistItem)
    db.session.commit()

def get_filtered_recommendation(base_request_url, user_id):
    """This returns a food recommendation that is filtered based on user likes, dislikes, and blacklist.
    
    This function will not reroll until it finds a recipe that is neither blacklisted nor disliked to avoid 
    exceeding the API request limit.
    """
    
    if randint(1, 100) <= 100 and user_id: #change to 10
        user=User.query.get_or_404(user_id)
        preferences = json.loads(user.preferences)
        liked_recipes = Like.query.filter_by(user_id=user_id)
        likes_count = Like.query.filter_by(user_id=user_id).count()
        if likes_count > 0:
            index = randint(0, likes_count-1)
            liked_recipes = [l for l in liked_recipes]
            liked_recipe = requests.get(f"https://api.spoonacular.com/recipes/{liked_recipes[index].id}/information?apiKey={keys.SPOON_KEY}")
            liked_recipe = json.loads(liked_recipe.content)
            if not liked_recipe["diets"]:
                liked_recipe["diets"] = {}
            if preferences["diet"] in liked_recipe["diets"]:
                blacklist = Blacklist.query.filter_by(user_id=user_id, food_api_id=liked_recipes[index].food_api_id).first()
                if blacklist and blacklist.expire_date < datetime.utcnow():
                    add_food_to_blacklist(liked_recipe.food_api_id, user.id).first()
                    resp = requests.get(f"https://api.spoonacular.com/recipes/{liked_recipe.food_api_id}/information/apiKey={keys.SPOON_KEY}")
                    return json.loads(resp.content)
    resp = requests.get(f"{base_request_url}")
    resp_data = json.loads(resp.content)
    
    if user_id and Dislike.query.filter_by(food_api_id=resp_data["results"][0]["id"], user_id=user_id).first():
        resp = requests.get(f"{base_request_url}")
        resp_data = json.loads(resp.content)

    if user_id:
        add_food_to_blacklist(resp_data["results"][0]["id"], user_id)
    return json.loads(resp.content)

# homepage

@routes.route("/", methods=["GET"])
def homepage():
    """Checks if a user is logged in and displays homepage."""

    if g.user:
        user = User.query.get_or_404(g.user.id)
    else:
        user = None
    return render_template("home.html", user=user)

# User routes

@routes.route("/user/<username>")
def user_profile(username):
    """Displays user page to the logged in user.
    If user is unauthorized, flashes error and redirects to home.
    """
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    elif g.user.username != username:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.filter(User.username == username).first()
    return render_template("users/profile.html", user=user)

# Food routes

@routes.route("/foods/<int:food_api_id>")
def display_food(food_api_id):
    """Displays a foods information to the user."""

    resp = requests.get(f"https://api.spoonacular.com/recipes/{food_api_id}/information?apiKey={keys.SPOON_KEY}")
    food = json.loads(resp.content)
    if g.user:
        user = User.query.get_or_404(g.user.id)
    else:
        user = None
    
    return render_template("/foods/display_info.html", food=food, user=user)

@routes.route("/foods/new_mealplan")
def new_mealplan():
    """Displays a form to the user allowing them to create a new mealplan and save it to their profile."""

    if g.user:
        user=User.query.get_or_404(g.user.id)
        return render_template("/foods/create_plan.html", user=user)
    flash("Unauthorized", "danger")
    return redirect("/")


@routes.route("/foods/like/<int:food_api_id>", methods=["POST"])
def like_toggle(food_api_id):
    """Adds a food to a given users liked list.
    Can also remove a food in the event of a dislike or an unlike.
    """
    
    if g.user:
        outputJSON = {"liked": False, "disliked": False}
        user=User.query.get_or_404(g.user.id)
        like=Like.query.filter_by(food_api_id=food_api_id, user_id=user.id).first()
        dislike=Dislike.query.filter_by(food_api_id=food_api_id, user_id=user.id).first()
        if like:
            db.session.delete(like)
        else:
            like = Like(food_api_id=food_api_id, user_id=user.id)
            outputJSON["liked"] = True
            db.session.add(like)
        if dislike:
            db.session.delete(dislike)
        db.session.commit()
        return jsonify(outputJSON)
    else:
        flash("Unauthorized", "danger")
        return redirect("/")

@routes.route("/foods/dislike/<int:food_api_id>", methods=["POST"])
def dislike_toggle(food_api_id):
    """Adds a food to a given users disliked list.
    Can also remove a food in the event of a like or a user toggling off the dislike option.
    """

    if g.user:
        outputJSON = {"liked": False, "disliked": False}
        user=User.query.get_or_404(g.user.id)
        like=Like.query.filter_by(food_api_id=food_api_id, user_id=user.id).first()
        dislike=Dislike.query.filter_by(food_api_id=food_api_id, user_id=user.id).first()
        if dislike:
            db.session.delete(dislike)
        else:
            dislike = Dislike(food_api_id=food_api_id, user_id=user.id)
            outputJSON["disliked"] = True
            db.session.add(dislike)
        if like:
            db.session.delete(like)
        print(outputJSON)
        db.session.commit()
        return jsonify(outputJSON)
    else:
        flash("Unauthorized", "danger")
        return redirect("/")

@routes.route("/foods/checkrating/<int:food_api_id>")
def checkrating(food_api_id):
    """Checks if a food is liked or disliked and returns status to the user."""

    if g.user:
        outputJSON = {}
        user=User.query.get_or_404(g.user.id)
        outputJSON["liked"] = True if Like.query.filter_by(food_api_id=food_api_id, user_id=user.id).first() else False
        outputJSON["disliked"] = True if Dislike.query.filter_by(food_api_id=food_api_id, user_id=user.id).first() else False
        return jsonify(outputJSON)
    else:
        flash("Unauthorized", "danger")
        return redirect("/")


# API routes

@routes.route("/api/get_food", methods=["GET"])
def get_food():
    """Retrieves a food, given a users preferences, and returns it to the user."""

    data = {"diet": request.args["diet"], "exclude": request.args["exclude"]}
    # resp = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={keys.SPOON_KEY}&excludeIngredients={data['exclude']}&diet={data['diet']}&sort=random&number=1")
    if g.user:
        resp = get_filtered_recommendation(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={keys.SPOON_KEY}&excludeIngredients={data['exclude']}&diet={data['diet']}&sort=random&number=1", g.user.id)
    else:
        resp = get_filtered_recommendation(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={keys.SPOON_KEY}&excludeIngredients={data['exclude']}&diet={data['diet']}&sort=random&number=1", None)
    return jsonify(resp)

@routes.route("/api/mealplans/gen_mealplan", methods=["POST"])
def gen_mealplan():
    """Creates a new mealplan and using the provided user agruments"""
    
    data = request.json
    user_mealplan = {"days": []}
    user_grocery = {"weeks": []}
    
    if ("breakfast" in data["meals"]):
        breakfast_resp = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={keys.SPOON_KEY}&excludeIngredients={data['exclude']}&diet={data['diet']}&sort=random&number={data['days']}&type=breakfast&fillIngredients=true")
        breakfast_resp = json.loads(breakfast_resp.content)
    if ("lunch" in data["meals"]):
        lunch_resp = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={keys.SPOON_KEY}&excludeIngredients={data['exclude']}&diet={data['diet']}&sort=random&number={data['days']}&type=main course&fillIngredients=true")
        lunch_resp = json.loads(lunch_resp.content)
    if ("dinner" in data["meals"]):
        dinner_resp = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={keys.SPOON_KEY}&excludeIngredients={data['exclude']}&diet={data['diet']}&sort=random&number={data['days']}&type=main course&fillIngredients=true")
        dinner_resp = json.loads(dinner_resp.content)
    
    for i in range(0, int(data["days"])):
        new_day = []
        if "breakfast" in data["meals"]:
            new_day.append({ "breakfast": breakfast_resp["results"][i] })
        if "lunch" in data["meals"]:
            new_day.append({ "lunch": lunch_resp["results"][i] })
        if "dinner" in data["meals"]:
            new_day.append({ "dinner": dinner_resp["results"][i] })
        user_mealplan["days"].append(new_day)
    
    for i in range(0, math.ceil(int(data["days"])/7)):
        accum_list = []
        for x in range(i*7, (i*7)+7):
            if x >= int(data["days"]):
                break
            if "breakfast" in data["meals"]:
                accum_list += (user_mealplan["days"][x][0]["breakfast"]["missedIngredients"])
            if "lunch" in data["meals"]:
                accum_list += (user_mealplan["days"][x][1]["lunch"]["missedIngredients"])
            if "dinner" in data["meals"]:
                accum_list += (user_mealplan["days"][x][2]["dinner"]["missedIngredients"])
        user_grocery["weeks"].append(add_ingredient_vals(accum_list))

    return jsonify(generatedMP={"mealplan": user_mealplan, "grocerylist": user_grocery})

@routes.route("/api/mealplans/save_mealplan", methods=["POST"])
def save_mealplan():
    """Saves a newly generated mealplan to the server database."""
    
    if g.user:
        data = request.json
        curr_mealplan = Mealplan.query.filter_by(user_id=g.user.id).first()
        if curr_mealplan:
            db.session.delete(curr_mealplan)
        mealplan = MealPlan(
                plan = data["mealplan"],
                grocery_list = data["grocerylist"],
                user_id = g.user.id
                )
        db.session.add(mealplan)
        db.session.commit()
        
        return jsonify(data)

    return jsonify({"mealplan": None, "grocerylist": None})

@routes.route("/api/mealplans/get_mealplan/<int:user_id>")
def get_mealplan(user_id):
    """Retrieves a users mealplan and returns it to them in JSON format."""

    if g.user and g.user.id == user_id:
        mealplan=MealPlan.query.filter_by(user_id=user_id).first()
        mealplan = mealplan
        if mealplan:
            return jsonify(mealplan=mealplan["plan"], grocerylist=mealplan["grocery_list"])
        return jsonify(mealplan={}, grocerylist={})
    else:
        flash("Unauthorized", "danger")
        return redirect("/")

@routes.route("/api/get_prefs")
def get_prefs():
    if g.user:
        user = User.query.get_or_404(g.user.id)
        return jsonify(preferences=json.loads(user.preferences))
    else:
        return jsonify(preferences={'diet': 'None', 'exclude': []})

@routes.route("/api/update_prefs", methods=["POST"])
def update_prefs():
    data = request.json
    user = User.query.get_or_404(g.user.id)
    user.preferences = json.dumps({"diet": data["diet"], "exclude": data["exclude"]})
    db.session.add(user)
    db.session.commit()
    return jsonify(preferences=user.preferences)

# User auth

@routes.route("/register", methods=["GET", "POST"])
def register_user():
    """Displays and handles user registration form."""

    form = RegisterForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username = form.username.data,
                email=form.email.data,
                password=form.password.data,
            )
            db.session.commit()
        except IntegrityError:
            flash("Username already taken.", "danger")
            return render_template("users/register.html", form=form)
        do_login(user)
        return redirect("/")
    return render_template("users/register.html", form=form)

@routes.route("/login", methods=["GET", "POST"])
def login_user():
    """Displays and handles user login form."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash("Welcome", "success")
            return redirect("/")
        flash("Invalid credentials", "danger")
    return render_template("users/login.html", form=form)

@routes.route("/logout")
def logout():
    """Handles user logout."""

    user = User.query.get_or_404(g.user.id)

    do_logout(user)
    flash("Logged out.", "success")
    return redirect("/")

# Turn off all Flask caching
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@routes.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers["Cache-Control"] = "public, max-age=0"
    return req
