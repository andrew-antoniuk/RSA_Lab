import socket
import threading
from time import sleep

def extended_gcd(a: int, b: int):
    if a == 0:
        return b, 0, 1
    d, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return d, x, y

class Client:
    def __init__(self, server_ip: str, port: int, username: str) -> None:
        self.server_ip = server_ip
        self.port = port
        self.username = username
        self.secret_key = None

    def init_connection(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((self.server_ip, self.port))
        except Exception as e:
            print("[client]: could not connect to server: ", e)
            return

        # Handshake step 1: Send Username
        self.s.send(self.username.encode('utf-8'))
        sleep(0.1) # Prevent message gluing

        # Handshake step 2: Generate and send RSA Public Key
        p, q = 61, 53
        n = p * q
        phi = (p - 1) * (q - 1)
        e = 17
        d = extended_gcd(e, phi)[1] % phi
        self.s.send(f"{e},{n}".encode('utf-8'))

        # Handshake step 3: Receive and decrypt the XOR Secret Key
        data = self.s.recv(1024).decode('utf-8')
        self.secret_key = pow(int(data), d, n)
        print(f"System: Connection established. Secret key decrypted.")

        threading.Thread(target=self.read_handler, daemon=True).start()
        self.write_handler()

    def read_handler(self):
        while True:
            try:
                # Use latin-1 to receive XORed data
                message = self.s.recv(1024).decode('latin-1')
                if not message: break
                decrypted = "".join(chr(ord(ch) ^ self.secret_key) for ch in message)
                print(f"\n{decrypted}")
            except Exception as e:
                print(f"Error reading: {e}")
                break

    def write_handler(self):
        while True:
            msg_content = input(f"{self.username} > ")
            full_message = f"{self.username}: {msg_content}"
            encrypted = "".join(chr(ord(ch) ^ self.secret_key) for ch in full_message)
            self.s.send(encrypted.encode('latin-1'))

if __name__ == "__main__":
    name = input("Enter your username: ")
    cl = Client("127.0.0.1", 9001, name)
    cl.init_connection()
