# encoding=utf-8
from web3 import Web3
from decimal import Decimal

ENV = 'main'

if ENV == 'main':
    NODE_URL = 'https://mainnet.infura.io/v3/2849c01a970f4ed082cb57be7f9db8bb'
    CHAIN_ID = 1
else:
    NODE_URL = 'https://goerli.infura.io/v3/2849c01a970f4ed082cb57be7f9db8bb'
    CHAIN_ID = 5

w3 = Web3(Web3.HTTPProvider(NODE_URL))

FROM_ADDRESS_01 = "0xB46AAe4592b1C29DFB71D128169aC4980dD6E325"
FROM_ADDRESS_02 = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

private_key_01 = ""
private_key_02 = ""

TO_ADDRESS_NULL = None
TO_ADDRESS_01 = "0x7fa31d53Aaa649Bbf08ba2fEa0aE5B6b71cd2ccd"
TO_ADDRESS_02 = "0x13eDC33D36086422D547693c21b365259e4823bc"
TO_ADDRESS_03 = "0xB46AAe4592b1C29DFB71D128169aC4980dD6E325"
TO_ADDRESS_04 = "0xBA9193FE0768008D1928A23a31F1dDB0B1D2eC53"
TO_ADDRESS_05 = "0xA2d3cB65d9C05Da645a0206304D8eF7d7e67f82C"


def check_address(address):
    if Web3.isChecksumAddress(address):
        address = Web3.toChecksumAddress(address)
    return address

def get_nonce(address):
    nonce = w3.eth.get_transaction_count(address)
    return nonce

def get_data(text):
    data = Web3.toBytes(text=text)
    return data

def generate_1559_tx(from_address, to_address, value, gas_limit=21000, gas_price=None, text='', tx_type="0x2"):
    nonce = get_nonce(from_address)
    data = get_data(text)
    gas_price_amount = 10000000000 if not gas_price else gas_price
    transaction = {
        "to": check_address(to_address),
        "value": value,
        "nonce": nonce,
        "gas": gas_limit,
        "maxFeePerGas": gas_price_amount,
        "maxPriorityFeePerGas": 5000000000,  # 1Gwei
        "chainId": CHAIN_ID,
        "type": tx_type,  # 选填
        "data": data
    }
    transactionA = {
        "to": check_address(to_address),
        "value": value,
        "nonce": nonce,
        "gas": gas_limit,
        "gasPrice": gas_price_amount,
        "accessList": [],
        "chainId": CHAIN_ID,
        "data": data
    }
    return transaction

def generate_old_tx(from_address, to_address, value, gas_limit=21000, gas_price=None, text=''):
    nonce = get_nonce(from_address)
    data = get_data(text)
    gas_price_amount = 10000000000 if not gas_price else gas_price
    transaction = {
        "to": check_address(to_address),
        "value": value,
        "nonce": nonce,
        "gas": gas_limit,
        "gasPrice": gas_price_amount,
        # "chainId": CHAIN_ID,
        "data": data
    }
    return transaction

def sign_tx(trancaction, private_key):
    signed_txn = w3.eth.account.sign_transaction(trancaction, private_key)
    print("signed_raw_tx:", signed_txn.rawTransaction.hex())
    print("singed_txid", signed_txn.hash.hex())
    return signed_txn

def main():
    value = Web3.toWei(Decimal('0.00000012'), 'ether')
    gas_limit = 21100
    gas_price = Web3.toWei(Decimal('14'), 'gwei')  # MaxFee=13Gwei
    tx = generate_1559_tx(FROM_ADDRESS_02, TO_ADDRESS_05, value, gas_limit=gas_limit, gas_price=gas_price)
    # tx = generate_old_tx(FROM_ADDRESS_02, TO_ADDRESS_04, value, gas_limit=gas_limit, gas_price=gas_price)
    signed_txn = sign_tx(tx, private_key_02)
    print("r:", signed_txn.r)
    print("s:", signed_txn.s)
    # w3.eth.send_raw_transaction(signed_txn.rawTransaction)


if __name__ == "__main__":
    main()
