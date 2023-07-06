# encoding=utf-8
from web3 import Web3

ENV = 'main'

if ENV == 'main':
    NODE_URL = 'https://mainnet.infura.io/v3/2849c01a970f4ed082cb57be7f9db8bb'
    CHAIN_ID = 1
else:
    NODE_URL = 'https://goerli.infura.io/v3/2849c01a970f4ed082cb57be7f9db8bb'
    CHAIN_ID = 5


ADDRESS = "0xB46AAe4592b1C29DFB71D128169aC4980dD6E325"

w3 = Web3(Web3.HTTPProvider(NODE_URL))

balance = w3.fromWei(w3.eth.get_balance(ADDRESS), "ether")

print(f"The balance of {ADDRESS} is: {balance} ETH")
