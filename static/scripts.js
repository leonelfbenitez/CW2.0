$(document).ready(function() {
    var username = getCookie("username");
    var password = getCookie("password");

    if (username != "" && password != "") {
        //If username found and credentials are valid
        $("#loginForm").hide();
        $("#logoutBtn").show();
        //Change status
        $("#status").html("<b>Status: </b> Logged in");
    }
});

function logout() {
    document.cookie = "username=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "password=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    location.reload(true);
}

function setCookie(cname, cvalue, exhours) {
    const d = new Date();
    d.setTime(d.getTime() + (exhours * 60 * 60 * 1000));
    let expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function login() {
    var username = (document.getElementById('username').value).trim();
    var password = (document.getElementById('password').value).trim();

    var formData = "username=" + username + "&password=" + password;

    $.ajax({
        url: "http://localhost:5000/user/login",
        type: "POST",
        data: formData,
        success: function(data) {
            if (data['message'] == "OK") {
                //If username found and credentials are valid
                $("#loginForm").hide();
                $("#logoutBtn").show();
                //Change status
                $("#status").html("<b>Status: </b> Logged in");
                //Set cookies
                setCookie("username", username, 1);
                setCookie("password", password, 1);
                alert("OK");
                $("#login_stat").val("test");
            } else {
                alert(data['message']);
                $("#logoutBtn").hide();
                $("#status").html("<b>Status: </b> Not logged in");
                $("#login_stat").val("0");
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            alert("Error: " + textStatus + " " + errorThrown);
        }
    })
}