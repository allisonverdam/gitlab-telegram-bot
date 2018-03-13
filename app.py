	#!/usr/bin/env python3

import json
from flask import Flask
from flask import request
from flask import jsonify
from bot import Bot
from chat import Chat
import schedule
from datetime import datetime
app = Flask(__name__)

class GitlabBot(Bot):
    def __init__(self):
        super(GitlabBot, self).__init__()
        self.chats = []
        try:
            chats = open('chats', 'r').read()
            self.chats = json.loads(chats)
        except:
            open('chats', 'w').write(json.dumps(self.chats))

        #self.send_to_all('Olá.')

    def text_recv(self, txt, chatid):
        ''' registering chats '''
        txt = txt.strip()
        if txt.startswith('/'):
            txt = txt[1:]
        if txt == 'conectar':
            if len(self.chats) == 0:
                self.reply(chatid, "\U0001F60E  Pronto, agora você recebera as notificações!")
                self.chats.append(json.dumps(Chat(True,chatid).__dict__))
                open('chats', 'w').write(json.dumps(self.chats))
            else:
                achou = False
                for i in range(len(self.chats)):
                    if chatid == json.loads(self.chats[i])['chatid'] and json.loads(self.chats[i])['enviarMensagens'] == True:
                        achou = True
                        self.reply(chatid, "\U0001F60E  Você ja esta recendo as notificações.")
                        break
                    elif chatid == json.loads(self.chats[i])['chatid'] and json.loads(self.chats[i])['enviarMensagens'] == False:
                        achou = True
                        self.reply(chatid, "\U0001F60E  Pronto, agora você recebera as notificações!")
                        temp = json.loads(self.chats[i])
                        temp['enviarMensagens'] = True
                        self.chats[i] = json.dumps(temp)
                        open('chats', 'w').write(json.dumps(self.chats))
                        break
                if achou == False:
                    self.reply(chatid, "\U0001F60E  Pronto, agora você recebera as notificações!")
                    self.chats.append(json.dumps(Chat(True,chatid).__dict__))
                    open('chats', 'w').write(json.dumps(self.chats))
        elif txt == 'sair':
            achou = False
            for i in range(len(self.chats)):
                if chatid == json.loads(self.chats[i])['chatid'] and json.loads(self.chats[i])['enviarMensagens'] == True:
                    achou = True
                    self.reply(chatid, "\U0001F63F Ok, estou aqui caso precise.")
                    temp = json.loads(self.chats[i])
                    temp['enviarMensagens'] = False
                    self.chats[i] = json.dumps(temp)
                    open('chats', 'w').write(json.dumps(self.chats))
                    break
            if achou == False:
                self.reply(chatid, 'Você não está inscrito em nenhum projeto.')
        else:
            self.reply(chatid, "\U0001F612 Não tenho nada a dizer.")

    def send_to_all(self, msg):
        for c in self.chats:
            self.reply(json.loads(c)['chatid'], msg)

b = GitlabBot()

def daily():
    weekDay=datetime.today().weekday()
    if(weekDay == 5 or weekDay == 6):
        return
    b.send_to_all("HORA DA DAILY!!! \U0001F554 \U0001F64B 🙋‍♂️")

schedule.every().day.at("17:00").do(daily)


@app.route("/", methods=['GET', 'POST'])
def webhook():
    data = request.json
    # json contains an attribute that differenciates between the types, see
    # https://docs.gitlab.com/ce/user/project/integrations/webhooks.html
    # for more infos
    kind = data['object_kind']
    if kind == 'push':
        msg = generatePushMsg(data)
    elif kind == 'tag_push':
        msg = generatePushMsg(data)  # TODO:Make own function for this
    elif kind == 'issue':
        msg = generateIssueMsg(data)
    elif kind == 'note':
        msg = generateCommentMsg(data)
    elif kind == 'merge_request':
        msg = generateMergeRequestMsg(data)
    elif kind == 'wiki_page':
        msg = generateWikiMsg(data)
    elif kind == 'pipeline':
        msg = generatePipelineMsg(data)
    elif kind == 'build':
        msg = generateBuildMsg(data)
    b.send_to_all(msg)
    return jsonify({'status': 'ok'})


def generatePushMsg(data):
    if data['total_commits_count'] == 0:
        return
    msg = '*{0} ({1}) - {2} novos commits*\n'\
        .format(data['project']['name'], data['project']['default_branch'], data['total_commits_count'])
    msg = msg + 'Autor: {0} \n'.format(data['user_name'])
    for commit in data['commits']:
        msg = msg + '----------------------------------------------------------------\n'
        msg = msg + commit['message'].rstrip()
        msg = msg + '\n' + commit['url'].replace("_", "\_") + '\n'
    msg = msg + '----------------------------------------------------------------\n'
    return msg


def generateIssueMsg(data):
    action = data['object_attributes']['action']
    if action == 'open':
        msg = '*{0} nova Issue para {1}*\n'\
            .format(data['project']['name'], data['assignee']['name'])
    elif action == 'close':
        msg = '*{0} Issue fechada por {1}*\n'\
            .format(data['project']['name'], data['user']['name'])
    msg = msg + '*{0}*'.format(data['object_attributes']['title'])
    msg = msg + 'see {0} for further details'.format(data['object_attributes']['url'])
    return msg


def generateCommentMsg(data):
    ntype = data['object_attributes']['noteable_type']
    if ntype == 'Commit':
        return
    elif ntype == 'MergeRequest':
        msg = 'note to MergeRequest'
    elif ntype == 'Issue':
        msg = 'note to Issue'
    elif ntype == 'Snippet':
        msg = 'note on code snippet'
    return msg


def generateMergeRequestMsg(data):
    return 'new MergeRequest'


def generateWikiMsg(data):
    return 'new wiki stuff'


def generatePipelineMsg(data):
    return 'new pipeline stuff'


def generateBuildMsg(data):
    return 'new build stuff'

def generateCommitMsg(data):
    msg = '*{0} ({1}) - novo commit: *'.format(data['project']['name'], data['project']['default_branch'])
    msg = msg + '\n Mensagem: {0}'.format(data['commit']['message'])
    msg = msg + '\n Commit feito por: {0}'.format(data['commit']['author']['name'])
    msg = msg + '\n Criado em: {0}'.format(data['commit']['timestamp'])
    msg = msg + '\n' + data['commit']['url'].replace("_", "\_") + '\n'
    msg = msg + '----------------------------------------------------------------\n'
    return msg

if __name__ == "__main__":
    b.run_threaded()
    app.run(host='0.0.0.0', port=10111)
