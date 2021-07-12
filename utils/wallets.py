"""
Contains the definition of the Wallet class.

"""


import hashlib
import base64
import json
import ecdsa


def encode_transaction(transaction):
    """Returns encoded transaction"""
    return json.dumps(transaction, sort_keys=True).encode()


class Wallet:

    """
    A class to represent a wallet.

    ...
    Attributes
    ----------
    owner : str
        name of the wallet owner
    address : str
        256-bit hashed address of the wallet owner.
        Also links to the owners public key stored in the db
    private_key : (temporary)
        wallet ECDSA private key used to sign new transactions.
        IMPORTANT: This is temporary and will be removed in the
        future when this project is setup with Discord. The user will
        be responsible for keeping track of his/her private key.

        Converted to hex, must be converted back to bytes before
        being used
    public_key :
        wallets ECDSA public key. Encoded in base64, needs to be
        decoded before being used.
    """

    def __init__(self, wallet_dict):
        self.owner = wallet_dict["owner"]
        self.address = wallet_dict["address"]
        self.public_key = wallet_dict["public_key"]
        self.private_key = wallet_dict["private_key"]

    @property
    def amount(self):
        """Return a sum of all the UTXO linked to this wallet's address"""
        return 5

    def create_transaction(self, out_addr, amount):
        """Form a valid transaction.

        Arguments:
        ----------
        out_addr -- the address of the wallet receiving the output
        amount -- total of the transaction

        Combine an array of UTXO that are >= to the amount specified (input).
        Create a resulting array, containing at least one UTXO, to the receiving
        wallet (output). If the input sum > amount, a second UTXO will be created to store
        the 'change'. This UTXO is addressed to the current wallet address.
        """
        new_tx = {
            'sender': self.address,
            'receiver': out_addr,
            'amount': amount
        }

        new_tx['sig'] = self.sign_transaction(new_tx)

        return new_tx

    def sign_transaction(self, new_tx):
        """Creates and returns a transaction signature.

        Arguments:
        ----------
        new_tx -- New transaction to be signed
        private_key -- Private key associated with this wallet.

         """

        enc_tx = encode_transaction(new_tx)

        # When the key pair is created we convert the private key to hex. from_string requires
        # a byte string so we need to make the conversion. Otherwise we will get a malformed
        # key error thrown.

        signing_key = ecdsa.SigningKey.from_string(bytes.fromhex(
            self.private_key), curve=ecdsa.SECP256k1)

        signature = base64.b64encode(
            signing_key.sign(enc_tx, hashfunc=hashlib.sha256))

        return signature

    def verify_transaction(self, unverified_tx):
        """Verifies transaction signature

        IMPORTANT: This function may be better fit as a method of blockchain
        which will verify the transaction before adding it to the transaction
        pool

        Arguments:
        ----------
        unverified_tx -- Transaction to be verified
        public_key -- Public key of the wallet suspected of making this transaction


        """
        # When the key pair is created we encode the public key in base64 to create a shorter
        # key. Before reconstructing, using from_string(), we must decode it. Otherwise we will get
        # a malformed key error thrown.

        verifying_key = ecdsa.VerifyingKey.from_string(
            base64.b64decode(self.public_key), curve=ecdsa.SECP256k1)

        tx_headers = {
            'sender': unverified_tx['sender'],
            'receiver': unverified_tx['receiver'],
            'amount': unverified_tx['amount']
        }

        is_valid = verifying_key.verify(base64.b64decode(unverified_tx['sig']), encode_transaction(
            tx_headers), hashfunc=hashlib.sha256)

        return is_valid

    def serialize(self):
        """Converts the wallet to a JSON object"""
        return {
            'owner': self.owner,
            'address': self.address,
            'public_key': self.public_key,
            'private_key': self.private_key
        }

    def print_wallet(self):
        """Prints the wallet to the console"""
        print(
            f'Owner: {self.owner}\n'
            f'Address: {self.address}\n'
            f'Private Key: {self.private_key}\n'
            f'Public Key: {self.public_key}\n'
        )
