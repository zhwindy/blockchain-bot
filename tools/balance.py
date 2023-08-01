# encoding=utf-8
import os
from web3 import Web3

ENV = 'main'

if ENV == 'main':
    NODE_URL = os.environ.get("NODE_URL_MAIN")
    CHAIN_ID = 1
else:
    NODE_URL = os.environ.get("NODE_URL_TEST")
    CHAIN_ID = 5

ADDRESS = "0xB46AAe4592b1C29DFB71D128169aC4980dD6E325"

w3 = Web3(Web3.HTTPProvider(NODE_URL))

balance = w3.fromWei(w3.eth.get_balance(ADDRESS), "ether")

print(f"The balance of {ADDRESS} is: {balance} ETH")
