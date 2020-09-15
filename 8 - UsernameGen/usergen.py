import argparse as ap
import unicodedata

def generate(fullname, separators):
    usernames = []
    fullname = unicodedata.normalize('NFKD', fullname).encode('ascii', 'ignore').decode('utf-8')
    names = fullname.lower().split()

    for name in names[:]:
        if len(name) < 4:
            names.remove(name)

    for sep in separators:
        usernames.append(sep.join(names))

        initials = names[0][0]
        for surename in names[1:]:
            initials += surename[0]            
            usernames.append(names[0]+sep+surename)
            usernames.append(names[0][0]+sep+surename)
            usernames.append(names[0]+sep+surename[0])

        usernames.append(names[0]+sep+initials)

    return usernames


if __name__ == '__main__':
    parser = ap.ArgumentParser(description="Gerador de usernames.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-n', '--name', help='Um nome completo entre aspas.')
    group.add_argument('-f', '--file', type=ap.FileType(mode='r'), help='Um arquivo contendo nomes completos.')
    parser.add_argument('-s', '--separators', nargs='+', default=['','.','_'], 
        help='Um ou mais separadores. Cada um deve estar entre aspas. Os padrão são: "","." e "_"')
    parser.add_argument('-o', '--output', help='Optar por salvar em arquivos.', action='store_true')
    args = parser.parse_args()

    if args.name:
        usernames = generate(args.name, args.separators)
        if args.output:
            with open(usernames[0]+'.txt','w') as outfile:
                [outfile.write(username+'\n') for username in usernames]
        else:
            [print(username) for username in usernames]
    elif args.file:
        fullnames = args.file.readlines()
        usernamelist = []
        for fullname in fullnames:
            usernamelist.append(generate(fullname.strip(), args.separators))

        if args.output:
            for userlist in usernamelist:
                with open(userlist[0]+'.txt','w') as outfile:
                    [outfile.write(username+'\n') for username in userlist]
        else:
            for userlist in usernamelist:
                [print(username) for username in userlist]