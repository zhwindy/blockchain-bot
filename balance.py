# encoding=utf-8
from web3 import Web3

# NODE_URL = 'https://mainnet.infura.io/v3/2849c01a970f4ed082cb57be7f9db8bb'
NODE_URL = 'https://goerli.infura.io/v3/2849c01a970f4ed082cb57be7f9db8bb'

ADDRESS_FROM = "0x8e703608D7ab5144F8fE26D96193c10a9Aa2C287"
ADDRESS_TO = "0xB46AAe4592b1C29DFB71D128169aC4980dD6E325"

w3 = Web3(Web3.HTTPProvider(NODE_URL))

balance_from = w3.fromWei(w3.eth.get_balance(ADDRESS_FROM), "ether")
balance_to = w3.fromWei(w3.eth.get_balance(ADDRESS_TO), "ether")

print(f"The balance of { ADDRESS_FROM } is: { balance_from } ETH")
print(f"The balance of { ADDRESS_TO } is: { balance_to } ETH")
