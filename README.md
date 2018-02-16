# gitlab webhook telegram bot

Simple gitlab telegram bot that listen to gitlab webhooks and send each event
to the authenticated chats

https://core.telegram.org/bots

Create a new bot https://core.telegram.org/bots#create-a-new-bot
and then copy the token to the token file.

# Requirements 
Only work with python3

# How to use

1. Run the app.py in your server
1. Create a webhook in your gitlab project that points to
   http://yourserver:10111/
1. Digite "conectar" para começar a receber as mensagens
1. You will receive each event in your repo

# FAQ

## Q. How can I stop receiving messages
R. Digite /sair para parar de receber as notificações

## Q. How can I enable the bot in group chats
R. Digite /conectar ao invés de conectar, todos os comandos quando executados em grupos tem que ser precedidos de "/"

# Interesting files

 * chats, the json with all the chats to send notifications
 * token, the bot token
 * offset, the last msg id received from telegram api
