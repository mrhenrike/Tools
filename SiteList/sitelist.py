import requests as r
from bs4 import BeautifulSoup as bs
import argparse as ap
from requests.packages.urllib3.exceptions import InsecureRequestWarning
r.packages.urllib3.disable_warnings(InsecureRequestWarning)


def wordListGen(url,minlen,depth,leet):
    try:
        req = r.get(url, verify=False)
    except:
        print('Não foi possível conectar em '+url+'. Verifique a URL e a conexão.')
        exit(1)
    html = req.text
    soup = bs(html, 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text()
    words = set()
    for word in text.split():
        if len(word) >= minlen:
            words.add(word.strip('.,:!;"?@#$%&*()\n'))
    if depth > 0:
        depth -= 1
        for link in set(soup.find_all('a')):
            if link.get('href').startswith('http'):
                continue
            words2 = wordListGen(url+'/'+link.get('href'),minlen,depth,leet)
            if words2 != None:
                words = words.union(words2)
    if leet:
        words = words.union(leetMode(words))

    return words

def leetMode(wordlist):
    changes = {'a':'4', 'e':'3', 'o':'0', 'l':'1', 's':'5', 't':'7'}
    for word in wordlist:
        newword = ''
        for char in word:
            if char.lower() in changes.keys():
                    newword += changes[char.lower()]
            else:
                newword += char

        if newword != word:
            yield newword

if __name__ == '__main__':
    parser = ap.ArgumentParser(description="Gera uma wordlist a partir do conteúdo de uma URL.")
    parser.add_argument('-u', '--url', help='O endereço do site alvo.', required=True)
    parser.add_argument('-m', '--minlen', default=4, 
        help='O tamanho mínimo de uma palavra para estar na lista.', type=int)
    parser.add_argument('-d', '--depth', 
        default=1, help='A profundidade máxima de links para coleta.', type=int)
    parser.add_argument('-l', '--leet',  
        help='Gera palavras modificadas usando substituição leet.', action='store_true')
    parser.add_argument('-o', '--output', type=ap.FileType(mode='r'), 
        help='Salva a wordlist em um arquivo.')
    args = parser.parse_args()
    if not any([args.url.startswith('http://'), args.url.startswith('https://')]):
        args.url = 'http://'+args.url

    wordlist = wordListGen(args.url,args.minlen,args.depth,args.leet)

    if args.output:
        
        for word in wordlist:
            args.output.write(word+'\n')
        print(f'Wordlist criada com sucesso em {args.output.name}. {len(wordlist)} palavras foram coletadas.')
    else:
        for word in wordlist:
            print(word)
        print(f'Wordlist criada com sucesso. {len(wordlist)} palavras foram coletadas.')
