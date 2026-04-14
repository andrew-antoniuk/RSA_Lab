"""
Client part
"""

import socket
import threading
from math import gcd # unused

def extended_gcd(a: int, b: int):

    """
    Recursive implementation of extended Euclidean Algorithm.
    Computes gcd as well as coefficients of linear that gcd representation
    """

    if a == 0: # recursive part
        return b, 0, 1

    # compute gcd and linear coeffs
    d, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1

    return d, x, y

class Client:

    """
    Client
    """

    def __init__(self, server_ip: str, port: int, username: str) -> None:
        self.server_ip = server_ip
        self.port = port
        self.username = username

    def init_connection(self):

        """
        Connect with server
        """

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((self.server_ip, self.port))
        except Exception as e:
            print("[client]: could not connect to server: ", e)
            return

        self.s.send(self.username.encode())

        # create key pairs
        p, q = 61, 53 # better to choose bigger
        n = p * q
        phi = (p - 1) * (q - 1)
        e = 17
        d = extended_gcd(e, phi)[1] % phi

        # keys
        self.public_key = (e, n)
        self.private_key = (d, n)

        # exchange public keys
        self.s.send(f"{e},{n}".encode())

        # receive the encrypted secret key
        data = self.s.recv(1024).decode()
        print("Received secret:", data)
        encrypted = int(data)
        self.secret_key = pow(encrypted, d, n)

        message_handler = threading.Thread(target = self.read_handler, args = ())
        message_handler.start()
        input_handler = threading.Thread(target = self.write_handler, args = ())
        input_handler.start()

    def read_handler(self):

        """
        Decrypt and read
        """

        while True:
            message = self.s.recv(1024).decode()

            # decrypt message with the secrete key
            decrypted = "".join(chr(ord(ch) ^ self.secret_key) for ch in message)
            print(decrypted)

    def write_handler(self):

        """
        Encrypt and send
        """

        while True:
            message = f"{self.username}: {input()}"

            # encrypt message with the secrete key
            encrypted = "".join(chr(ord(ch) ^ self.secret_key) for ch in message)
            self.s.send(encrypted.encode())

if __name__ == "__main__":
    cl = Client("127.0.0.1", 9001, "a")
    cl.init_connection()
