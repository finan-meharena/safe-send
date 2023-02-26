from hashlib import sha512
import json
import time

from flask import Flask, request
import requests


# Class to represent a Block

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_has = previous_hash
        self.nonce = 0

    # method to generate block hash 

    def compute_block_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha512(block_string.encode()).hexdigest()


class Blockchain:
    difficulty = 2  # difficulty of PoW algorithm

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_block_hash()
        self.chain.append(genesis_block)

    def add_new_block(self, block, proof):
        previous_hash = self.last_block.hash

        # if hash for last block and new block doesnt match, or of no valid proof of work, return false
        if (previous_hash != block.previous_hash or not self.is_valid_proof(block)):
            return False

        # if above is validated, add block
        block.hash = proof
        self.chain.append(block)

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

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_block_hash()
        while not computed_hash.startswith("0" * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_block_hash()

        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

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

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        return (block_hash.startswith("0" * Blockchain.difficulty) and block_hash == block.compute_block_hash())

    @property
    def last_block(self):
        return self.chain[-1]


##################### End of Block Chain codes ##################


def announce_new_block(block):
    pass
    # for node in nodes:
    #     pass
