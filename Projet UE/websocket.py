import asyncio
import ssl
import uuid
import datetime
import websockets
import json
from sys import stderr
from json import JSONDecodeError


class WSChatClient:
    def __init__(self, username: str, nb_messages: int , ticket: str):
        self.username = username
        self.nb_messages = nb_messages
        self.websocket = None
        self.ticket = ticket
        self.connected = False


class WSChatServer:
    def __init__(self, port: int, context):
        self.clients = {}
        self.total_messages = 0
        self.sessions = {}
        self.websockets_list=[]
        self.server = websockets.serve(self.handler, "localhost", port, ssl=context)

    def client_authentication(self, auth_dict: dict) -> int:
        """
        Verifies the client authentication ticket.
        :param auth_dict: Authentication dictionary sent by the client
        :return: 0 if authentication succeeded, 1 if the ticket is invalid, 2 if there is a JSON error
        """
        try:
            # Extract the ticket from the authentication dictionary
            ticket = auth_dict["ticket"]
            # Check if the ticket is valid
            if ticket in self.sessions:
                return 0  # authentication succeeded
            else:
                return 1  # invalid ticket

        except KeyError:
            # The authentication dictionary does not contain the required fields
            return 2  # JSON error

    async def handler(self, websocket):
        """
        Called when a client connects. Each client has its own function
        running concurrently. The function stops when the connection is ended.
        :param self: This server
        :param websocket: Websocket of the client
        :return: Nothing
        """
        print("WSChatServer - new connection", websocket)

        # As predicted on the documentation, the first message a WS client should
        # send contains its credentials. It will be sent via JSON format.
        auth_result = -1
        client_ticket = None
        try:
            auth_message = await websocket.recv()
            #print("Auth message received: {}".format(auth_message))
            message_dict = json.loads(auth_message)
            print("Auth message received: {}".format(message_dict))
        except websockets.ConnectionClosedOK:
            print("This client has successfully disconnected during authentication.")
            return
        except websockets.ConnectionClosed as e:
            print(e, file=stderr)
            return
        except websockets.ConnectionClosedError as e:
            print(e, file=stderr)
            return
        except JSONDecodeError as e:
            print(e, file=stderr)
            auth_result = 2  # JSON error

        if auth_result != 2:
            auth_result = self.client_authentication(message_dict)

        auth_answer = {
            "msg_type": 1,  # this message is an authentication result
            "auth_result": auth_result
        }
        if auth_result == 0:
            auth_answer["log"] = "You are now authenticated!"
            client_ticket = message_dict["ticket"]
        else:
            auth_answer["log"] = "The authentication has failed!"

        print(auth_answer)
        await websocket.send(json.dumps(auth_answer))
        # 1. On met à jour l'instance client sur le serveur
        client = self.sessions[client_ticket]
        client.authenticated = True
        client.ws = websocket

        # On ajoute le websocket à la liste des websockets
        self.websockets_list.append(websocket)

        self_dict = {
            "msg_type": 3,
            "client_name": client.username
        }
        await websocket.send(json.dumps(self_dict))
        # 2. On envoie une notification de connexion à tout le monde
        notification_dict = {
            "msg_type": 3,
            "new_client": client.username
        }
        websockets.broadcast(self.websockets_list, json.dumps(notification_dict))
        # 3. On envoie la liste des utilisateurs connectés
        user_list = [c.username for c in self.clients.values()]
        user_dic = {
            "msg_type": 3,
            "update_user_liste":user_list,
        }
        await websocket.send(json.dumps(user_dic))
        # 4. The chat session with this client can begin.
        while True:
            try:
                message = await websocket.recv()
                print("aa")
                # Nous n'enverrons que des messages JSON.
                # Lorsque nous recevons un message, nous devons attendre la fin avant de le traiter.
                await self.handler_message(client, json.loads(message))
            except websockets.exceptions.ConnectionClosedOK:
                print("WSChatServer - This client has successfully disconnected.")
                break
            except websockets.exceptions.ConnectionClosed as e:
                print(e)
                break
            except websockets.exceptions.ConnectionClosedError as e:
                print(e)
                break
            except JSONDecodeError as e:
                print(e)
                # Le format JSON du message est invalide.
                msg_dict = {
                    "msg_type": 5,  # erreur
                    "error_type": "JSONDecodeError",
                    "log": "The JSON sent raised an Exception on the python server..."
                }
                await websocket.send(json.dumps(msg_dict))

    def create_client(self, ticket, username, nb_messages):
        client = WSChatClient(username, nb_messages,ticket)
        self.clients[username]= client
        self.sessions[ticket]=client


    async def main(self):
        async with self.server:
            print("WSChatServer - Starting server...")
            await asyncio.Future()  # run forever

    async def handler_message(self, client: WSChatClient, message: dict):
        """
        Broadcasts the message to all clients.
        """
        message_id = str(uuid.uuid4())  # generate a unique identifier for the message
        msg_type = 2  # set the message type to 2 for a client message
        date_now = datetime.datetime.now()  # current timestamp in milliseconds
        date_now = int(date_now.timestamp())
        # Convert timestamp to datetime object
        date_now = datetime.datetime.fromtimestamp(date_now)

        # Format datetime object as a string
        date_string = date_now.strftime('%Y-%m-%d %H:%M:%S')
        print(date_string)

        # construct the message JSON object
        message_data = {
            "id": message_id,
            "msg_type": msg_type,
            "timestamp": date_string,
            "from": client.username,
            "content": message["content"],
        }
        print(f"Received message from {client.username}: {message['content']}")
        # broadcast the message to all clients
        websockets.broadcast(self.websockets_list, json.dumps(message_data))















