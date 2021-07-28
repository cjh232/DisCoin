import threading
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from random import randint
import queue
import blockchain
import textwrap


class Miner:
    def __init__(self, cv, address, version, difficulty, blockchain, mined_evt):
        self._cv = cv
        self._address = address
        self._version = version
        self._difficulty = difficulty
        self._blockchain = blockchain
        self._mined_evt = mined_evt

    def start(self, headers, txs):
        self._t = threading.Thread(target=self.run, args=(headers, txs))
        self._t.start()

    def create_hash(self, encoded_headers_arr, nonce):

        encoded_headers = b''.join(
            encoded_headers_arr + [str(nonce).encode()])

        return hashlib.sha256(encoded_headers).hexdigest()

    def create_merkle_root(self, transactions):
        def encode(transaction): return json.dumps(
            transaction, sort_keys=True).encode()

        encoded_list = [encode(transaction) for transaction in transactions]

        encoded_bytes = b''.join(encoded_list)

        return hashlib.sha256(encoded_bytes).hexdigest()

    def run(self, time, txs):
        """
        Headers order is -> idx, timestamp, mrk, prev_hash
        """
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

                block = self.create_block(
                    index, time, nonce, txs, mrkl_root, block_hash, prev_hash)

                res = self._blockchain.offer_proof_of_work(
                    block, self._mined_evt)
                if res:
                    break

            nonce = randint(0, sys.maxsize)
            block_hash = self.create_hash(encoded_header_arr, nonce)

    def create_block(self, index, time, nonce, tx, mrkl_root, curr_hash, prev_hash):
        """Create a new block

        Returns:
            Dict[str, Any]: The newly created block.

        """

        return {
            'index': str(index),
            "ver": self._version,
            'time': time,
            'nonce': str(nonce),
            'tx': tx,
            'n_tx': len(tx),
            'mrkl_root': mrkl_root,
            'hash': curr_hash,
            'previous_hash': prev_hash,
            'relayed_by': self._address,
        }

    def join(self):
        self._t.join()


lock = threading.Lock()
blockchain = blockchain.Blockchain(1, 4, [], None, lock)


def mine_block(blockchain):
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
        miners.append(Miner(1, public_address, 1, 4, blockchain, mined_evt))

    for miner in miners:
        miner.start(time_now, [{'sender': 'me'}])

    for miner in miners:
        miner.join()


for i in range(20):
    mine_block(blockchain)

blockchain.print_chain()
