# Spin a Meal

Hosted link: https://cullen-hutchison-capstone1.herokuapp.com/

### Description
<p>
This is a simple website for providing meal recommendations. You can filter it by diet and choose specific ingredients to exclude. If you sign up for an account, 
you can also like or dislike foods. Foods will then be recommended more or less frequently. As a logged in user, you may also create a meal plan 
this will also follow your diet and exlusion preferences. I thought it was important to provide users the option to avoid foods they dislike and, 
after a reasonable amount of time, provide them with foods they had previously liked. Generatiung meal plans is an important part of 
any website that gives users foods to make. On top of that, I chose to add grocery lists week by week for these meal plans. Having that addition 
will make cooking these foods far less inconvenient.
</p>

### Standard User Flow
<p>
Upon visting the site, you will automatically be given a meal recommendation. If you are logged in, it will follow your user preferences. 
You will have the option to skip that recommendation or cook it. Skipping will provide a new recommendation, whereas pressing cook will redirect you 
to a food details page. In that page you will ahve instructions, ingredients and the option tolike or dislike. There is, at all stages, a navbar that 
can redirect you to home, take you to login/register, or for users who are logged in, allow them to visit their profile ort log out. In your profile 
you can adjust your dietary and exclusion preferences. You can also viwe your current meal plan and grocery list if applciable.
</p>

### API notes
<p>
I deliberately avoided more concise filtering to decrease the number of requests being sent to the server during this project. 
If I had access to a paid plan I would have liked to filter more thoroughly based on usert preferences.
</p>

### Tech Stack Used

This project used:
 - Spoonacular API
 - Flask
 - Postgresql
 - SQLAlchemy
 - Bcrypt
 - WTForms
 - requests - python
 - ajax - js
 - font awesome
 - Jinja

## Original Project Proposal

### Goal
<p>
The goal of this website is to provide users with daily meal reccomendations and plans. In doing so, I hope 
to help people come up with new foods to make and provide an alternative to people's current eating habits.
</p>

### Demographic
<p>
This website exists for those who feel that they eat the same foods every week. Anyone who wants to try new 
foods and break their current habits would benefit from this project.
</p>

### Data Sources
<p>
I plan to use the spoonacular food api. It contains ovfer 5,000 possible recipes including recipes, nutrition data, 
price data, and substitutions for ingredients.

API link: https://spoonacular.com/food-api
</p>

### Project Outline

#### Database Schema
Rough Draft (subject to change)
![database schema demo](https://github.com/Cullen-H/Capstone1/blob/demo/dbschema.png)

#### Potential Issues
I may run into isses trying to reccomend new foods to users and ensuring they weren't reccomended a similar food too recently.
This could be solved by adding foods to a blacklist after they've been reccomended to a user. In the event that a user is not logged 
in, I could store a temporary blacklist that persists for their current session. it may also be difficult to decide when liked foods

#### Sensitive Info
I plan to set up user accounts so passwords will need to be hashed for storage.

#### Functionality
This website will provide meal reccomendations. There will be an option to skip a food and have an alternate reccomended to them. 
Users who are logged in will be able to create meal plans for the week and generate grocery lists from those meal plans. Grocery
lists would also provide estimated costs and could be sorted for different periods of time. You will also have the option to like 
or dislike foods, and that will effect their likelyhood to be reccomended to you again in the future.

#### User Flow
![user flow demo](https://github.com/Cullen-H/Capstone1/blob/demo/userflow.png)

#### Stretch Goals
- I would like to add the ability for a user to search for foods of a specific type and display it to them
- More accurate pricing data based on location or nearby stores
  - expanding on this, you could create a mobile order to a specific grocery store

#### What makes this more than CRUD?
This project sorts and reccomends data based on user preference and decides if a specific piece of data should be excluded based on 
reccomendation history and ratings.
