#encoding=utf-8
import os
import time
import web3
import requests
from decimal import Decimal


class Rpc:
    """
    eth rpc方法
    """
    def __init__(self, api='https://testnet-rpc.mintchain.io', chainid=1686, proxies=None, timeout=30):
        self.api = api
        self.chainid = chainid
        self.proxies = proxies
        self.timeout = timeout

    def get_current_block(self):
        """获取最新区块"""
        data = {"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}
        res = requests.post(self.api, json=data, proxies=self.proxies, timeout=self.timeout)
        return res.json()

    def get_block_detail(self, number):
        """获取区块hash"""
        if isinstance(number, int):
            number = hex(number)
        data = {"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[number,True],"id":1}
        res = requests.post(self.api, json=data, proxies=self.proxies, timeout=self.timeout)
        return res.json()

    def get_transaction(self, txhash):
        """获取的交易详情"""
        data = {"jsonrpc":"2.0","method":"eth_getTransactionByHash","params":[txhash],"id":1}
        res = requests.post(self.api, json=data, proxies=self.proxies, timeout=self.timeout)
        return res.json()

    def get_gas_price(self):
        """获取gasprice"""
        data = {"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}
        res = requests.post(self.api, json=data, proxies=self.proxies, timeout=self.timeout)
        return res.json()

    def get_gas_limit(self, to, data):
        """call估算gas"""
        data = {"jsonrpc":"2.0","method":"eth_estimateGas","params":[{"to": to, "data": data}],"id":1}
        res = requests.post(self.api, json=data, proxies=self.proxies, timeout=self.timeout)
        return res.json()

    def get_transaction_count_by_address(self, address):
        data = {"jsonrpc":"2.0","method":"eth_getTransactionCount","params":[address,'latest'],"id":1}
        res = requests.post(self.api, json=data, proxies=self.proxies, timeout=self.timeout)
        return res.json()

    def call(self, to, data):
        data = {"jsonrpc":"2.0","method":"eth_call","params":[{"to": to, "data": data}, "latest"],"id":1}
        res = requests.post(self.api, json=data, proxies=self.proxies, timeout=self.timeout)
        return res.json()

    def send_raw_transaction(self, hex):
        """广播交易"""
        data = {"jsonrpc":"2.0","method":"eth_sendRawTransaction","params":[hex],"id":1}
        res = requests.post(self.api, json=data, proxies=self.proxies, timeout=self.timeout)
        return res.json()

    def get_balance(self, address):
        """获取余额"""
        data = {"jsonrpc":"2.0","method":"eth_getBalance","params":[address, 'latest'],"id":1}
        res = requests.post(self.api, json=data, proxies=self.proxies, timeout=self.timeout)
        return res.json()#(int(res.json()['result'], 16)) / math.pow(10,18)

    def transfer(self, account, to, amount, gaslimit, **kw):
        amount = int(amount, 16) if isinstance(amount, str) else int(amount)
        gaslimit = int(gaslimit, 16) if not isinstance(gaslimit, int) else gaslimit
        gas_price = web3.Web3.toWei(Decimal('0.1'), 'gwei')
        max_gas_price = web3.Web3.toWei(Decimal('0.1'), 'gwei')
        transfer_amount = amount - (gaslimit * gas_price)
        if transfer_amount < 0:
            print(100*">", "余额不足")
            return False
        nonce = int(self.get_transaction_count_by_address(account.address)['result'], 16)
        tx = {
            'from': account.address,
            'to': to,
            'value': transfer_amount,
            'nonce': nonce,
            'gas': gaslimit,
            "maxFeePerGas": gas_price,
            "maxPriorityFeePerGas": max_gas_price,
            "type": "0x2",
            'chainId': self.chainid
        }
        if kw:
            tx.update(**kw)
        print(tx)
        signed = account.signTransaction(tx)
        print("txid:", signed.hash.hex())
        return self.send_raw_transaction(signed.rawTransaction.hex())
    
    def transfer_token(self, account, to, amount, gaslimit, **kw):
        amount = int(amount, 16) if isinstance(amount, str) else int(amount)
        gaslimit = int(gaslimit, 16) if not isinstance(gaslimit, int) else gaslimit
        gas_price = web3.Web3.toWei(Decimal('0.1'), 'gwei')
        max_gas_price = web3.Web3.toWei(Decimal('0.1'), 'gwei')
        nonce = int(self.get_transaction_count_by_address(account.address)['result'], 16)
        tx = {
            'from': account.address,
            'to': to,
            'value': amount,
            'nonce': nonce,
            'gas': gaslimit,
            "maxFeePerGas": gas_price,
            "maxPriorityFeePerGas": max_gas_price,
            "type": "0x2",
            'chainId': self.chainid
        }
        if kw:
            tx.update(**kw)
        print(tx)
        signed = account.signTransaction(tx)
        return self.send_raw_transaction(signed.rawTransaction.hex())


def query(privkey, contract):
    """
    balanceOf
    """
    rpc = Rpc()
    account = web3.Account.from_key(privkey)
    call_data = '0x70a08231' + '000000000000000000000000' + account.address[2:]
    to = web3.Web3.toChecksumAddress(contract)
    res = rpc.call(contract, call_data)
    return res


def mint(privkey, contract):
    """
    mint
    """
    account = web3.Account.from_key(privkey)
    rpc = Rpc()

    amount = hex(web3.Web3.toWei(1000*10**8, 'ether'))[2:]
    data = '0x40c10f19' + '000000000000000000000000' + account.address[2:] + amount.rjust(64, '0')
    to = web3.Web3.toChecksumAddress(contract)

    res = rpc.transfer_token(account, to, 0, gaslimit=99999, data=data)

    return res


def detect_balance(rpc, address):
    """
    检测余额
    """
    rt = rpc.get_balance(address)
    res = rt['result']
    balance = int(res, base=16)
    print(100*"=", balance)
    if balance > 8000000000000:
        return balance
    return False


def transfer(privkey, address):
    """
    转账
    """
    rpc = Rpc()
    account = web3.Account.from_key(privkey)
    balance = detect_balance(rpc, account.address)
    if balance:
        res = rpc.transfer(account, address, balance, gaslimit=300000)
        print(res)
    return True


def main_transfer(privkey):
    address = '0xA2d3cB65d9C05Da645a0206304D8eF7d7e67f82C'
    while True:
        try:
            transfer(privkey, address)
        except Exception as e:
            print(e)
            time.sleep(0.1)
            continue


def main_transfer_token(privkey, token_contract, to_address):
    """
    token转账
    """
    rpc = Rpc()
    account = web3.Account.from_key(privkey)

    amount = hex(web3.Web3.toWei(10000, 'ether'))[2:]
    data = '0xa9059cbb' + '000000000000000000000000' + to_address.lower()[2:] + amount.rjust(64, '0')

    to = web3.Web3.toChecksumAddress(token_contract)
    try:
        res = rpc.transfer_token(account, to, 0, gaslimit=99999, data=data)
        print(res)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    token_contract = '0x4ae6D009f463A8c80F382eAE7c1E880B077179d8'
    privateKey = os.environ.get("PRIVATE_KEY_01")
    # print(query(privateKey, token_contract))
    # print(mint(privateKey, token_contract))
    main_transfer_token(privateKey, token_contract, '0x2E8Eb30a716e5fE15C74233E039bfb1106e81D12')
