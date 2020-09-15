import threading as th
import queue
import argparse as ap
import requests as r

from requests.packages.urllib3.exceptions import InsecureRequestWarning
r.packages.urllib3.disable_warnings(InsecureRequestWarning)


def loadList(file):
    
    wordqueue = queue.Queue()

    for word in file.readlines():
        wordqueue.put(word.strip())
    return wordqueue

def bruter(wordqueue, extentions, url, statuscodes, feedback):
    while not wordqueue.empty():
        attempt = wordqueue.get()
        attemptlist = []

        if '.' not in attempt:
            attemptlist.append(f'/{attempt}/')
        else:
            attemptlist.append(f'/{attempt}')

        if extentions:
            for ext in extentions:
                attemptlist.append(f'/{attempt}.{ext}')

        for item in attemptlist:
            testurl = url+item
            itemlen = len(item)
            try:
                resp = r.get(testurl, verify=False, allow_redirects=False)
                text = resp.text
                status = resp.status_code
                if status in statuscodes:
                    if feedback and feedback in text:
                        continue
                    print(f'[+] {status} ==> {item}')
                    if 'Index of /' in resp.text:
                        print(f'\r[+] Listagem de diretórios habilitada em {item}')
                    
            except KeyboardInterrupt:
                print('Tarefa cancelada pelo usuário...')
                exit(0)
            except ConnectionError:
                print('Erro de conexão...')
            except Exception as e:
                print(e)
        wordqueue.task_done()

if __name__ == '__main__':
    parser = ap.ArgumentParser(description="Enumeração de arquivos e diretórios.")
    parser.add_argument('-u', '--url', 
        help='A URL a ser testada.', required=True)
    parser.add_argument('-w', '--wordlist', type=ap.FileType(mode='r'),
        help='Um arquivo contendo diretórios/arquivos para testar.', required=True)
    parser.add_argument('-t', '--threads', default=1, type=int, 
        help='O número de threads. O padrão é 1.')
    parser.add_argument('-e', '--extensions', nargs='+',
        help='Extensões a serem testadas, separadas por espaço.')
    codegroup = parser.add_mutually_exclusive_group()
    codegroup.add_argument('--show', nargs='+', type=int,
        help='Códigos HTTP a serem mostrados, separados por espaço.')
    codegroup.add_argument('--hide', nargs='+', type=int,
        help='Códigos HTTP a serem excluídos, separados por espaço.')
    parser.add_argument( '-fb', '--feedback', 
        help='''Se o programa está recebendo 200 para todas as requisições, 
        considere passar uma string que está contida na página de retorno.
        Assim, ele saberá se a resposta é um 404 com redirecionamento para 200.''')
    args = parser.parse_args()

    if not args.url.startswith('http'):
        args.url = 'http://'+args.url

    statuscodes = {200,301,302,401,403,405}
    if args.show:
        statuscodes = statuscodes.union(args.show)
    elif args.hide:
        statuscodes = statuscodes.difference(args.hide)

    wordqueue = loadList(args.wordlist)
    
    for _ in range(args.threads):
        th.Thread(target=bruter, 
            args=(wordqueue,args.extensions,args.url, statuscodes, args.feedback)).start()

    wordqueue.join()