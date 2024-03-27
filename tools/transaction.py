# encoding=utf-8
import os
from web3 import Web3
from decimal import Decimal

ENV = 'main'

if ENV == 'main':
    NODE_URL = os.environ.get("NODE_URL_MAIN")
    CHAIN_ID = 1
else:
    NODE_URL = os.environ.get("NODE_URL_TEST")
    CHAIN_ID = 5

w3 = Web3(Web3.HTTPProvider(NODE_URL))

FROM_ADDRESS_01 = "0x6C9d0DE7F98664647319461895f14F170f190CCA"
FROM_ADDRESS_02 = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

private_key_01 = os.environ.get("PRIVATE_KEY_OL")
private_key_02 = os.environ.get("PRIVATE_KEY_MIS")

TO_ADDRESS_NULL = None
TO_ADDRESS_01 = "0x5F00163E536c2f3626FE8ccFfeb11b64536BB0aF"
TO_ADDRESS_02 = "0xBA9193FE0768008D1928A23a31F1dDB0B1D2eC53"


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
    gas_priority_amount = Web3.toWei(Decimal('1'), 'gwei')
    transaction = {
        "to": check_address(to_address),
        "value": value,
        "nonce": nonce,
        "gas": gas_limit,
        "maxFeePerGas": gas_price_amount,
        "maxPriorityFeePerGas": gas_priority_amount,
        "chainId": CHAIN_ID,
        "type": tx_type,  # 选填
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
        "data": data
    }
    return transaction


def sign_tx(trancaction, private_key):
    signed_txn = w3.eth.account.sign_transaction(trancaction, private_key)
    # print("signed_raw_tx:", signed_txn.rawTransaction.hex())
    print("singed_txid", signed_txn.hash.hex())
    return signed_txn


def main():
    tx_type = 2
    value = Web3.toWei(Decimal('0.0001'), 'ether')
    gas_limit = 21000
    gas_price = Web3.toWei(Decimal('14'), 'gwei')  # MaxFeePrice
    if tx_type == 2:
        unsign_tx = generate_1559_tx(FROM_ADDRESS_01, TO_ADDRESS_01, value, gas_limit=gas_limit, gas_price=gas_price)
    else:
        unsign_tx = generate_old_tx(FROM_ADDRESS_01, TO_ADDRESS_01, value, gas_limit=gas_limit, gas_price=gas_price)
    signed_txn = sign_tx(unsign_tx, private_key_01)
    # print("r:", signed_txn.r)
    # print("s:", signed_txn.s)
    w3.eth.send_raw_transaction(signed_txn.rawTransaction)


if __name__ == "__main__":
    # address = "0x5F00163E536c2f3626FE8ccFfeb11b64536BB0aF"
    # print(get_nonce(address))
    main()
