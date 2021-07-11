from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Hash import SHA256
import binascii

# Generate 1024-bit RSA key pair (private + public key)
# keyPair = RSA.generate(bits=1024)
# public_key = keyPair.publickey()

# print(keyPair.exportKey())
# Sign the message using the PKCS#1 v1.5 signature scheme (RSASP1)
# msg = b'Message for RSA signing'
# hash = SHA256.new(msg)
# signer = PKCS115_SigScheme(keyPair)
# signature = signer.sign(hash)

# print("Signature:", binascii.hexlify(signature))

# # Verify valid PKCS#1 v1.5 signature (RSAVP1)
# msg = b'Message for RSA signing'
# hash = SHA256.new(msg)

# verifier = PKCS115_SigScheme(public_key)

# try:
#     verifier.verify(hash, signature)
#     print("Valid")
# except:
#     print("Invalid")


def generate_key_pair():
    return RSA.generate(bits=1024)

def build_private_key(key):
    return RSA.import_key(key)

def build_public_key(key):
    return RSA.import_key(key)

def sign_transaction(tx_encoded, key_pair):
    tx_hash = SHA256.new(tx_encoded)
    signer = PKCS115_SigScheme(key_pair)
    signature = signer.sign(tx_hash)

    return signature

def verify_transaction(tx_encoded, key_pair, signature):
    tx_hash = SHA256.new(tx_encoded)
    public_key = key_pair.publickey()
    verifier = PKCS115_SigScheme(public_key)

    try:
        verifier.verify(tx_hash, signature)
        return True
    except:
        return False


def build_new_wallet(name):
    key_pair = generate_key_pair()

    wallet = {
        'name': name,
        'amount': 500,
        'private_key': key_pair.exportKey().decode()
    }

    return [wallet, key_pair.publickey().exportKey().decode()]
# key_pair = generate_key_pair()

# print(key_pair.publickey().exportKey())