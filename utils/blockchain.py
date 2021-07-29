import hashlib
import json
import threading
from datetime import date, datetime, timezone
from contextlib import contextmanager


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
        self._chain = []
        self._transactions = []
        self._version = version
        self._difficulty = difficulty
        self._controller = controller
        self._lock = lock

        if len(arr) < 1:
            self.genesis_block = self.create_genesis()
            self._chain.append(self.genesis_block)
        else:
            self.build_from_arr(arr)

    def __iter__(self):
        return iter(self._chain)

    def create_genesis(self):
        """Create the genesis block for a new blockchain

        Returns:
            The newly created genesis block

        """
        time = datetime.now(timezone.utc).strftime("%d-%b-%Y (%H:%M:%S.%f)")

        genesis = {
            'index': 0,
            "ver": self._version,
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
        for block in self._chain:
            print(f'\nBlock {int(block["index"]) + 1} / {len(self._chain)}')
            print('-----------------------------')
            for key, value in block.items():
                print(key, value, sep=': ')

    def add_transaction(self, transaction):
        self._transactions.append(transaction)

    def is_valid(self):

        if(len(self.chain) == 1):
            return True

        idx = 1
        prev_block = self._chain[0]

        while idx < len(self._chain):
            curr_block = self._chain[idx]

            if prev_block["hash"] != curr_block["previous_hash"]:
                return False

            idx = idx + 1
            prev_block = curr_block

    def get_genesis_block(self):
        return self.genesis_block

    def offer_proof_of_work(self, block, mined_evt):

        # By default miners will wait indefinitely to acquire the lock.
        # Change this -1 value to the desired timeout in seconds.
        with self._acquire_with_timeout(-1) as acquired:
            if acquired and not mined_evt.is_set():

                proof = block["hash"]

                if self.proof_is_valid(proof):
                    self._chain.append(block)
                    mined_evt.set()
                    return True
                else:
                    print('Proof is invalid')
                    return False
            else:
                print(
                    f'timeout: lock not available - Miner: {block["related_by"]}')
                return False

    def proof_is_valid(self, proof):
        return proof[:self._difficulty] == ''.zfill(self._difficulty)

    def get_last_block(self):
        return self._chain[-1]

    @contextmanager
    def _acquire_with_timeout(self, timeout):
        result = self._lock.acquire(timeout=timeout)

        try:
            yield result
        finally:
            if result:
                self._lock.release()
