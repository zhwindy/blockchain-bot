#encoding=utf-8
import os
import time
import web3
import requests
import random
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


def query(privkey, contract):
    """
    balanceOf
    """
    rpc = Rpc()
    account = web3.Account.from_key(privkey)
    call_data = '0x70a08231' + '000000000000000000000000' + account.address[2:]
    to = web3.Web3.to_checksum_address(contract)
    res = rpc.call(contract, call_data)
    return res


def mint_token(privkey, token_contract):
    """
    mint
    """
    account = web3.Account.from_key(privkey)
    rpc = Rpc()

    amount = hex(web3.Web3.to_wei(1000*10**8, 'ether'))[2:]
    data = '0x40c10f19' + '000000000000000000000000' + account.address[2:] + amount.rjust(64, '0')
    to = web3.Web3.to_checksum_address(token_contract)

    res = rpc.transfer_token(account, to, 0, gaslimit=85000, data=data)

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


def main_transfer_token(privkey, token_contract, to_address, nonce=None, amount=1):
    """
    token转账
    """
    rpc = Rpc()
    account = web3.Account.from_key(privkey)

    hex_amount = hex(web3.Web3.to_wei(amount, 'ether'))[2:]
    data = '0xa9059cbb' + '000000000000000000000000' + to_address.lower()[2:] + hex_amount.rjust(64, '0')

    to = web3.Web3.to_checksum_address(token_contract)
    try:
        res = rpc.transfer_token(account, to, 0, gaslimit=85000, nonce=nonce, data=data)
        print(res)
        return res
    except Exception as e:
        print(e)
        return False


def get_airdrop_address(airdrop_type=None):
    conn = get_conn(database='mint')
    cursor = conn.cursor()
    if airdrop_type in ['nft']:
        sql = "SELECT id, address FROM testnet_airdrop_whitelist where nft_drop=0"
    else:
        sql = "SELECT id, address FROM testnet_airdrop_whitelist where airdrop=0"
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


def airdrop_token(privKey, token_contract):
    """
    token airdrop
    """
    conn = get_conn(database='mint')
    cursor = conn.cursor()

    airdrop_address = get_airdrop_address()
    nonce = 1
    for i in airdrop_address:
        recrod_id = i.get("record_id")
        address = str(i.get("address", ""))
        if not address or not recrod_id:
            continue
        if len(address) != 42:
            continue
        amount = random.randint(100,10000)
        rt = main_transfer_token(privKey, token_contract, address, nonce=nonce, amount=amount)
        if not rt:
            time.sleep(2)
            continue
        else:
            if rt.get("result"):
                sql = f"update testnet_airdrop_whitelist set airdrop=1, amount={amount} where id={recrod_id}"
                print(sql)
                cursor.execute(sql)
                conn.commit()
                nonce += 1
            else:
                continue
        time.sleep(0.5)
    conn.close()


if __name__ == '__main__':
    token_contract = '0xdF639a5224EcCca72F6D84EE30CA67E5E2223C98'
    token_privKey = os.environ.get("PRIVATE_KEY_BOME")
    # print(query(token_privKey, token_contract))
    # print(mint_token(token_privKey, token_contract))
    airdrop_token(token_privKey, token_contract)
    # to_address = "0xCa261418513ea74Ef1416D5BBb1EDBe3d24dcB57"
    # print(mint_nft(nft_privKey, nft_contract, to_address=to_address))
