"""
Client part
"""

import socket
import threading
from time import sleep
# from math import gcd # unused

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
        self.secret_key = None

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

        self.s.send(self.username.encode("utf-8"))
        sleep(0.1)

        # create key pairs
        p, q = 61, 53 # better to choose bigger
        n = p * q
        phi = (p - 1) * (q - 1)
        e = 17
        d = extended_gcd(e, phi)[1] % phi

        # exchange public keys
        self.s.send(f"{e},{n}".encode("utf-8"))

        # receive the encrypted secret key
        data = self.s.recv(1024).decode("utf-8")
        print("\nReceived secret key:", data)
        self.secret_key = pow(int(data), d, n)

        message_handler = threading.Thread(target = self.read_handler, args = ())
        message_handler.start()
        input_handler = threading.Thread(target = self.write_handler, args = ())
        input_handler.start()

    def read_handler(self):

        """
        Decrypt and read
        """

        while True:
            message = self.s.recv(1024).decode("utf-8") # latin-1

            if not message:
                break

            # decrypt message with the secret key
            decrypted = "".join(chr(ord(ch) ^ self.secret_key) for ch in message)
            # \r moves cursor to start of line
            print(f"\r{decrypted}")
            print(f"{self.username}: ", end = "", flush = True)

    def write_handler(self):

        """
        Encrypt and send
        """

        while True:
            message = input()
            full = f"{self.username}: {message}"
            # encrypt message with the secrete key
            encrypted = "".join(chr(ord(ch) ^ self.secret_key) for ch in full)
            self.s.send(encrypted.encode("utf-8")) # latin-1

if __name__ == "__main__":
    name = input("Enter your username: ")
    cl = Client("127.0.0.1", 9001, name) # "a"
    cl.init_connection()
