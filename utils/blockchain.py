import hashlib
import json
import threading
from datetime import date, datetime, timezone


class Blockchain:
    """The in memory representation of the blockchain.

    This blockchain is assembled at runtime using the blocks
    retrieved from the Firestore database. If no blocks are stored
    in the database, a brand new chain is created by appending a
    genesis block, which is then saved to the database.

    Args: 
        version (str):
            The id of the current blockchain version.
        difficulty (int):
            The integer difficulty of the blockchain. Reflects
            how many 0's are meant to prefix any block hashes.
        arr (list[Dict[str]]): 
            The array of blocks retrieved from the Firestore database.
            The blocks are retrieved in ascending order and are used
            to reconstruct the blockchain from previous usage
        controller (:class:`controller.DatabaseController`):
            The datbase controller class which handles all the database
            request throughout the codebase.   

    """

    def __init__(self, version, difficulty, arr, controller, lock):
        self.chain = []
        self.transactions = []
        self.version = version
        self.difficulty = difficulty
        self.controller = controller
        self.lock = lock

        if len(arr) < 1:
            self.genesis_block = self.create_genesis()
            self.chain.append(self.genesis_block)
        else:
            self.build_from_arr(arr)

    def create_genesis(self):
        """Create the genesis block for a new blockchain

        Returns:
            The newly created genesis block

        """
        time = datetime.now(timezone.utc).strftime("%d-%b-%Y (%H:%M:%S.%f)")

        genesis = {
            'index': 0,
            "ver": self.version,
            'time': time,
            'nonce': 0,
            'tx': [],
            'n_tx': 0,
            'mrkl_root': hashlib.sha256(b'').hexdigest(),
            'hash': '0',
            'previous_hash': '0'
        }

        return genesis

    def build_from_arr(self, arr):
        """Rebuild the blockchain from an array of blocks

        Args:
            arr: A list of blocks to be included in the blockchain

        Returns:
            Nothing: Assigns self.chain to the input list

        """
        self.chain = arr

    def print_chain(self):
        for block in self.chain:
            print(f'\nBlock {int(block["index"]) + 1} / {len(self.chain)}')
            print('-----------------------------')
            for key, value in block.items():
                print(key, value, sep=': ')

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def is_valid(self):

        if(len(self.chain) == 1):
            return True

        idx = 1
        prev_block = self.chain[0]

        while idx < len(self.chain):
            curr_block = self.chain[idx]

            if prev_block["hash"] != curr_block["previous_hash"]:
                return False

            idx = idx + 1
            prev_block = curr_block

    def get_genesis_block(self):
        return self.genesis_block

    def offer_proof_of_work(self, block, mined_evt):

        self.lock.acquire()

        # If event is set a block has already been mined.
        if mined_evt.is_set():
            self.lock.release()
            return False

        result = False

        proof = block["hash"]

        if self.proof_is_valid(proof):
            self.chain.append(block)
            mined_evt.set()
            result = True
        else:
            print('Proof is invalid')

        self.lock.release()

        return result

    def proof_is_valid(self, proof):
        return proof[:self.difficulty] == ''.zfill(self.difficulty)

    def get_last_block(self):
        return self.chain[-1]
