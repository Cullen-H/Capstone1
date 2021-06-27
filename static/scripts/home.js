const BASE_URL = "http://localhost:5000";

let USER_PREFS;

let userDiet;

let userTags;

let currRespId;

axios.get(`${BASE_URL}/api/get_prefs`).then(resp => {
    USER_PREFS = resp.data;
    userDiet = USER_PREFS.preferences.diet;
    $("#diet-dd").val(userDiet)
    userTags = USER_PREFS.preferences.exclude;
    getRecommendation();
});


const loadingHTML = `
<h1>Please Wait</h1>
<div id="recommendation-img-container">
<div class="loading"></div> 
</div>
`

const imageNA = 'static/images/imageNA.jpg';

async function getRecommendation() {
    // change to recursive for checking likes/dislikes/blacklistS
    // check liked and cross ref with black lists. Give chance to recommend a previously liked food.
    currRespId = null;
    $("#recommendation-container").empty();
    $("#recommendation-container").append(loadingHTML);

    const resp = await axios.get(`${BASE_URL}/api/get_food`, {
        params: {
        "diet": userDiet,
        "exclude": userTags.join(",")
        }
    });

    respData = resp.data.results[0]

    try {
        const respHTML = `
        <h1>${respData.title}</h1>
        <div id="recommendation-img-container">
        <img src="${respData.image}"></img>
        </div>
        `;
        $("#recommendation-container").empty();
        $("#recommendation-container").append(respHTML);
        currRespId = respData.id;
    } catch {
        console.log("Server error -- limit reached.")
        const respHTML = `
        <h1>Failed To Get Recommendation</h1>
        <div id="recommendation-img-container">
        <img src="${imageNA}"></img>
        </div>
        `;
        $("#recommendation-container").empty();
        $("#recommendation-container").append(respHTML);
    }
    $("#cook-btn-a").attr("href", `${BASE_URL}/foods/${currRespId}`);

}

$("#skip-btn").click(function() {
    getRecommendation('random');
})
