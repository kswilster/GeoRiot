var req;

// Sends a new request to update the to-do list
function sendRequest() {
    if (window.XMLHttpRequest) {
        req = new XMLHttpRequest();
    } else {
        req = new ActiveXObject("Microsoft.XMLHTTP");
    }
    req.onreadystatechange = handleResponse;
    req.open("GET", "/blog/get-userlist", true);
    req.send(); 
}

// This function is called for each request readystatechange,
// and it will eventually parse the XML response for the request
function handleResponse() {
    if (req.readyState != 4 || req.status != 200) {
        return;
    }

    // Removes the old user list
    var list = document.getElementById("userlist");
    var one_follow = document.getElementById("one_follow");
    while (list.hasChildNodes()) {
        list.removeChild(list.firstChild);
    }

    // Parses the XML response to get a list of DOM nodes representing users
    // and following users
    var xmlData = req.responseXML;
    var users = xmlData.getElementsByTagName("user");
    var fol_users = xmlData.getElementsByTagName("followuser");
    
    // Makes a list of following users to give out
    var users_fol = [];
    for (var i = 0; i < fol_users.length; ++i) {
        users_fol.push(fol_users[i].getElementsByTagName("username")[0].textContent)
    }

    // Adds each user to the list again
    for (var i = 0; i < users.length; ++i) {
        // Parses the username from the DOM
        var username = users[i].getElementsByTagName("username")[0].textContent
  
        // Builds a new HTML DIV item for each list
        var div = document.createElement('DIV');

        var input = document.createElement('INPUT');
        input.type = 'submit';
        input.name = 'req_user';
        input.value= username;

	// If the user is being followed or is currently clicked on by anon
        // user, then it is highlighted red
        if ($.inArray(username, users_fol) >= 0)
            input.style.background = "red";
        if (one_follow  && one_follow.value == username) {
            input.style.background = "red";
            input.id = "one_follow";
        }

        // Adds user back to the list
        div.appendChild(input);
        list.appendChild(div);
    }
        
}

// causes the sendRequest function to run every 5 seconds
window.setInterval(sendRequest, 30000);
