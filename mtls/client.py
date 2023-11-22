import socket
import ssl

def connect_to_server():
    HOST = 'localhost'
    PORT = 9443

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_cert_chain(certfile='client.crt', keyfile='client.key')
    context.load_verify_locations(cafile='server.crt')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        with context.wrap_socket(sock, server_hostname=HOST) as ssock:
            ssock.connect((HOST, PORT))
            ssock.sendall(b'Hello, world')
            data = ssock.recv(1024)

    print(repr(data))

if __name__ == '__main__':
    connect_to_server()
