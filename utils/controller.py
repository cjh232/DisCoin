import firebase_admin
from firebase_admin import firestore
import factories


class UserDoesNotExist(Exception):

    def __init__(self, message="User does not exist under this username"):
        self.message = message
        super().__init__(self.message)


class WalletDoesNotExist(Exception):

    def __init__(self, message="Wallet does not exist under this address"):
        self.message = message
        super().__init__(self.message)


class DatabaseController:

    def __init__(self, credentials_path):
        self.credentials = firebase_admin.credentials.Certificate(
            credentials_path)
        self._start_firebase_app()

    def _start_firebase_app(self):
        """Creates a firestore client instance"""

        firebase_admin.initialize_app(self.credentials)
        self.db = firestore.client()

    def get_user_address(self, username: str):
        """
        Returns the user's wallet address if it exists.
        If not, raises UserDoesNotExist exception.
        """

        user_ref = self.db.collection('users').document(username)

        user_doc = user_ref.get()

        if not user_doc.exists:
            raise UserDoesNotExist

        return user_doc.to_dict()["address"]

    def get_user_wallet(self, address):
        """
        Returns user wallet matching the given address if it exists.
        If it does not exist, raises WalletDoesNotExist exception.
        """

        wallet_ref = self.db.collection('wallets').document(address)

        wallet_doc = wallet_ref.get()

        if not wallet_doc.exists:
            raise WalletDoesNotExist

        return wallet_doc.to_dict()

    def get_blockchain_stream(self):
        blocks_ref = self.db.collection('blocks')

        query = blocks_ref.order_by(
            'index', direction=firestore.Query.ASCENDING
        )

        return query.stream()

    def get_blockchain_version(self):
        versions_ref = self.db.collection('versions')

        query = versions_ref.order_by(
            'version_id', direction=firestore.Query.DESCENDING
        ).limit(1)

        [version_res] = [v for v in query.stream()]

        return version_res.to_dict()

    def save_block(self, block, index):
        self.db.collection('blocks').document(str(index)).set(block)

    def save_wallet(self, wallet, address):
        self.db.collection('wallets').document(address).set(wallet.to_dict())

    def save_public_key(self, key, address):
        self.db.collection('public_keys').document(address).set({'key': key})

    def save_user(self, address, user):
        self.db.collection('users').document(user).set({'address': address})

    def register_new_user(self, wallet):
        user = wallet.owner
        address = wallet.address
        public_key = wallet.public_key

        self.save_public_key(public_key, address)
        self.save_wallet(wallet, address)
        self.save_user(address, user)

    def add_utxo(self, amount, rec_addr):
        self.db.collection('utxos').add({
            'rec_addr': rec_addr,
            'amount': amount
        })

    def get_utxo_list(self, addr):
        utxo_ref = self.db.collection('utxos')

        utxo_query = utxo_ref.where('rec_addr', '==', addr)

        return [utxo.to_dict() for utxo in utxo_query.stream()]
