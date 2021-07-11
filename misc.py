import ecdsa
import json
import base64

encode = lambda transaction: json.dumps(transaction, sort_keys=True).encode()

def hash_tx(tx):
    hashBytes = hashlib.sha256(encode(tx)).digest()

    return hashBytes


def generate_ECDSA_keys():
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    private_key = sk.to_string().hex()

    vk = sk.get_verifying_key()
    public_key = vk.to_string().hex()
    
    public_key = base64.b64encode(bytes.fromhex(public_key))

    

    return [private_key, public_key]

tx = {
    'sender': 'Chris',
    'receiver': 'Dan',
    'amount': 500
}


[private_key, public_key] = generate_ECDSA_keys()

# print('Private Key:', private_key)


# print('Public Key:', public_key)

wallet = {
    'address': public_key,
    'private_key': private_key,
}

def sign_tx(private_key, tx):

    encoded_tx = encode(tx)

    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
    signature = base64.b64encode(sk.sign(encoded_tx))

    return signature

# print(sign_tx(private_key, tx))

tx["sig"] = sign_tx(private_key, tx)

print(tx["sig"])