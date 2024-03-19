#encoding=utf-8
import time
import web3
import math
import requests
from decimal import Decimal
from db_mysql import get_conn


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
        gas_price = web3.Web3.to_wei(Decimal('0.1'), 'gwei')
        max_gas_price = web3.Web3.to_wei(Decimal('0.1'), 'gwei')
        transfer_amount = amount - (gaslimit * gas_price)
        if transfer_amount < 0:
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
        signed = account.sign_transaction(tx)
        print("txid:", signed.hash.hex())
        return self.send_raw_transaction(signed.rawTransaction.hex())
    
    def transfer_token(self, account, to, amount, gaslimit, nonce=None, **kw):
        amount = int(amount, 16) if isinstance(amount, str) else int(amount)
        gaslimit = int(gaslimit, 16) if not isinstance(gaslimit, int) else gaslimit
        gas_price = web3.Web3.to_wei(Decimal('0.1'), 'gwei')
        max_gas_price = web3.Web3.to_wei(Decimal('0.1'), 'gwei')
        # 若没有自定义nonce则使用系统默认值
        if not nonce:
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
        signed = account.sign_transaction(tx)
        return self.send_raw_transaction(signed.rawTransaction.hex())


def detect_balance(rpc, address):
    """
    检测余额
    """
    try:
        rt = rpc.get_balance(address)
        res = rt.get('result', '0x0')
        balance = int(res, base=16)
    except Exception as e:
        balance = 0
    return balance


def get_check_address():
    conn = get_conn(database='mint')
    cursor = conn.cursor()
    sql = "SELECT id, address FROM mint_forest where status=0"
    records = []
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        for r in result:
            info = {"record_id": 0, "address": ''}
            info['record_id'] = r[0]
            info['address'] = r[1]
            records.append(info)
    except Exception as e:
        print(e)
    conn.close()
    return records


def check_address(address):
    flag = None
    balance = 0
    rpc_dict = {
        "eth": Rpc(api="https://eth-mainnet.nodereal.io/v1/f6ff79c79bb84d7aa02dba4902d89a26"),
        "bsc": Rpc(api="https://bsc-mainnet.nodereal.io/v1/f6ff79c79bb84d7aa02dba4902d89a26"),
        "polygon": Rpc(api="https://polygon-mainnet.nodereal.io/v1/f6ff79c79bb84d7aa02dba4902d89a26"),
        "op": Rpc(api="https://opt-mainnet.nodereal.io/v1/f6ff79c79bb84d7aa02dba4902d89a26"),
        "arb": Rpc(api="https://open-platform.nodereal.io/f6ff79c79bb84d7aa02dba4902d89a26/arbitrum-nitro/"),
        "base": Rpc(api="https://open-platform.nodereal.io/f6ff79c79bb84d7aa02dba4902d89a26/base"),
        "zksync": Rpc(api="https://open-platform.nodereal.io/f6ff79c79bb84d7aa02dba4902d89a26/zksync"),
    }
    for k, v in rpc_dict.items():
        ck_balance = detect_balance(v, address)
        if ck_balance > 0:
            flag = k
            balance = ck_balance / math.pow(10,18)
            break
        else:
            continue
    
    return flag, balance


def check_status():
    """
    check process
    """
    conn = get_conn(database='mint')
    cursor = conn.cursor()

    all_address = get_check_address()
    for i in all_address:
        recrod_id = i.get("record_id")
        address = str(i.get("address", "")).strip()
        if not address or not recrod_id:
            continue
        if len(address) != 42:
            continue
        flag, balance = check_address(address)
        print(recrod_id, address, flag, balance)
        if not flag:
            sql = f"update mint_forest set status=2 where id={recrod_id}"
        else:
            sql = f"update mint_forest set status=1, {flag}={balance} where id={recrod_id}"
        cursor.execute(sql)
        conn.commit()
    conn.close()


if __name__ == '__main__':
    check_status()
