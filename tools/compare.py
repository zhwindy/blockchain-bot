# encoding=utf-8
import os
import requests

ENV = 'main'

if ENV == 'main':
    NODE_URL = os.environ.get("NODE_URL_MAIN")
    CHAIN_ID = 1
else:
    NODE_URL = os.environ.get("NODE_URL_TEST")
    CHAIN_ID = 5


def get_tx_input_data(txid):
    param = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByHash",
        "params": [str(txid)],
        "id": 1
    }
    res = requests.post(NODE_URL, json=param)
    data = res.json()
    rt = data.get("result")
    if not rt:
        return "get none"
    input_data = rt.get("input")
    print("tx input data:", input_data)

    return input_data


def get_contract_code(address):
    param = {
        "jsonrpc": "2.0",
        "method": "eth_getCode",
        "params": [str(address), "latest"],
        "id": 1
    }
    res = requests.post(NODE_URL, json=param)
    data = res.json()
    code = data.get("result")
    print("contract code:", code)
    return code


def compare(txid, address):
    input_data = get_tx_input_data(txid)
    print(120*"=")
    code = get_contract_code(address)
    if input_data == code:
        print(100*"*", "equal")
    else:
        print(100*"*", "not equal")


if __name__ == '__main__':
    txid = "0xa8cb9dfdcb3d2074ae6b492e23f280f01a69a639afa5331f90cadaa2313faa48"
    address = "0x80313d5db1da630b952bd4af81d6585c4c3f984d"
    # get_tx_input_data(txid)
    compare(txid, address)
