var map;
var lookup = [];
var geocoder = new google.maps.Geocoder();
var directionsService = new google.maps.DirectionsService();
var manage = $( "#manage-true" );
var home
var markersArrayNew = [];
var markersArrayOld = [];
if (!manage == '') {
  console.log(manage)
}
else {
  console.log('good')
}

var url = "/blog/user/" + username

// Need to change the center of the map to the home of the user if it's there.  If not, just
// a random place works.  Probably do this through an xml file
function initialize() {
  var mapOptions = {
    center: new google.maps.LatLng(40.44341, -79.94211740000003),
    zoom: 11
  };
  map = new google.maps.Map(document.getElementById("map-canvas"),
    mapOptions);
}

// Codes the address as longitude and latitude.  Allows it to be used by google maps
function codeAddress(user, event_title, datetime_start, datetime_end, address, event_id, picture_url, callback) {
  geocoder.geocode( { 'address': address}, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      callback([user, event_title, datetime_start, datetime_end, address, event_id, picture_url, results[0].geometry.location]);
    } else {
      alert("Geocode was not successful for the following reason: " + status);
    }
  });
}

// Clears the Markers from the array
function clearOverlays(markersArray) {
  for (var i = 0; i < markersArray.length; i++ ) {
    markersArray[i].setMap(null);
  }
  markersArray.length = 0;
}

// Codes the address as longitude and latitude.  Allows it to be used by google maps
function codeAddressOnly( address, callback) {
  geocoder.geocode( { 'address': address}, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      callback(results[0].geometry.location);
    } else {
      alert("Geocode was not successful for the following reason: " + status);
    }
  });
}

function isLocationFree(search) {
  for (var i = 0, l = lookup.length; i < l; i++) {
    if (lookup[i].toString() === search.toString()) {
      return false;
    }
  }
  return true;
}

function createMarker(results) {
        //console.log(results.toString());
        var username = results[0];
        var user = results[0];
        var event_title = results[1];
        var datetime_start = results[2];
        var datetime_end = results[3];
        var location = results[4];
        var event_id = results[5];
        var picture_url = results[6];
        var latlng = results[7];


        var curdate = new Date();
        var dt_start = new Date(datetime_start);
        var dt_end = new Date(datetime_end);
        if (true) {
          var marker = new google.maps.Marker({
              map: map,
              position: latlng,
              title: event_title
          });

          if (dt_start <= curdate && dt_end >= curdate) {
            marker.setAnimation(google.maps.Animation.BOUNCE);
          }

          contentString = '<h1>' + event_title + '</h1>'
          
          if (picture_url) {
            contentString = contentString +
                            '<img src ="' + picture_url + '" alt="' + event_title + '" width = "200px">';
          }
          contentString = contentString +
                          '<div>Event by ' + user + '</div>' +
                          '<div>Starting at: ' + datetime_start + '</div>'+
                          '<div>Ending at: ' + datetime_end + '</div>' + 
                          '<div>Event at: ' + location + '</div>';
          if (user == username) {
              contentString = contentString + 
                              '<a href="/blog/delete-item/' +event_id+ '">Delete Event </a>';
          }

          var infowindow = new google.maps.InfoWindow({
            content: contentString
          });

          var url = '/blog/rsvp-user/' + event_id
	  if (user_authenticated == "True") {
            infowindow.setContent(infowindow.getContent() +
                          '<div>' +
                          '<a href="/blog/rsvp/' +event_id+ '/J">Join </a>' + 
                          '<a href="/blog/rsvp/' +event_id+ '/M">Maybe </a>' + 
                          '<a href="/blog/rsvp/' +event_id+ '/D">Decline </a> </div>');
	    $.ajax({
	      type: 'GET',
	      url: url,
	      datatype: "xml", 
	      success: function(data) {
	        var rsvp_status = $(data).find('status').text();
                infowindow.setContent(infowindow.getContent() +
                          '<div>RSVP Info: ' + rsvp_status + '</div>');
	      }
	    });
	  }

          google.maps.event.addListener(marker, 'click', function() {
            infowindow.open(map,marker);
          });

          var cardImg = $("#event" + event_id).find(".event-img");
          window.cardImg = cardImg;

          cardImg.click(function(){
            infowindow.open(map,marker);
            map.setCenter(marker.getPosition());
          });

          lookup.push(latlng);
          markersArrayNew.push(marker);
          calcRoute(infowindow, home, location);
        }

}

function calcRoute(infowindow, start, end) {
  var request = {
    origin:start,
    destination:end,
    travelMode: google.maps.TravelMode.DRIVING
  };

  directionsService.route(request, function(result, status) {
    if (status == google.maps.DirectionsStatus.OK) {
      var content = infowindow.getContent();
      var distance = result.routes[0].legs[0].distance.text;
      var duration = result.routes[0].legs[0].duration.text;
      infowindow.setContent(content + 
                            '<div>Distance: ' + distance + '</div>' +
                            '<div>Duration: ' + duration + '</div>');
    }
  });
}


var req;

