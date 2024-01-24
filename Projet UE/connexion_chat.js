document.addEventListener("DOMContentLoaded" , function(event) {
    const authentication_form = document.getElementById("test_auth") ;
    const account_creation_form = document.getElementById ("create_account");

    // Sending an account creation request

    account_creation_form.addEventListener("submit", function(e) {
      e.preventDefault(); // prevent the default form's behavior (sending POST data)

      var xhttp = new XMLHttpRequest();
      var data = new FormData(account_creation_form); // get the data of form

      var username = data.get("username"); // get the value of the <input name="username">
      var password = data.get("password"); // get the value of the <input name="password">
      var password_bis = data.get("password_bis"); // get the value of the <input name="password">
      if (password != password_bis) {
        alert("Passwords aren't matching!")
        return;
      }

      var user_json_data = { // create the JSON object which will sent as the data in the body
        "username": username,
        "password": password
      };

      xhttp.onreadystatechange = function() { // this function will run when the server respond back
        if (xhttp.readyState == 4) {
          // this request should return a HTTP resource
          var res = xhttp.responseText;
          if (xhttp.status != 200) { // If the response from the server has not a response code of: 200
            alert("Account creation failed!");
          } else {
            // We reload the page
            window.location.replace("/accueil_auth.html");
          }
        }
      }
      xhttp.open("POST", '/connexion_chat'); // Create a POST request to send for the server
      xhttp.setRequestHeader("content-type", "application/json"); // set the content type to json (like the server wants)
      xhttp.send(JSON.stringify(user_json_data), false); // put the JSON object in the body of that request and send that request
    });


    // Sending an authentication request
    authentication_form.addEventListener("submit", function(e) {
    e.preventDefault(); // prevent the default form's behavior (sending POST data)
    var xhttp = new XMLHttpRequest();
    var data = new FormData(authentication_form); // get the data of form

    var username = data.get("username"); // get the value of the <input name="username">
    var password = data.get("password"); // get the value of the <input name="password">

    var user_json_data = { // create the JSON object which will sent as the data in the body
      "username": username,
      "password": password
    };

    xhttp.onreadystatechange = function() { // this function will run when the server respond back
      if (xhttp.readyState == 4) {
        // this request should return a HTTP resource
        var res = xhttp.responseText;
        if (xhttp.status != 200) { // If the response from the server has not a response code of: 200
          alert("Authentication failed!");
        } else {
          // We reload the page
          window.location.replace("/member_page.html");
          }
        }
      }

      xhttp.open("POST", '/authenticate'); // Create a POST request to send for the server
      xhttp.setRequestHeader("content-type", "application/json"); // set the content type to json (like the server wants)
      xhttp.send(JSON.stringify(user_json_data), false); // put the JSON object in the body of that request and send that request
    });
});