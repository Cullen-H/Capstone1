const BASE_URL = window.location.origin;

let USER_PREFS;

let currentMealplan = null;

const loadingHTML = `
<div id="loading-container">
<div class="loading"></div> 
</div>
`;

axios.get(`${BASE_URL}/api/get_prefs`).then(resp => {
    USER_PREFS = resp.data;
    userDiet = USER_PREFS.preferences.diet;
    userTags = USER_PREFS.preferences.exclude;
});

function genMealPlanHTML(mealplan) {
    let htmlBody = $('<div id="mealplan-container"></div>');
    let daysList = $('<ul></ul>');
    htmlBody.append('<h1>Meal Plan</h1>');

    for (let i = 0; i < mealplan["days"].length; i++) {
        let newLiHeader = $(`<li>Day ${i+1}</li>`);
        let newUl = $('<ul></ul>');
        if (mealplan["days"][i][0]) {
            let newLi = $(`<li style="padding-left: 25px;">Breakfast: <a href="/foods/${mealplan["days"][i][0]["breakfast"]["id"]}">${mealplan["days"][i][0]["breakfast"]["title"]}</a></li>`);
            newUl.append(newLi);
        }
        if (mealplan["days"][i][1]) {
            let newLi = $(`<li style="padding-left: 25px;">Lunch: <a href="/foods/${mealplan["days"][i][1]["lunch"]["id"]}">${mealplan["days"][i][1]["lunch"]["title"]}</a></li>`);
            newUl.append(newLi);
        }
        if (mealplan["days"][i][2]) {
            let newLi = $(`<li style="padding-left: 25px;">Dinner: <a href="/foods/${mealplan["days"][i][2]["dinner"]["id"]}">${mealplan["days"][i][2]["dinner"]["title"]}</a></li>`);
            newUl.append(newLi);
        }
        newLiHeader.append(newUl);
        daysList.append(newLiHeader);
    }
    htmlBody.append(daysList);
    $("#new-plan-container").append(htmlBody);
}

function genGroceryListHTML(grocerylist) {
    let htmlBody = $('<div id="grocerylist-container"></div>');
    let weeksList = $('<ul></ul>');
    htmlBody.append('<h1>Necessary Ingredients</h1>');

    for (let i = 0; i < grocerylist["weeks"].length; i++){
        let newLiHeader = $(`<li>Week ${i+1}</li>`);
        let newUl = $('<ul></ul>')
        for (let ingredient in grocerylist["weeks"][i]) {
            let newLi = $(`<li>${grocerylist["weeks"][i][ingredient]["amount"]} ${grocerylist["weeks"][i][ingredient]["unit"]} of ${ingredient}</li>`);
            newUl.append(newLi);
        }
        newLiHeader.append(newUl);
        weeksList.append(newLiHeader);
    }
    htmlBody.append(weeksList);
    $("#new-plan-container").append(htmlBody);
}

$("#new-plan-submit").on("click", async function() {
        $("#new-plan-save").remove();
        $("#new-plan-container").empty();
        $("#new-plan-container").append(loadingHTML);
    meals = [];
    if ($("#mp-breakfast").is(":checked")) meals.push("breakfast");
    if ($("#mp-lunch").is(":checked")) meals.push("lunch");
    if ($("#mp-dinner").is(":checked")) meals.push("dinner");
    const resp = await axios.post(`${BASE_URL}/api/mealplans/gen_mealplan`, {
        "diet": userDiet,
        "exclude": userTags,
        "days": $("#days-select").val(),
        "meals": meals,
    }).then( res => {
        currentMealplan = res.data.generatedMP;
        genMealPlanHTML(currentMealplan["mealplan"]);
        genGroceryListHTML(currentMealplan["grocerylist"]);
        $("#loading-container").remove();
        $("#btns-container").append('<button id="new-plan-save">Save this plan!</button>');
    });
});

$("#new-plan-save").on("click", async function() {
    const resp = axios.post(`${BASE_URL}/api/save_mealplan`, {
        "mealplan": currentMealplan["mealplan"],
        "grocerylist": currentMealplan["grocerylist"],
    });
});
