function onGoogleSignIn(googleUser) {
    // The ID token you need to pass to your backend:
    var id_token = googleUser["code"];
    var payload = {
        id_token: id_token,
        csrf_token: csrf_token
    };
    $.post("/googlelogin", payload).done(function(data) {
        if ( data ) {
            window.location.href = "/";
        }

    }).fail(function(data) {
        if (data.status === 403) {
            $(".error").html("Something went wrong: " + data.statusText);
        } else {
            $(".error").html("Something went wrong: " + data.responseJSON);
        }
    });
}
