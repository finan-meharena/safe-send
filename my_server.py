from hashlib import sha512
import json
import time

from flask import Flask, request
import requests


class Block:
    """ Class to represent a single Block"""

    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0

    # method to generate block hash
    def compute_block_hash(self):
        # store block data as a string, then hash it, generating a unique value
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha512(block_string.encode()).hexdigest()


class Blockchain:
    """Class to represent a cain of blocks, Blockchain"""
    difficulty = 2  # difficulty of PoW algorithm

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    # method that creates the very first block, genesis block
    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_block_hash()
        self.chain.append(genesis_block)

    # method that adds a new block
    def add_new_block(self, block, proof):
        previous_hash = self.last_block.hash

        # if hash for last block and new block doesnt match, or of no valid proof of work, return false
        if previous_hash != block.previous_hash or not self.is_valid_proof(block):
            return False

        # if above is validated, add block
        block.hash = proof
        self.chain.append(block)

    # method that mines a block before it is added to the blockchain
    def mine(self):

        # if no unconfirmed transactions, no further mining
        if not self.unconfirmed_transactions:
            return False
        last_block = self.last_block

        new_block = Block(last_block.index + 1,
                          self.unconfirmed_transactions,
                          time.time(),
                          last_block.hash)
        proof = self.proof_of_work(new_block)
        self.add_new_block(new_block, proof)
        self.unconfirmed_transactions = []
        announce_new_block(new_block)

        return new_block.index

    # method that tries and gets the nonce as per the difficulty level set
    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_block_hash()
        while not computed_hash.startswith("0" * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_block_hash()

        return computed_hash

    # method that adds unconfirmed transaction(pending ones)
    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    # method that checks if a chain is valid
    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash

            delattr(block, "hash")
            if not cls.is_valid_proof(block, block.hash) or previous_hash != block.previous_has:
                result = False
                break
            block.hash = block_hash
            previous_hash = block_hash

            return result

    # method that if proof of work is valid based on the difficulty level set
    @classmethod
    def is_valid_proof(cls, block, block_hash):
        return block_hash.startswith("0" * Blockchain.difficulty) and block_hash == block.compute_block_hash()

    # method that gets the last block in the blockchain
    @property
    def last_block(self):
        return self.chain[-1]


########################################## End of Blockchain codes #######################################

# Flask Web Application


app = Flask(__name__)

# copy of blockchain for a node
blockchain = Blockchain()

# set to store connected nodes' address
nodes = set()


# endpoint to add new transaction
@app.route("/new-transaction", methods=['POST'])
def new_transaction():
    pass


# endpoint to get the current valid chain
@app.route("/chain", methods=['GET'])
def get_chain():
    # consensus()

    chain_data = []

    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data), "chain": chain_data})


@app.route("/mine", methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "Sorry, there are no transactions to be mined"
    return f"Block #{result} is mined successfully!"


# function to register new node
def register_new_peers():
    nodes = request.get_json()
    if not nodes:
        return "Invalid Data", 400
    for node in nodes:
        nodes.add(node)
    return "Node successfully added!", 200


# endpoint to show pending transactions,
@app.route("/pending_tx")
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


# consensus algorithm
def consensus():
    global blockchain
    longest_chain = None
    curr_len = len(blockchain.chain)

    # get length of each chain in each node,
    for node in nodes:
        response = requests.get(f"http://{node}")
        length = response.json()['length']
        chain = response.json()['chain']

        # if length of any of the nodes is found to be longer than the current one and it is valid,choose that chain
        if length > curr_len and blockchain.check_chain_validity(chain):
            curr_len = length
            longest_chain = chain

        # only if a longer chain is found, current chain is replaced with it,
        if longest_chain:
            blockchain = longest_chain
            return True
        return False


# endpoint to add a block
@app.route("/add_block", methods=['POST'])
def validate_and_add_block():
    block_data = request.get_json()
    block = Block(block_data['index'],
                  block_data['transactions'],
                  block_data['timestamp'],
                  block_data['previous_hash'])
    proof = block_data['hash']
    added = blockchain.add_new_block(block, proof)

    if not added:
        return "Sorry,the Block couldn't be added to the chain!"
    return "Block added to chain!", 201


# function to add new node to the network
def announce_new_block(block):
    for node in nodes:
        url = f"http://{node}/add_block"
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))


print("Server running...")