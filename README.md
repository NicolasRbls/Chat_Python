# Chat_Python
##Description du Projet Chat Python/JS
Ce projet est un système de chat en temps réel utilisant Python et JavaScript. Il intègre des WebSockets pour une communication bidirectionnelle entre le serveur et les clients. La partie backend est écrite en Python avec aiohttp et gère l'authentification des utilisateurs, les sessions, et les communications WebSocket. Le frontend, écrit en JavaScript, permet aux utilisateurs de se connecter, de s'authentifier et d'envoyer/recevoir des messages dans une interface web.

##Comment Utiliser
-Configuration : Assurez-vous d'avoir Python installé avec les modules aiohttp et websockets.
-Lancement du Serveur : Exécutez le script serveur Python. Il démarre un serveur HTTPS sur le port 8000 et un serveur WebSocket sur le port 8001.
-Interface Web : Ouvrez votre navigateur et accédez à localhost:8000 pour interagir avec l'interface de chat.
-Connexion et Chat : Créez un compte ou connectez-vous, puis utilisez la fenêtre de chat pour envoyer et recevoir des messages.
