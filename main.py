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

blocks_ref = db.collection('versions')
version_query = blocks_ref.order_by(
    'version_id', direction=firestore.Query.DESCENDING).limit(1)

[ version_res ] = [v for v in version_query.stream()]

version = version_res.to_dict()
version_id = version["version_id"]
difficulty = version["difficulty"]

print(version_id, difficulty)

blocks_stream = query.stream()

chain = [block.to_dict() for block in query.stream()]

blockchain = Blockchain(version_id, int(difficulty), stream=blocks_stream) if len(chain) > 0 else Blockchain(version_id, int(difficulty), stream=None)

# If chain returned by steam is empty, Blockchain class is created
# with no paramets, causing a genesis block to be created. This needs
# to be stored to the db.

if len(chain) < 1:
    doc_ref = db.collection("blocks").document("0")
    doc_ref.set(blockchain.get_genesis_block())

new_transaction = {
    "sender": "Chris",
    "receiver": "bob",
    "amount": 300
}

blockchain.add_transaction(new_transaction)

[new_block, index] = blockchain.mine_block()

doc_ref = db.collection("blocks").document(str(index))
doc_ref.set(new_block)

new_transaction = {
    "sender": "Alex",
    "receiver": "John",
    "amount": 3100
}

blockchain.add_transaction(new_transaction)

new_transaction = {
    "sender": "Alex",
    "receiver": "Desmond",
    "amount": 3100
}

blockchain.add_transaction(new_transaction)

[new_block, index] = blockchain.mine_block()

doc_ref = db.collection("blocks").document(str(index))
doc_ref.set(new_block)


# blockchain.print_chain()



