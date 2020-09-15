from socket import socket, SOCK_STREAM, AF_INET
import argparse as ap
from threading import Thread
import re
import progressbar as pb
import queue
import ipaddress as ipaddr

def scanner():
    global count

    while not fila.empty():

        ip, port = fila.get().split(':')
        port = int(port)

        try:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((ip,port))
            results[ip][port] = 'open'
        except Exception as e:
            results[ip][port] = 'closed/filtered'
        count +=1
        bar.update(count)
        sock.close()
        fila.task_done()

def handlePorts(ports):
    portlist = set()
    try:
        for port in ports:
            if port.isdigit():
                portlist.add(int(port))
            elif '-' in port:
                firstPort, lastPort = port.split('-')
                [portlist.add(i) for i in range(int(firstPort),int(lastPort)+1)]
            else:
                raise Exception('Incorrect port format!')
        return portlist
    except:
        raise Exception('Incorrect port format!')

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--ip', 
        help='Um único endereço IP.')
    group.add_argument('-f', '--file', type=ap.FileType(mode='r'), 
        help='Um arquivo contendo um IP por linha.')
    parser.add_argument('-p', '--ports', 
        nargs='+', 
        help='''Uma ou mais portas separadas por espaços.
        Intervalos são aceitos: p1 OR or p1 p2 p3-pn p4.''', 
        required=True)
    parser.add_argument('-o', '--open', 
        help='Mostrar apenas as portas abertas.', 
        action='store_true')
    parser.add_argument('-t', '--threads', 
        type=int, 
        default=1, 
        help='Quantidade de threads. O padrão é 1.')
    args = parser.parse_args()

    ports = handlePorts(args.ports)
    fila = queue.Queue()

    if args.ip:
        if '/' in args.ip:
            try:
                network = ipaddr.ip_network(args.ip)
            except ValueError:
                print('Formato CDIR inválido')
                exit(1)
            iplist = []
            for address in network:
                iplist.append(str(address))
        elif re.fullmatch('(((1\d|[1-9])?\d|2([0-4]\d|5[0-5]))\.){3}((1\d|[1-9])?\d|2([0-4]\d|5[0-5]))', ip) is None:
            raise ValueError('Endereço IP inválido!')
        else:
            iplist = [args.ip]
        [fila.put(f'{ip}:{port}') for ip in iplist for port in ports]
    elif args.file:
        iplist = set(args.file.readlines())
        [fila.put(f'{ip.strip()}:{port}') for ip in iplist for port in ports]

    count = 0
    threadsList = []
    results = {}
    for ip in iplist:
        results[ip.strip()] = {}

    try:
        bar = pb.ProgressBar(max_value=fila.qsize())
        for thread in range(args.threads):
            threadsList.append(Thread(target=scanner))
        [t.start() for t in threadsList]
        fila.join()
    except KeyboardInterrupt:
        exit(0)

    for ip in sorted(results.keys()):
        if not 'open' in results[ip].values():
            continue
        print(f'\nHost {ip}')
        for port, state in sorted(results[ip].items()):
            if args.open and state != 'open':
                continue
            print(f'\tPort {port} is {state}!')
