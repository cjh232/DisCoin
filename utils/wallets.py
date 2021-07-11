import hashlib
import ecdsa
import json
import base64


class Wallet:

    def __init__(self, wallet_dict):
        self.owner = wallet_dict["owner"]
        self.address = wallet_dict["address"]
        self.private_key = wallet_dict["private_key"]

    
    @property
    def amount(self):
        # This function will need to sum all the utxo linked to this wallets address.
        return 5  

    def create_transaction(self, out_addr, amount):

        tx = {
            'sender': self.address.decode(),
            'receiver': out_addr,
            'amount': amount
        }

        tx['sig'] = self.sign_transaction(tx)

        return tx

    def sign_transaction(self, tx):

        enc_tx = self.encode(tx)

        # When the key pair is created we convert the private key to hex. from_string requires
        # a byte string so we need to make the conversion. Otherwise we will get a malformed
        # key error thrown.

        sk = ecdsa.SigningKey.from_string(bytes.fromhex(self.private_key), curve=ecdsa.SECP256k1)

        signature = base64.b64encode(sk.sign(enc_tx, hashfunc=hashlib.sha256))

        return signature
        
    def verify_transaction(self, tx):
        # When the key pair is created we encode the public key in base64 to create a shorter
        # key. Before reconstructing, using from_string(), we must decode it. Otherwise we will get
        # a malformed key error thrown.

        vk = ecdsa.VerifyingKey.from_string(base64.b64decode(self.address), curve=ecdsa.SECP256k1)

        tx_headers = {'sender': tx['sender'], 'receiver': tx['receiver'], 'amount': tx['amount']}

        is_valid = vk.verify(base64.b64decode(tx['sig']), self.encode(tx_headers), hashfunc=hashlib.sha256)
        
        return is_valid


    def encode(self, tx):
        return json.dumps(tx, sort_keys=True).encode()
        

    def serialize(self):
        return {
            'owner': self.owner,
            'address': self.address,
            'private_key': self.private_key
        }
    
    def print_wallet(self):
        print(f'Owner: {self.owner}\nAddress: {self.address}\nPrivate Key: {self.private_key}')
        

    