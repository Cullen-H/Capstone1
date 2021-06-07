# Food Reccommender

Lorem ipsum dolor sit amet consectetur adipisicing elit. Maxime mollitia,
molestiae quas vel sint commodi repudiandae consequuntur voluptatum laborum
numquam blanditiis harum quisquam eius sed odit fugiat iusto fuga praesentium
optio, eaque rerum! Provident similique accusantium nemo autem.

## Proposal

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
##### Rough Draft (subject to change)
![database schema demo](https://github.com/Cullen-H/Capstone1/blob/demo/dbschema.jpg)

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
![user flow demo](https://github.com/Cullen-H/Capstone1/blob/demo/userflow.jpg)

#### Stretch Goals
- I would like to add the ability for a user to search for foods of a specific type and display it to them
- More accurate pricing data based on location or nearby stores
  - expanding on this, you could create a mobile order to a specific grocery store

#### What makes this more than CRUD?
This project sorts and reccomends data based on user preference and decides if a specific piece of data should be excluded based on 
reccomendation history and ratings.
