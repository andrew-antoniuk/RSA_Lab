"""
Server part
"""

import socket
import threading
from random import randint
from time import sleep

class Server:

    """
    Server
    """

    def __init__(self, port: int) -> None:
        self.host = "127.0.0.1"
        self.port = port
        self.clients = []
        self.username_lookup = {}
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        self.secret_key = None # filler
        self.public_keys = {}

    def start(self):

        """
        Start exchanging
        """

        self.s.bind((self.host, self.port))
        self.s.listen(100)

        # generate keys ...
        self.secret_key = randint(1, 255)

        while True:
            c, addr = self.s.accept()

            username = c.recv(1024).decode("utf-8")
            print(f"{username} tries to connect")

            self.username_lookup[c] = username
            self.clients.append(c)

            # receive public key
            public_key_data = c.recv(1024).decode("utf-8")
            e, n = map(int, public_key_data.split(","))
            self.public_keys[c] = (e, n)

            # encrypt the secret with the clients public key
            encrypted = pow(self.secret_key, e, n)

            # send the encrypted secret to a client
            c.send(str(encrypted).encode("utf-8"))

            sleep(0.1)
            self.broadcast(f"new person has joined: {username}")

            threading.Thread(target = self.handle_client, args = (c, addr,)).start()

    def broadcast(self, msg: str):

        """
        Connection with clients
        """

        for client in self.clients:

            # encrypt the message
            try:
                encrypted_msg = "".join(chr(ord(ch) ^ self.secret_key) for ch in msg)
                client.send(encrypted_msg.encode("utf-8")) # latin-1
            except Exception:
                self.clients.remove(client)

    def handle_client(self, c: socket, addr):

        """
        Send to the client
        """

        while True:
            msg = c.recv(1024)

            for client in self.clients:
                if client != c:
                    client.send(msg)

if __name__ == "__main__":
    s = Server(9001)
    s.start()
