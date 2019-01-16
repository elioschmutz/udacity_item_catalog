window.fbAsyncInit = function() {
    FB.init({
        appId      : fb_client_id,
        cookie     : true,
        xfbml      : true,
        version    : "v3.2"
    });

    FB.AppEvents.logPageView();

};

// Here we run a very simple test of the Graph API after login is
// successful.  See statusChangeCallback() for when this call is made.
function onFacebookSignIn() {
    var access_token = FB.getAuthResponse()["accessToken"];
    FB.api("/me", function(response) {
        $.ajax({
            type: "POST",
            url: "/fbconnect?csrf_token=" + csrf_token,
            processData: false,
            data: access_token,
            contentType: "application/octet-stream; charset=utf-8",
            success: function(result) {
                // Handle or verify the server response if necessary.
                if (result) {
                    window.location.href = "/";
                } else {
                    $(".error").html("Something went wrong");
                }
            }
        });
    });
}
