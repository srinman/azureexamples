import socket
import ssl

def start_server():
    HOST = 'localhost'
    PORT = 9443

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='server.crt', keyfile='server.key')
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(cafile='client.crt')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind((HOST, PORT))
        sock.listen(5)

        with context.wrap_socket(sock, server_side=True) as ssock:
            conn, addr = ssock.accept()
            print(f'Connected by {addr}')
            data = conn.recv(1024)
            conn.sendall(data)

if __name__ == '__main__':
    start_server()
