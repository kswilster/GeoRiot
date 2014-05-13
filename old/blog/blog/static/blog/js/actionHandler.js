function login() {
	request = {};

	request['csrfmiddlewaretoken'] = $("[name='csrfmiddlewaretoken']").val();
	request['username'] = $("#username").val();
	request['password'] = $("#password").val();

	$.ajax({
		'url' : '/blog/login',
		'type' : 'POST',
		'data' : request,
		'success' : handleLogin,
	});
}

function logout() {
	console.log("logging out");
	$.ajax({
		'url' : '/blog/logout',
		'type' : 'GET',
		'success' : function(){
			$(".logged-out").show();
			$(".logged-in").hide();
			window.user_authenticated = "False"
			window.username = null;
			location.reload();
		}
	})
}

function handleLogin(response) {
	var loginBox = $("#login-errors");
	loginBox.empty();

	if (!response.success) {
		for (error in response.errors) {
			var e = document.createElement("tr");
			e.innerHTML = response.errors[error];
			loginBox.append(e);
		}
	} else {
		var body = $("#login").find(".modal-body");

		var text = document.createElement("h2");
		text.innerHTML = "Successfully logged in";
		body.html(text);

		//change view
		$(".logged-out").hide();
		$(".logged-in").show();
		if (response.username != null && response.username != "")
			$("#user-welcome").innerHTML = "Welcome, " + response.username;
		else
			$("#user-welcome").innerHTML = "Welcome!"

	}
}

function register() {
	request = {};

	request['csrfmiddlewaretoken'] = $("[name='csrfmiddlewaretoken']").val();
	request['username'] = $("#id_username").val();
	request['password1'] = $("#id_password1").val();
	request['password2'] = $("#id_password2").val();
	request['email'] = $("#id_email").val();
	request['street'] = $("#id_street").val();
	request['city'] = $("#id_city").val();
	request['state'] = $("#id_state").val();
	request['zipcode'] = $("#id_zipcode").val();

	$.ajax({
		'url' : '/blog/register',
		'type' : 'POST',
		'data' : request,
		'success' : handleRegister,
	});
}

function handleRegister(response) {
	console.log(response);
	var errBox = $("#register-errors");
	errBox.empty();
	
	if (!response.success) {
		for (error in response.errors) {
			var row = document.createElement("tr");
			row.innerHTML = response.errors[error];
			errBox.append(row);
		}
	} else {
		var body = $("#register").find(".modal-body");
		body.empty();

		var regText = document.createElement("h2");
		regText.innerHTML = "Registered Successfully, check your email for confirmation.";
		body.append(regText);
	}

}

function addEvent(event) {
	//stop normal form function
	event.preventDefault();

	var fd = new FormData($(this).context);
	var token = $(this).find("[name='csrfmiddlewaretoken']");
	fd.append("csrfmiddlewaretoken", token.val());

    $.ajax({
        'type': $(this).attr('method'),
        'url': $(this).attr('action'),
        'data': fd,
        'contentType': false,
        'processData': false,
        'enctype': 'multipart/form-data',
        'success': handleEventAdd,
        'error': function(data) {
            $("#add-event-body").html("Something went wrong!");
        },
    });
    return false;
}

function handleEventAdd(data) {
	$("#add-event-body").html(data);
	var add = $('#add_event_form');
    add.submit(addEvent);
}

function fetchEvents() {
	$.ajax({
		type: 'GET',
		url: '/blog/get-eventlist',
		success: function (data) {
			window.test = data;
		}
	})
}

function rsvp(id) {
	$.ajax({
		type: 'GET',
		url: '/blog/rsvp/'+id+'/J',
		success: function(){
			alert("RSVP'd for EVENT " + id);
		}
	});
}