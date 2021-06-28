const BASE_URL = window.location.origin;

function setRatings(ratings) {
    console.log("liked: ")
    console.log(ratings["liked"]);
    console.log("disliked: ")
    console.log(ratings["disliked"]);
    console.log("------------------");
    $("#like-btn").removeClass("far");
    $("#like-btn").removeClass("fas");
    $("#like-btn").removeClass("danger");
    $("#like-btn").removeClass("success");
    $("#dislike-btn").removeClass("far");
    $("#dislike-btn").removeClass("fas");
    $("#dislike-btn").removeClass("danger");
    $("#dislike-btn").removeClass("success");
    if (ratings["liked"]) {
        $("#like-btn").addClass("fas success");
    } else {
        $("#like-btn").addClass("far")
    }
    if (ratings["disliked"]) {
        $("#dislike-btn").addClass("fas danger");
    } else {
        $("#dislike-btn").addClass("far");
    }
}

axios.get(`${BASE_URL}/foods/checkrating/${foodApiId}`).then(resp => {
    setRatings(resp.data);
});

$("#like-btn").click(async function(){
    const resp = await axios.post(`${BASE_URL}/foods/like/${foodApiId}`);
    setRatings(resp.data);
});

$("#dislike-btn").click(async function(){
    const resp = await axios.post(`${BASE_URL}/foods/dislike/${foodApiId}`);
    setRatings(resp.data);
});
