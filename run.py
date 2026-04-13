"""
For manual testing
"""

from math import gcd
from time import time

def extended_gcd(a: int, b: int) -> tuple[int]:

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

p, q = 7043, 5483 # big prime numbers
N = p * q # public key modulo part
E = 17 # public key exponential part
R = (p - 1) * (q - 1) # phi(N)

assert 0 < E < R, "Number 'e' does not satisfy the inequality"
assert gcd(E, R) == 1, "Number 'e' is not coprime with phi(n)" # it is faster to use math.gcd()

D = extended_gcd(E, R)[1] % R # private key for decrypting

while True:
    # print(f"\nPublic key 'n': {N}\nPublic key 'e': {E}\n")
    # msg = input("Enter your message:\n>>> ") # A-Z capital letters only
    # # M = int("".join([str(ord(ch)) for ch in msg]))
    # M = int.from_bytes(msg.encode("utf-8"), "big")
    # print(f"\nMessage transform: {M}\n")

    # C = pow(M, E, N)
    # print(f"\nEncrypted number: {C}")

    # # decrypt, possible only for receiver
    # M_ = pow(C, D, N)
    # print(f"Encrypted message: {M_.to_bytes((M_.bit_length() + 7) // 8, "big").decode("utf-8")}")

    print(f"\nPublic key 'n': {N}\nPublic key 'e': {E}\n")
    msg = input("Enter your message:\n>>> ")
    start = time()
    # break the string into 3-byte chunks to ensure M < N
    raw_bytes = msg.encode("utf-8")
    encrypted = []

    for i in range(0, len(raw_bytes), 3):
        chunk = raw_bytes[i:i + 3]
        M = int.from_bytes(chunk, "big")

        # M is always less than N
        assert M < N, "Chunk too large!"

        C = pow(M, E, N)
        encrypted.append(C)

    print(f"\nEncrypted sequence: {encrypted}\n")

    # decryption
    decrypted = bytearray()
    for C in encrypted:
        M_ = pow(C, D, N)
        # Convert back to bytes (3 bytes max)
        decrypted.extend(M_.to_bytes((M_.bit_length() + 7) // 8, "big"))

    print(f"Decrypted message: {decrypted.decode('utf-8')}\n")
    end = time()
    print(f"====================\nTime spent: {(end - start):.5f}s\n====================\n")
