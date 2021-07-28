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

    """ A user wallet

    This represents the user's DisCoin wallet.     

    Args:
        owner (str): 
            name of the wallet owner
        address (str):
            256-bit sha256 hashed address of the wallet owner.
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

    def __init__(self, wallet_dict, controller):
        self.owner = wallet_dict["owner"]
        self.address = wallet_dict["address"]
        self.public_key = wallet_dict["public_key"]
        self.private_key = wallet_dict["private_key"]
        self.controller = controller

    @property
    def amount(self):
        """Return a sum of all the UTXO linked to this wallet's address"""
        utxo_list = self.controller.get_utxo_list(self.address)

        utxo_sum = 0

        for utxo in utxo_list:
            utxo_sum = utxo_sum + utxo["amount"]

        return utxo_sum

    def create_transaction(self, out_addr, amount):
        """Form a valid transaction.

        Combine an array of UTXO that are >= to the amount specified (input).
        Create a resulting array, containing at least one UTXO, to the receiving
        wallet (output). If the input sum > amount, a second UTXO will be created to store
        the 'change'. This UTXO is addressed to the current wallet address.


        Args:
            out_addr -- the address of the wallet receiving the output
            amount -- total of the transaction

        Returns:
            A dictionary representing the new transaction created
        """
        [utxo_in, utxo_out] = self.create_tx_in_and_out(amount, out_addr)

        new_tx = {
            'sender': self.address,
            'receiver': out_addr,
            'amount': amount,
            'in': utxo_in,
            'out': utxo_out,
        }

        new_tx['sig'] = self.sign_transaction(new_tx)

        return new_tx

    def sign_transaction(self, new_tx):
        """Creates and returns a transaction signature.

        Args:
            new_tx -- New transaction to be signed
            private_key -- Private key associated with this wallet.

        Returns:
            The base64 encoded transaction signature
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

        Args:
            unverified_tx -- Transaction to be verified
            public_key -- Public key of the wallet suspected of making this transaction

        Returns:
            A boolean indicated whether the transaction is verified.


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

    def to_dict(self):
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

    def create_tx_in_and_out(self, amount, out_addr):
        """Creates input and output arrays for transaction

        Combines the neccessary utxo's into an input array such that
        their sums are >= to the amount argument. Creates an output array
        sending the out_addr the correct amount of DisCoin. If there is
        any change (ie: input_sum > amount) the difference is added to the output
        array in the form of a utxo addressed to the sender's wallet.

        Args:
            amount : int -- Intended transaction amount
            out_addr : str -- Wallet address of the receiver

        Returns:
            A list containing the utxo_input and the utxo_output arrays

        """

        utxo_list = self.controller.get_utxo_list(self.address)

        utxo_sum = 0
        utxo_in = []
        utxo_out = []

        for utxo in utxo_list:
            utxo_in.append(utxo)
            utxo_sum = utxo_sum + utxo["amount"]

            if utxo_sum >= amount:
                break

        resulting_utxo = {
            'amount': amount,
            'rec_addr': out_addr
        }

        utxo_out.append(resulting_utxo)

        if utxo_sum > amount:
            change_utxo = {
                'amount': utxo_sum - amount,
                'rec_addr': self.address
            }

            utxo_out.append(change_utxo)

        return [utxo_in, utxo_out]
