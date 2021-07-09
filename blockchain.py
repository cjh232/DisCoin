import hashlib
import json
from datetime import date, datetime, timezone

class Blockchain:

    def __init__(self, stream = None):
        self.chain = []
        self.transactions = []

        if not stream:
            self.chain.append(self.create_genesis())
        else:
            self.build_from_stream(stream)


    def create_block(self, index, time, nonce, tx, mrkl_root, curr_hash, prev_hash):
        return {
        'index': str(index),
        'time': time,
        'nonce': str(nonce),
        'tx': tx,
        'n_tx': len(tx),
        'mrkl_root': mrkl_root,
        'hash': curr_hash,
        'previous_hash': prev_hash
    }

    def create_merkle_root(self, transactions):
        encode = lambda transaction: json.dumps(transaction, sort_keys=True).encode()

        encoded_list = [encode(transaction) for transaction in transactions]

        encoded_bytes = b''.join(encoded_list)

        return hashlib.sha256(encoded_bytes).hexdigest()


    def create_genesis(self):
        time = datetime.now(timezone.utc).strftime("%d-%b-%Y (%H:%M:%S.%f)")

        return self.create_block(0, time, 0, [], self.create_merkle_root([]), '0', '0')

    def build_from_stream(self, stream):
        
        for doc in stream:
            block = doc.to_dict()
            self.chain.append(block)


    def mine_block(self):
        index = len(self.chain)

        previous_block = self.chain[index - 1]

        time = datetime.now(timezone.utc).strftime("%d-%b-%Y (%H:%M:%S.%f)")
        idx = str(index)
        mrkl_root = self.create_merkle_root(self.transactions)
        previous_hash = previous_block["hash"]
        nonce = 1

        header_vals = [time, idx, str(nonce), mrkl_root, previous_hash]
        encoded_header_vals = [val.encode() for val in header_vals]

        encoded_header = b''.join(encoded_header_vals)
        block_hash = hashlib.sha256(encoded_header).hexdigest()

        while block_hash[:2] != '00':
            nonce = nonce + 1
            header_vals = [time, idx, str(nonce), mrkl_root, previous_hash]
            encoded_header_vals = [val.encode() for val in header_vals]
            encoded_header = b''.join(encoded_header_vals)
            block_hash = hashlib.sha256(encoded_header).hexdigest()


        block = self.create_block(
            index, 
            time, 
            nonce, 
            self.transactions, 
            mrkl_root, 
            block_hash, 
            previous_hash
        )

        self.chain.append(block)
        return [block, index]

    def print_chain(self):
        for block in self.chain:
            print(block["index"], block["hash"])

    def add_transaction(self, transaction):
        self.transactions.append(transaction)