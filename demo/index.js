$(document).ready(function() {
	console.log("go team mdfs");

	var DROPBOX_APP_KEY = "lrbb9ssu70c3qdb";
	var SOUNDCLOUD_CLIENT_ID = "d3d8d0b3e2db7a1085678bd9478024dd";

	var client = new Dropbox.Client({key: DROPBOX_APP_KEY});
	// Try to finish OAuth authorization.
	client.authenticate({interactive: false}, function (error) {

	    if (error) {
	        alert('Authentication error: ' + error);
	    }
	});

	if (client.isAuthenticated()) {
		var dropboxAccessToken = client._credentials.token;
		console.log(dropboxAccessToken);
		mdfs.postAccessToken('dropbox', dropboxAccessToken, mdfs.accessTokenCallback);
	    // Client is authenticated. Display UI.
	}


	SC.initialize({
	    client_id: SOUNDCLOUD_CLIENT_ID,
	    redirect_uri: "http://localhost:5000/callback",
	    scope: 'non-expiring'
	});


	var soundcloudLogin = function(){
		SC.connect(function() {
		    SC.get('/me', function(me) { 
		      	var soundcloudAccessToken = SC.accessToken();
		      	mdfs.postAccessToken('soundcloud', soundcloudAccessToken, mdfs.accessTokenCallback);
		    });
		});
	}

	$(".soundcloud-login").click(function() {
		console.log('soundcloud-login');
		soundcloudLogin();
	});

	$(".dropbox-login").click(function() {
		client.authenticate();
	})

	$(".facebook-login").click(function() {
		 FB.login(function(response) {
		   if (response.authResponse) {
		     console.log('Welcome!  Fetching your information.... ');
		     FB.api('/me', function(response) {
		       console.log('Good to see you, ' + response.name + '.');
		     });
		   } else {
		     console.log('User cancelled login or did not fully authorize.');
		   }
		 }, {scope: 'publish_actions,user_photos,public_profile,email'});
		 checkLoginState();
	});
});

