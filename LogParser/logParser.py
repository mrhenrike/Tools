import argparse as ap
import os
import re
from collections import Counter

def statistics(resultsList):
    length = len(resultsList)
    count = Counter(resultsList)
    freq = count.most_common(len(count))

    return length, freq

def parseLog(file, compiledfilters):
    results = {}

    for pattern, regex in compiledfilters.items():
        results[pattern] = [x.group() for x in re.finditer(regex, file)]
        
    return results


if __name__ == '__main__':
    parser = ap.ArgumentParser(description='Um parser de logs simples que busca múltiplos padrões.')
    pathfiles = parser.add_mutually_exclusive_group(required=True)
    pathfiles.add_argument(
        '-f', '--files', nargs='+', help='O caminho do(s) arquivo(s) a serem pesquisados.')
    pathfiles.add_argument('-r', '--recursive', help='Uma pasta para buscar recursivamente todos os arquivos.')
    parser.add_argument(
        '-p',
        '--patterns',
        nargs='+',
        choices=['phone', 'date_mda', 'date_dma', 'email', 
                 'ipaddr', 'macaddr', 'card', 'url', 'fullurl', 
                 'uuid', 'md5', 'sha1', 'hexstring'],
        help='Um ou mais padrões separados por espaço.',
        required=True)
    parser.add_argument(
        '-s', '--stats', help='Mostrar estatísticas.', action='store_true')
    parser.add_argument(
        '-o', '--output', help='Salvar os resultados em arquivos.', action='store_true')
    args = parser.parse_args()

    if args.files:
        files = args.files
    elif args.recursive:
        if not os.path.isdir(args.recursive):
            raise FileNotFoundError(f'O diretório {args.recursive} é inválido.')

        files = []
        for root, directories, filenames in os.walk(args.recursive):
            for file in filenames:
                files.append(os.path.join(root, file))

    filters = {
        'phone'     : '(\+?\d{,3})? ?(\(\d{,3}\))? ?\d{4,5}[ -]?\d{4}',
        'date_mda'  : '\d{1,2}[/-](\d{1,2}|\w{3})[/-]\d{2,4}',
        'date_dma'  : '(\d{1,2}|\w{3})[/-]\d{1,2}[/-]\d{2,4}',
        'email'     : '[a-z0-9_.]+@[a-z0-9]+\.[a-z0-9]{2,}(\.[a-z0-9]+)?',
        'ipaddr'    : '(((1\d|[1-9])?\d|2([0-4]\d|5[0-5]))\.){3}((1\d|[1-9])?\d|2([0-4]\d|5[0-5]))',
        'card'      : '(\d{4}[ -]?){3}\d{4}',
        'url'       : 'https?://[a-z0-9A-Z._?&=-]+',
        'fullurl'   : 'https?://[a-z0-9A-Z._?&=/%-]+',
        'macaddr'   : '([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}',
        'uuid'      : '[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}',
        'md5'       : '[a-fA-F0-9]{32}',
        'sha1'      : '[a-fA-F0-9]{40}',
        'hexstring' : '[a-fA-F0-9]{10,}',
    }
    
    compiledfilters = dict((pattern, re.compile(filters[pattern])) for pattern in args.patterns)

    for file in files:
        try:
            results = parseLog(open(file, 'rb').read().decode('latin'), compiledfilters)
        except Exception as e:
            raise e
        print(f'\n====================\n{file}\n====================\n')
        
        for pattern, result in results.items():
            if len(result) == 0:
                print('Sem resultados.')
                continue
            print('\n'+pattern)
            if args.stats:
                length, freq = statistics(result)
                print(f'Total de {length} itens encontrados.')
                for item in freq:
                    print(f'{item[0]}: {item[1]} - {round((item[1]/length)*100, 2)}%')
            else:
                for item in sorted(set(result)):
                    print(item)

            if args.output:
                with open(f'{file}-{pattern}.txt','a') as outfile:
                    for item in set(result):
                        outfile.write(item+'\n')
