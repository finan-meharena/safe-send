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
