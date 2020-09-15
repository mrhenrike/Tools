import dns.query
import dns.zone
import argparse as ap

def transferZone(dnsserver, domain):
    try:
        return dns.zone.from_xfr(dns.query.xfr(dnsserver, domain))
    except Exception as e:
        print(e)
        return False

if __name__ == '__main__':

    parser = ap.ArgumentParser()
    parser.add_argument('--server', help='O servidor DNS a ser consultado.', required=True)
    parser.add_argument('--domain', help='O domínio a ser usado na consulta.', required=True)
    parsed = parser.parse_args()

    results = transferZone(parsed.server, parsed.domain)

    if not results:
        print(results)
        print('Não foi possível transferir a zona.')
    else:
        for name in results.nodes.keys():
            print(results[name].to_text(name))
