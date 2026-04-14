import socket
import threading
from random import randint
from time import sleep

class Server:
    def __init__(self, port: int) -> None:
        self.host = "127.0.0.1"
        self.port = port
        self.clients = []
        self.username_lookup = {}
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.secret_key = None
        self.public_keys = {}

    def start(self):

        self.s.bind((self.host, self.port))
        self.s.listen(100)
        self.secret_key = randint(1, 255)
        print(f"Server started on {self.port}. Secret Key: {self.secret_key}")

        while True:
            c, addr = self.s.accept()

            # Use a small timeout or clear separation for the handshake
            username = c.recv(1024).decode('utf-8')
            print(f"{username} tries to connect")

            self.username_lookup[c] = username
            self.clients.append(c)

            # Receive public key
            public_key_data = c.recv(1024).decode('utf-8')
            e, n = map(int, public_key_data.split(","))
            self.public_keys[c] = (e, n)

            # Encrypt the secret with the client's public key
            encrypted_secret = pow(self.secret_key, e, n)
            c.send(str(encrypted_secret).encode('utf-8'))

            # Wait a moment for client threads to start before broadcasting
            sleep(0.1)
            self.broadcast(f"*** {username} has joined the chat ***")

            threading.Thread(target=self.handle_client, args=(c, addr,)).start()

    def broadcast(self, msg: str):
        for client in self.clients:
            try:
                # Use latin-1 for XORed data to avoid UnicodeDecodeErrors
                encrypted_msg = "".join(chr(ord(ch) ^ self.secret_key) for ch in msg)
                client.send(encrypted_msg.encode('latin-1'))
            except:
                self.clients.remove(client)

    def handle_client(self, c: socket, addr):
        while True:
            try:
                # Receive raw bytes and relay to others
                msg_bytes = c.recv(1024)
                if not msg_bytes: break

                for client in self.clients:
                    if client != c:
                        client.send(msg_bytes)
            except:
                break
        c.close()

if __name__ == "__main__":
    s = Server(9001)
    s.start()
