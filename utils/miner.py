import threading
import hashlib
import json
import sys
from datetime import datetime, timezone
from random import randint
from collections import namedtuple

import blockchain

Headers = namedtuple('Headers', [
    'index',
    'time',
    'nonce',
    'tx',
    'mrkl_root',
    'curr_hash',
    'prev_hash'
])


class Miner:
    def __init__(self, address, version, _blockchain, mined_evt):
        self._address = address
        self._version = version['id']
        self._difficulty = version['difficulty']
        self._blockchain = _blockchain
        self._mined_evt = mined_evt
        self._t = None

    def start(self, headers, txs):
        self._t = threading.Thread(target=self.run, args=(headers, txs))
        self._t.start()

    @staticmethod
    def create_hash(encoded_headers_arr, nonce):

        encoded_headers = b''.join(
            encoded_headers_arr + [str(nonce).encode()])

        return hashlib.sha256(encoded_headers).hexdigest()

    @staticmethod
    def create_merkle_root(transactions):
        def encode(transaction):
            return json.dumps(
                transaction, sort_keys=True).encode()

        encoded_list = [encode(transaction) for transaction in transactions]

        encoded_bytes = b''.join(encoded_list)

        return hashlib.sha256(encoded_bytes).hexdigest()

    def run(self, time, txs):
        prev_block = self._blockchain.get_last_block()

        index = str(int(prev_block["index"]) + 1)
        prev_hash = prev_block["hash"]
        mrkl_root = self.create_merkle_root(txs)

        headers = [index, time, mrkl_root, prev_hash]

        nonce = randint(0, sys.maxsize)

        encoded_header_arr = [val.encode() for val in headers]
        block_hash = self.create_hash(encoded_header_arr, nonce)

        while not self._mined_evt.is_set():

            if block_hash[:self._difficulty] == ''.zfill(self._difficulty):

                block_headers = Headers(
                    index, time, nonce, txs, mrkl_root, block_hash, prev_hash)

                block = self.create_block(block_headers)

                res = self._blockchain.offer_proof_of_work(
                    block, self._mined_evt)
                if res:
                    break

            nonce = randint(0, sys.maxsize)
            block_hash = self.create_hash(encoded_header_arr, nonce)

    def create_block(self, block_headers):
        """Create a new block

        Returns:
            Dict[str, Any]: The newly created block.

        """

        return {
            'index': str(block_headers.index),
            "ver": self._version,
            'time': block_headers.time,
            'nonce': str(block_headers.nonce),
            'tx': block_headers.tx,
            'n_tx': len(block_headers.tx),
            'mrkl_root': block_headers.mrkl_root,
            'hash': block_headers.curr_hash,
            'previous_hash': block_headers.prev_hash,
            'relayed_by': self._address,
        }

    def join(self):
        self._t.join()


lock = threading.Lock()
blockchain = blockchain.Blockchain(1, 4, [], None, lock)


def mine_block():
    mined_evt = threading.Event()

    time_now = datetime.now(timezone.utc).strftime("%d-%b-%Y (%H:%M:%S.%f)")

    wallets = [
        '1',
        '2',
        '3',
        '6',
        '4',
        '9'
    ]

    miners = []

    for public_address in wallets:
        version = {
            'id': 1,
            'difficulty': 4
        }
        miners.append(Miner(public_address, version, blockchain, mined_evt))

    for miner in miners:
        miner.start(time_now, [{'sender': 'me'}])

    for miner in miners:
        miner.join()


for i in range(20):
    mine_block()

blockchain.print_chain()