// Sends a new request to update the to-do list
function sendRequest() {
    if (window.XMLHttpRequest) {
        req = new XMLHttpRequest();
    } else {
        req = new ActiveXObject("Microsoft.XMLHTTP");
    }
    req.onreadystatechange = handleResponse;
    
    req.open("GET", "/blog/get-eventlist", true);
    
    req.send(); 
}


// This function is called for each request readystatechange,
// and it will eventually parse the XML response for the request
function handleResponse() {
    if (req.readyState != 4 || req.status != 200) {
        return;
    }

    // Parses the XML response to get a list of DOM nodes representing users
    // and following users
    var xmlData = req.responseXML;
    var events = xmlData.getElementsByTagName("event");

    console.log(events);
    markersArrayOld = markersArrayNew.slice();
    markersArrayNew.length = 0;

    //remove cards from sidebar
    $(".events-list").empty();
    $(".callouts-list").empty();

    // Adds each user to the list again
    for (var i = 0; i < events.length; ++i) {
        // Parses the username from the DOM
        var user = events[i].getElementsByTagName("username")[0].textContent;
        var event_title = events[i].getElementsByTagName("title")[0].textContent;
        var picture = null;
        if (events[i].getElementsByTagName("picture").length > 0)
          picture = events[i].getElementsByTagName("picture")[0].textContent;
        var datetime_start = events[i].getElementsByTagName("datetime_start")[0].textContent;
        var datetime_end = events[i].getElementsByTagName("datetime_end")[0].textContent;
        var location = events[i].getElementsByTagName("location")[0].textContent;
        var event_id = events[i].getElementsByTagName("id")[0].textContent;

        var picture_url = null;
        if (events[i].getElementsByTagName("picture").length != 0) {
          picture_url = events[i].getElementsByTagName("picture")[0].textContent;
        }

        //make cards for sidebar
        var card = new Card(event_title, picture_url, event_id);
        var callout = new Callout(datetime_start, datetime_end, event_id);    
        $(".events-list").append(card);
        $(".callouts-list").append(callout);
        setGoing(event_id);

        // Need to make sure that marker is created depending on whether we want
        // current events, old events, or upcoming events
        codeAddress(user, event_title, datetime_start, datetime_end, location, event_id, picture_url, function(results) {
          createMarker(results);
        });


    }
    console.log( markersArrayOld)
    console.log(markersArrayNew);
    clearOverlays(markersArrayOld);
    console.log( markersArrayOld)
    console.log(markersArrayNew);
    
}

function Card(title, img, id) {
  var card = $("#event-template").children().clone();

  //change title, img, id
  card.attr('id', "event" + id);
  card.find(".event-title").html(title);
  if (img != null)
    card.find(".event-img").attr('src', "/blog/photo/"+id);
  else
    card.find(".event-img").attr('src', "/static/blog/img/icons/georiot-logo.png");


  //set handlers
  card.find(".people").attr('id', id);
  card.find(".info").attr('id', id);
  card.find(".rsvp").attr('id', id);
  card.find(".people").click(function(){
    var target = $(".callouts-list").find("#people" + $(this).attr('id'));
    $(".callouts-list").find(".callout").hide();
    target.show();
  });
  card.find(".info").click(function(){
    var target = $(".callouts-list").find("#info" + $(this).attr('id'));
    $(".callouts-list").find(".callout").hide();
    target.show();
  });
  card.find(".rsvp").click(function(){
    rsvp(id);
  });

  return card;
}

function Callout(start, end, id) {
  var callout = $("#callout-template").children().clone();

  //change Information date/time
  callout.find(".start").html(start);
  callout.find(".end").html(end);

  //set ids
  callout.find(".people").attr('id', 'people' + id);
  callout.find(".info").attr('id', 'info' + id);

  return callout;
}

function setGoing(id) {
  $.ajax({
    url: '/blog/event/'+id,
    type: 'GET',
    datatype: 'xml',
    success: function (data) {
      console.log(data);
      
      window.users = $(data).find("user");
      users = window.users;

      var text = $("#people" + id).find(".callout-text");

      for (var i = 0; i < users.length; ++i) {
        var newText = document.createElement("h5");
        newText.innerHTML = users[i].innerHTML;
        text.append(newText);
      }
    }
  });
}

function addCard(title, id, start, end) {
  ev = $.parseJSON(test.events)[0].fields;
  card = new Card(ev.title, ev.picture, id);
  callout = new Callout(ev.datetime_start, ev.datetime_end, id);

  $(".events-list").append(card);
  $(".callouts-list").append(callout);
}

function cardTest(id) {
  var ev = $.parseJSON(test.events)[0].fields;
  var card = new Card(ev.title, ev.picture, id);
  var callout = new Callout(ev.datetime_start, ev.datetime_end, id);

  $(".events-list").append(card);
  $(".callouts-list").append(callout);
}

// causes the sendRequest function to run every 5 seconds
window.setInterval(sendRequest, 30000);
sendRequest();
google.maps.event.addDomListener(window, 'load', initialize);

if (user_authenticated == "True") {
  $.ajax({
    type: 'GET',
    url: url,
    datatype: "xml", 
    success: function(data) {
      home = $(data).find('location').text();
      
      codeAddressOnly(home, function(results) {
        var latlng = results;
        map.setCenter(latlng);
      });
    }
  });
}
