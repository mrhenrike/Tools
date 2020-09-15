import threading
import argparse as ap
from colorama import init
import queue
from socket import gethostbyname
from termcolor import colored

def loadSearch(subfile, domain):
	subqueue = queue.Queue()
	
	[subqueue.put(sub.strip()+'.'+domain) for sub in subfile.readlines()]
	return subqueue



def subDomainSearch():

	while not workqueue.empty():
		addr = workqueue.get()
		try:
			hostip = gethostbyname(addr)
			print(colored('[+]','green') + f' Subdomínio encontrado!! {addr} com endereço IP: {hostip}.')
			domainsfound.append((addr,hostip))
		except:
			print(colored('[-]','red') + f' Subdomínio {addr} não encontrado.')
		workqueue.task_done()

if __name__ == '__main__':

	parser = ap.ArgumentParser(description="Enumeração de subdomínios.")
	parser.add_argument('-d', '--domain', 
		help='O domínio a ser testado.', 
		required=True)
	parser.add_argument('-w', '--wordlist', 
		type=ap.FileType(mode='r'), 
		help='Um arquivo contendo subdomínios a serem usados.', 
		required=True)
	parser.add_argument('-t', '--threads', 
		help='O número de threads a serem usadas. Padrão é 1.',
		default=1, 
		type=int)
	parser.add_argument('-o', '--output', 
		type=ap.FileType(mode='w'), 
		help='Arquivo para salvar os resultados.')
	args = parser.parse_args()

	init()
	workqueue = loadSearch(args.wordlist, args.domain)
	domainsfound = []

	for _ in range(args.threads):
		threading.Thread(target=subDomainSearch).start()

	workqueue.join()

	print('\n#################################################\n')
	print(f'Encontrados um total de {len(domainsfound)} subdomínios.\n')

	if args.output:
		args.output.write('sub domain,ip address\n')
		for item in domainsfound:
			args.output.write(f'{item[0]},{item[1]}\n')
		print(f'Lista de subdomínios salva em {args.output.name}')
	else:
		for item in domainsfound:
			print(f'{item[0]},{item[1]}')