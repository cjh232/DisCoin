import firebase_admin
from firebase_admin import firestore
from blockchain import Blockchain
import wallets
import binascii
import json


CREDENTIALS_PATH = 'discoin-ae632-firebase-adminsdk-olger-6d18986a1e.json'

credentials = firebase_admin.credentials.Certificate(CREDENTIALS_PATH)


default_app = firebase_admin.initialize_app(credentials)

db = firestore.client()

USER_NAME = 'Chris'

wallet_ref = db.collection('wallets').document(USER_NAME)
key_ref = db.collection('public_keys').document(USER_NAME)

wallet_doc = wallet_ref.get()
key_doc = key_ref.get()

if wallet_doc.exists:
    wallet = wallet_doc.to_dict()
    public_key = key_doc.to_dict()

    encoded_private_key = wallet["private_key"].encode()
    private_key_pair = wallets.build_private_key(encoded_private_key)

    encoded_public_key = public_key["key"].encode()
    public_key_pair = wallets.build_public_key(encoded_public_key)

    # print(key_pair.exportKey())

    transaction = {
        "sender": "Alex",
        "receiver": "John",
        "amount": 3100
    }

    tx_encoded = json.dumps(transaction, sort_keys=True).encode()
    signature = wallets.sign_transaction(tx_encoded, private_key_pair)

    # print('original:', signature)

    hex_sig = binascii.hexlify(signature)

    print(signature == binascii.unhexlify(hex_sig))

    if wallets.verify_transaction(tx_encoded, public_key_pair, signature):
        print('Valid transaction')


# TODO: Add function to create transaction so that it includes a signature