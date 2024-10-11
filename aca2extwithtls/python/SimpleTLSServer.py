from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl

class SimpleHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Hello, TLS!')
        self.wfile.flush()  # Ensure the response is flushed

def run(server_class=HTTPServer, handler_class=SimpleHandler):
    server_address = ('', 443)
    httpd = server_class(server_address, handler_class)
    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   server_side=True,
                                   certfile='/etc/tls/tls.crt',
                                   keyfile='/etc/tls/tls.key',
                                   ssl_version=ssl.PROTOCOL_TLS)
    print('Starting server on port 443...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()