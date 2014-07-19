$(document).ready(function() {
	console.log("go team mdfs");

	var formatAccessToken = function(service, accessToken) {
		return {'access_token': accessToken, 'service': service};
	}

	var postAccessToken = function(service, accessToken, callback) {
		data = formatAccessToken('soundcloud', accessToken);
		$.post( "/initialize", function(data) {
			if (callback) {
				callback(data);
			}
		});
	}

	var accessTokenCallback = function(json){
		console.log(json);
	}

	var DROPBOX_APP_KEY = "lrbb9ssu70c3qdb";
	var SOUNDCLOUD_CLIENT_ID = "d3d8d0b3e2db7a1085678bd9478024dd";

	SC.initialize({
		client_id: SOUNDCLOUD_CLIENT_ID,
		redirect_uri: "http://localhost:5000/callback",
		scope: 'non-expiring'
	});


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
		postAccessToken('dropbox', dropboxAccessToken, accessTokenCallback);
	    // Client is authenticated. Display UI.
	}



	var soundcloudLogin = function(){
		SC.connect(function() {
		    SC.get('/me', function(me) { 
		      	var soundcloudAccessToken = SC.accessToken();
		      	postAccessToken('soundcloud', soundcloudAccessToken, accessTokenCallback);
		    });
		});
	}

	$(".soundcloud-login").click(function() {
		soundcloudLogin();
	});

	$(".dropbox-login").click(function() {
		client.authenticate();
	})
});

