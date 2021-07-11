import hashlib
import binascii
import wallets
import base64
import ecdsa

NO_PARAMS = "Wallet factory requires either a name or a wallet dictionary."

class WalletBuildError(Exception):
    
    def __init__(self, message="Error building wallet"):
        self.message = message
        super().__init__(self.message)


class WalletFactory:

    STARTING_AMOUNT = 500
    
    def create_wallet(self, name = None, wallet_dict = None):

        if not wallet_dict and not name:
            raise WalletBuildError(NO_PARAMS)

        if not wallet_dict:
            wallet_dict = self.build_wallet_dict(name)

        return wallets.Wallet(wallet_dict)


    # Generates ECDSA key pair
    def generate_key_pair(self):
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        private_key = sk.to_string().hex()

        vk = sk.get_verifying_key()
        public_key = vk.to_string().hex()

        print('Public Key:', public_key)
        
        public_key = base64.b64encode(bytes.fromhex(public_key))

        return [private_key, public_key]

    def build_wallet_dict(self, name):

        [private_key, public_key] = self.generate_key_pair()

        return {
            'owner': name, 
            'address': public_key,
            'private_key': private_key,
        }

factory = WalletFactory()


existing_wallet = {
    'owner': 'Chris',
    'address': b'DPcRVZy+FCHJzdTRQb42OZ/HLH+jkdSVLestfSKu5W+p43N+Fy9mR4Y3RjcHhpGrtIvYQ4O/Pu6eBPMfXFzCag==',
    'private_key': '90fbae98d03107a1f3c13de6fbab137c455a7911d7607426d5483624dff662c2'
}

w2 = factory.create_wallet(name="Chris")

w2.print_wallet()

tx = w2.create_transaction('Dan', 500)

print(w2.verify_transaction(tx))

