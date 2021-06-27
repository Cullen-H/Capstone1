const BASE_URL = "http://localhost:5000";

let USER_PREFS;

let userDiet;

let userTags;

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
    $("#profile-container").append(htmlBody);
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
    $("#profile-container").append(htmlBody);
}

function genTagHTML(tagVal) {
    return `<span>${tagVal} <i id="tag-${tagVal}" class="x-btn fas fa-times-circle"></i></span>`;
}

$("#save-changes-btn").on("click", async function(e) {
    const resp = await axios.post(`${BASE_URL}/api/update_prefs`, {
        "diet": $("#diet-dd").val(),
        "exclude": userTags
    });
});

axios.get(`${BASE_URL}/api/get_prefs`).then(resp => {
    USER_PREFS = resp.data;
    userDiet = USER_PREFS.preferences.diet;
    userTags = USER_PREFS.preferences.exclude;
    $("#diet-dd").val(userDiet);
    for (let i of userTags){
        $("#excluded-tags").append(genTagHTML(i));
        $(`#tag-${i}`).on("click", function () {
            $(`#tag-${i}`).closest("span").remove();
            userTags.pop(userTags.indexOf(i));
        });
    }
});

axios.get(`${BASE_URL}/api/mealplans/get_mealplan/${user_id}`).then(resp => {
    currentMealplan = resp.data;
});

$("#excluded-input").on("keypress", function(e) {
    if (e.which === 13) {
        const newTag = genTagHTML($("#excluded-input").val());
        if (userTags.indexOf(newTag) !== '-1') {
            userTags.push($("#excluded-input").val());
            $("#excluded-tags").append(newTag);
            $(`#tag-${$("#excluded-input").val()}`).on("click", function() {
                $(`#tag-${$("#excluded-input").val()}`).closest(span).remove();
                userTags.pop(userTags.indexOf($("#excluded-input").val()));
            });
        }
        $("#excluded-input").val('');
    }
});

$(".x-btn").click(function() {
    console.log("Test");
});
