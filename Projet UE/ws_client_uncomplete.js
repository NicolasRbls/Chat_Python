// Since this is a secure connection, we must create a
// secured websocket connection.

var nb_messages = 0;
var authenticated = false;

// We need to keep some DOM elements in memory
var messages_zone;
var txt_input_msg;
var txt_input_nickname;
var p_nickname;
var p_nb_mess;
var ul_userlist;
var bt_connect;
var bt_disconnect;
var bt_send_msg;

var websocket;
var chat ;

//Page modifiers

// called when the websocket is connected
// show up the chat window
function ws_connected(){

}

// called when the websocket is disconnected
// hide the chat window, and show a button to reconnect
function ws_disconnected(){

}

function create_message_element(sender_name, mess_id, time_str, mess_content){

    var msg_container = document.createElement("div");
    msg_container.className = "message_container";

    var username_element = document.createElement("h1");
    username_element.className = "username";
    username_element.innerHTML = sender_name;
    msg_container.appendChild(username_element);

    var content_element = document.createElement("h2");
    content_element.className = "message_content";
    content_element.innerHTML = mess_content;
    msg_container.appendChild(content_element);

    var msg_data_element = document.createElement("p");
    msg_data_element.className = "msg_data";
    msg_container.appendChild(msg_data_element);

    var msg_time_element = document.createElement("span");
    msg_time_element.className = "message_time";
    msg_time_element.innerHTML = time_str;
    msg_data_element.appendChild(msg_time_element);

    var msg_id_element = document.createElement("p");
    msg_id_element.className = "message_id";
    msg_id_element.innerHTML = mess_id;
    msg_data_element.appendChild(msg_id_element);

    return msg_container;
}

// create a li element containing this username
function create_username_element(username){

}

// get a li element containing this username
// or null if it does not exist.
function get_username_element(username){

}

// remove a user li element from the list
function remove_username_element(username){

}
// WebSocket event handlers
function open_handler(websocket, ticket){

    websocket.onopen = function(e){

        console.log("Connected to WebSocket ChatServer!");

        // When connected, we send the ticket given
        // by the HTTPS server.
        var json_ticket = {"ticket": ticket};
        websocket.send(JSON.stringify(json_ticket));
        console.log("Ticket sent to the WebSocket ChatServer.");
    };
}
// listener of message event
function message_handler(websocket, ticket){


    websocket.onmessage = function(event){

        console.log("Message received from the server");
        const msg_data = JSON.parse(event.data);
        const msg_type = msg_data["msg_type"] ;
        console.log(msg_type);

        switch (msg_type) {
          case 1:
            if (msg_data["auth_result"] != 0) {
              console.log("Authentication failed, closing websocket...");
              websocket.close();
            }
            break;
          case 2:
            zone = create_message_element(msg_data["from"],msg_data["id"],msg_data["timestamp"],msg_data["content"]);
            chat.appendChild(zone);
            break;
          case 3:
            if (msg_data.hasOwnProperty("update_user_liste")){
            const users = msg_data["update_user_liste"];
            const list = document.getElementById("list");
            list.innerHTML = ""; // clear the list first
            for (let i = 0; i < users.length; i++) {
                const li = document.createElement("li");
                li.textContent = users[i];
                list.appendChild(li);
            };
            };
             if (msg_data.hasOwnProperty("client_name")){
                const name = document.getElementById("nickname");
                const user_name = msg_data["client_name"];
                user_name.textContent = user_name;
                name.innerHTML = "Nickname : "+user_name;

                const status = document.getElementById("connection_status");
                status.innerHTML = "Status : Connected";

                const msg = document.getElementById("nb_mess");
                msg.innerHTML = "Messages sent : "+nb_messages;

             };
            break;
        };
    };
};

function close_handler(websocket){
    websocket.onclose = function(event){
        bt_send_msg.disabled = true;
    }

};

function error_handler(websocket){
    websocket.onerror = function(event){
        alert("Error");
    }
}

function buttons_handlers(){

  const bt_connect = document.getElementById("connect");
  const bt_disconnect = document.getElementById("disconnect");
  const bt_send_msg = document.getElementById("msg_send_button");

  bt_connect.addEventListener("click", function() {
  let connection_success = false;
  console.log("Fetching ticket...");
  fetch("/get_ws_ticket")
    .then(response => response.json())
    .then(msg_json => {
      console.log(msg_json);
      connection_success = msg_json["result"] === 0;
      console.log("...")
      if (connection_success) {
        const ticket = msg_json["ticket"];
        //const nb_messages_db = msg_json["nb_messages"];
        //nb_messages = nb_messages_db;
        console.log("Connecting to WSServer...");
        websocket = new WebSocket("wss://localhost:8001/");
        console.log("Connection success!");
        bt_send_msg.disabled = false;
        open_handler(websocket, ticket);
        message_handler(websocket, ticket);
        close_handler(websocket);
        error_handler(websocket);
      } else {
        // Show something to the user to make him retry...
        print("Connection failed!");
      }
    })
    .catch(error => {
      console.log("An error has occurred... : " + error.message);
    });
});

bt_send_msg.addEventListener("click", function() {
    var msg = txt_input_msg.value;
    console.log("Message content: " + msg);
    var date_now = new Date();
    var timestamp = date_now.getTime();
    var data = {
        "content": msg,
        "timestamp": timestamp
    };
    var json_data = JSON.stringify(data);
    websocket.send(json_data);
    nb_messages += 1;
    const msg2 = document.getElementById("nb_mess");
    msg2.innerHTML = "Messages sent : "+nb_messages;

});

bt_disconnect.addEventListener("click", function() {
    bt_send_msg.disabled = true;
    const status2 = document.getElementById("connection_status");
    status2.innerHTML = "Status : Disconnected";
    websocket.close();
});

}



window.addEventListener("DOMContentLoaded", function() {

    // Keep some DOM elements in memory
    messages_zone = document.querySelector("#message_zone");
    txt_input_msg = document.querySelector("#input_message");
    txt_input_nickname = document.querySelector("#input_nickname");
    p_nickname = document.querySelector("#nickname");
    p_nb_mess = document.querySelector("#nb_mess");
    ul_userlist = document.querySelector("#list");
    bt_connect = document.querySelector("#connect");
    bt_disconnect = document.querySelector("#disconnect");
    bt_send_msg = document.querySelector("#msg_send_button");
    chat = document.getElementById("message_zone");
    // We must listen to these buttons
    buttons_handlers();

});
