#encoding=utf-8
import time
import web3
import requests
from decimal import Decimal


class Rpc:
    """
    eth rpc方法
    """
    def __init__(self, api='https://arb1.arbitrum.io/rpc', chainid=42161, proxies=None, timeout=30):
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
        """call计算gas"""
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
        print("txid:", signed.hash.hex())
        return self.send_raw_transaction(signed.rawTransaction.hex())




def query(privkey):
    """
    查询数量
    """
    rpc = Rpc()
    claim_contract = '0x67a24CE4321aB3aF51c2D0a4801c3E111D88C9d9'
    account = web3.Account.from_key(privkey)
    data = '0x84d24226000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb92266'
    to = web3.Web3.toChecksumAddress(claim_contract)
    res = rpc.call(claim_contract, data)
    return res


def claim(privkey):
    """
    领取
    """
    account = web3.Account.from_key(privkey)
    rpc = Rpc()
    # https://arbiscan.io/address/0x67a24CE4321aB3aF51c2D0a4801c3E111D88C9d9
    claim_contract = '0x67a24CE4321aB3aF51c2D0a4801c3E111D88C9d9' # clain合约地址
    data = '0x4e71d92d'
    to = web3.Web3.toChecksumAddress(claim_contract)
    res = rpc.transfer(account, to, 0, gaslimit=20000, data=data)
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
    account = web3.Account.from_key(privkey)
    # api = "http://127.0.0.1:8547"
    api = "https://open-platform.nodereal.io/a4a9f892480d45e395f93945c4b77c6e/arbitrum-nitro"
    rpc = Rpc(api=api)
    balance = detect_balance(rpc, account.address)
    if balance:
        res = rpc.transfer(account, address, balance, gaslimit=300000)
        print(res)
    return True


def collection(privkey, address):
    # 归集
    # https://arbiscan.io/token/0x912ce59144191c1204e64559fe8253a0e49e6548#balances
    rpc = Rpc()
    account = web3.Account.from_key(privkey)
    token = '0x912ce59144191c1204e64559fe8253a0e49e6548' # arb 代币地址

    # 1.查询地址余额
    call_data = '0x70a08231' + '000000000000000000000000' + account.address[2:]
    # call_data = "0x70a08231000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb92266"
    res = rpc.call(token, call_data)
    value = res['result']

    # 2.转账
    addr_1 = address.lower()[2:].rjust(64,'0')
    unit_2 = value[2:].rjust(64,'0')
    data = '0xa9059cbb' + addr_1 + unit_2
    to = web3.Web3.toChecksumAddress(token)
    res = rpc.transfer(account, to, 0, gaslimit=455210, data=data)
    return res


def main_transfer():
    pk = 'ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
    address = '0xA2d3cB65d9C05Da645a0206304D8eF7d7e67f82C'
    print(100*"*", "start")
    while True:
        try:
            transfer(pk, address)
        except Exception as e:
            print(e)
            time.sleep(0.1)
            continue


def main_transfer_token():
    # api = "http://127.0.0.1:8547"
    api = "https://open-platform.nodereal.io/a4a9f892480d45e395f93945c4b77c6e/arbitrum-nitro"
    rpc = Rpc(api=api)
    pk = 'ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
    address = '0xA2d3cB65d9C05Da645a0206304D8eF7d7e67f82C'

    addr_1 = address.lower()[2:].rjust(64,'0')
    data = '0xa9059cbb' + addr_1 + "0000000000000000000000000000000000000000000000b02ecf74c313880000"
    account = web3.Account.from_key(pk)

    token = '0x912ce59144191c1204e64559fe8253a0e49e6548' # arb 代币地址
    to = web3.Web3.toChecksumAddress(token)
    print(100*"*", "start")
    while True:
        try:
            res = rpc.transfer_token(account, to, 0, gaslimit=355210, data=data)
            print(res)
        except Exception as e:
            print(e)
            time.sleep(0.1)
            continue


if __name__ == '__main__':
    pk = '' # 你的私钥
    # 查询
    # print(query(pk))
    # 领取
    # res = claim(pk)
    # print(res)
    # 归集
    # address = ''
    # res = collection(pk, address)
    # transfer(pk, address)
    # main_transfer()
    main_transfer_token()
