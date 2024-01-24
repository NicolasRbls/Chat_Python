import asyncio
import sys
from aiohttp import web
import aiohttp
import ssl
import secrets
import hashlib
import datetime
import json
from websocket import WSChatServer


routes = web.RouteTableDef()

HTTPS_SERVER_PORT = 8000
runners = []
SESSION_DURATION = 500




def authentication_status(request) -> int:
    print(request.cookies)
    if "session_id" not in request.cookies:
        return 1
    sessions = request.app["sessions"]
    if request.cookies["session_id"] not in sessions:
        return 2
    session = sessions[request.cookies["session_id"]]
    expire_date = datetime.datetime.fromtimestamp(session["expire_date"])
    if expire_date < datetime.datetime.now():
        return 3
    return 0




async def main():
    loop = asyncio.get_event_loop()

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("cert.pem")

    http_app = web.Application()
    http_app.add_routes(routes)
    http_app["sessions"] = {}
    http_app["userbase"] = {}
    ws_server = WSChatServer(8001, context=context)
    http_app["WS_server"] = ws_server

    try:
        http_task = loop.create_task(start_application(http_app, HTTPS_SERVER_PORT, context))
        ws_task = loop.create_task(ws_server.main())
        await asyncio.gather(http_task, ws_task)
    except KeyboardInterrupt as e:
        print(e)


async def start_application(app, port, ssl_context, addr="localhost"):
    runner = web.AppRunner(app)
    runners.append(runner)
    await runner.setup()
    site = web.TCPSite(runner, addr, port, ssl_context=ssl_context)
    print(site)
    await site.start()
    print("APP started on {}:{}".format(addr, port))
    while True:
        await asyncio.sleep(3600)  # sleep for ever


@routes.get('/')
@routes.get('/accueil_auth.html')
async def main_page(request):
    """
    Called when a user sends a request to localhost:8080.
    :param request: The Request object sent by the user
    :return: The Response instance carrying accueil_auth.html.
    """
    print(request)

    # we send this html file
    html_page = retrieve_document_as_str("accueil_auth.html")
    response = web.Response(text=html_page, content_type="text/html")
    return response


@routes.get('/connexion_chat.js')
async def main_page_js(request):
    """
    Called when a user sends a request to localhost:8080.
    :param request: The Request object sent by the user
    :return: The Response instance carrying accueil_auth.html.
    """
    print(request)
    # we send this html file
    js_file = retrieve_document_as_str("connexion_chat.js")
    return web.Response(text=js_file, content_type="text/javascript")


@routes.get('/page_acc.css')
async def main_page_css(request):
    """
    Called when a user sends a request to localhost:8080.
    :param request: The Request object sent by the user
    :return: The Response instance carrying accueil_auth.html.
    """
    print(request)
    # we send this html file
    css_file = retrieve_document_as_str("page_acc.css")
    return web.Response(text=css_file, content_type="text/css")

@routes.get('/style.css')
async def main_page_css(request):
    """
    Called when a user sends a request to localhost:8080.
    :param request: The Request object sent by the user
    :return: The Response instance carrying accueil_auth.html.
    """
    print(request)
    # we send this html file
    css_file = retrieve_document_as_str("style.css")
    return web.Response(text=css_file, content_type="text/css")


def retrieve_document_as_str(path: str) -> str:
    doc = ""
    with open(path, 'r') as f:
        doc = f.read()
    return doc


@routes.post('/connexion_chat')
async def create_account(request):
    """
    Called when a user wants to create an account.
    :param request: the request holding the credentials in JSON format
    :return: The Response instance carrying accueil_auth.html with the
    answer from the server to the account creation request.
    """
    html_page = retrieve_document_as_str("accueil_auth.html")
    # retrieves the data from the request and parse it to json.
    # may raise an exception
    try:
        account_data = await request.json()
    except json.decoder.JSONDecodeError as e:
        print(e, file=sys.stderr)
        return web.Response(status=400,text=html_page,content_type="text/html")
    if account_data["username"] in request.app["userbase"]:
        print("user already exists")
        return web.Response(status=400,text=html_page,content_type="text/html")

    request.app["userbase"][account_data["username"]] = account_data
    response = web.Response(status=200, text=html_page, content_type="text/html")

    return response


@routes.post('/authenticate')
async def connexion_chat(request):
    html_page = retrieve_document_as_str("accueil_auth.html")
    try:
        login_data = await request.json()
    except json.decoder.JSONDecodeError as e:
        print(e, file=sys.stderr)
        return web.Response(status=400,text=html_page,content_type="text/html")
    user = login_data.get("username")
    password = login_data.get("password")

    userbase = request.app["userbase"]
    if user not in userbase:
        print("user does not exist")
        return web.Response(status=400, text=html_page, content_type="text/html")

    hashed_password = userbase[user]["password"]
    if hashed_password != password:
        print("incorrect password")
        return web.Response(status=400, text=html_page, content_type="text/html")

    session_id = secrets.token_hex(16)
    expiration_datetime = datetime.datetime.now() + datetime.timedelta(seconds=SESSION_DURATION)
    expiration_time = datetime.datetime.timestamp(expiration_datetime)
    session = {
        "username": user,
        "expire_date": expiration_time,
    }
    response = web.Response(text=html_page, content_type="text/html")
    response.set_cookie("session_id",
                        session_id,
                        max_age=SESSION_DURATION,
                        httponly=True,
                        secure=True)
    request.app["sessions"][session_id] = session
    print(request.app["sessions"])

    return response



@routes.get('/member_page.html')
async def member_page(request):
    """
    Called when a user sends a request to localhost:8080.
    :param request: The Request object sent by the user
    :return: The Response instance carrying member_page.html.
    """
    print(request)
    # we send this html file
    html_page = retrieve_document_as_str("member_page.html")
    html_page2 = retrieve_document_as_str("accueil_auth.html")
    if authentication_status(request)!=0:
        print("Error")
        print(authentication_status(request))
        return web.Response(status=400, text=html_page2, content_type="text/html")
    return web.Response(status=200, text=html_page, content_type="text/html")
        #marche pas faut demander


@routes.get('/ws_client_uncomplete.js')
async def chat_page_js(request):
    """
    Called when a user sends a request to localhost:8080.
    :param request: The Request object sent by the user
    :return: The Response instance carrying accueil_auth.html.
    """
    print(request)
    # we send this html file
    js_file = retrieve_document_as_str("ws_client_uncomplete.js")
    return web.Response(text=js_file, content_type="text/javascript")

@routes.get("/get_ws_ticket")
async def ask_ws_ticket(request):
    print(request)
    auth = authentication_status(request)
    data_dict = {"result": auth}
    if auth != 0:
        return web.Response(status=401)
    token = request.cookies["session_id"]
    print(token)
    ticket = secrets.token_hex(16)
    client_username = request.app["sessions"][token]["username"]
    #nb_message = request.app["usernase"][client_username]["nb_message"]
    request.app["WS_server"].create_client(ticket,client_username,0)

    data_dict["username"]=client_username
    data_dict["ticket"]=ticket
    data_dict["nb_messages"]=0

    data_json = json.dumps(data_dict)
    return web.Response(status=200,
                        text=data_json,
                        content_type="application/json")


asyncio.run(main())

