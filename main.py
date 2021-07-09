import firebase_admin
from firebase_admin import firestore
from blockchain import Blockchain


CREDENTIALS_PATH = 'discoin-ae632-firebase-adminsdk-olger-6d18986a1e.json'

credentials = firebase_admin.credentials.Certificate(CREDENTIALS_PATH)


default_app = firebase_admin.initialize_app(credentials)

db = firestore.client()
blocks_ref = db.collection('blocks')
query = blocks_ref.order_by(
    'index', direction=firestore.Query.ASCENDING)

blocks_stream = query.stream()

blockchain = Blockchain(blocks_stream)

new_transaction = {
    "sender": "Chris",
    "receiver": "John",
    "amount": 300
}

blockchain.add_transaction(new_transaction)

[new_block, index] = blockchain.mine_block()

doc_ref = db.collection("blocks").document(str(index))
doc_ref.set(new_block)

blockchain.print_chain()



