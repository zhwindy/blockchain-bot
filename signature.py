#encoding=UTF-8
import rlp
from rlp.sedes import big_endian_int, Binary, binary
from eth_rlp import HashableRLP
from eth_utils.curried import keccak
from hexbytes import HexBytes
from eth_account import Account
from web3 import Web3


class LegacyTransaction(HashableRLP):
    fields = (
        ('nonce', big_endian_int),
        ('gasPrice', big_endian_int),
        ('gas', big_endian_int),
        ('to', Binary.fixed_length(20, allow_empty=True)),
        ('value', big_endian_int),
        ('data', binary),
    )


class Transaction(HashableRLP):
    fields = (
        ('nonce', big_endian_int),
        ('gasPrice', big_endian_int),
        ('gas', big_endian_int),
        ('to', Binary.fixed_length(20, allow_empty=True)),
        ('value', big_endian_int),
        ('data', binary),
        ('v', big_endian_int),
        ('r', big_endian_int),
        ('s', big_endian_int),
    )


def sign_legacy_tx():
    tx = {
        "to": HexBytes("0x3535353535353535353535353535353535353535"),
        "value": 1000000000000000000,
        "nonce": 9,
        "gas": 21000,
        "gasPrice": 20000000000,
        "data": b"",
    }
    encoded_tx = LegacyTransaction.from_dict(tx)
    print("rlp encode result:", rlp.encode(encoded_tx).hex())

    signing_hash = encoded_tx.hash()
    print("signing msg hash:", signing_hash.hex())

    key_obj = eth_key_obj(private_key="4646464646464646464646464646464646464646464646464646464646464646")

    result = key_obj.sign_msg_hash(signing_hash)
    print_sign_result(result)


def sign_normal_tx():
    tx = {
        "to": HexBytes("0x3535353535353535353535353535353535353535"),
        "value": 1000000000000000000,
        "nonce": 9,
        "gas": 21000,
        "gasPrice": 20000000000,
        "data": b"",
        "v": 1,
        "r": 0,
        "s": 0,
    }
    sign_155_tx(tx)


def sign_155_tx(transaction):
    print(transaction)
    encoded_tx = Transaction.from_dict(transaction)

    print(rlp.encode(encoded_tx).hex())
    print(encoded_tx.hash().hex())


    private_key = "4646464646464646464646464646464646464646464646464646464646464646"
    acct = Account.from_key(private_key)
    print("address:", acct.address)
    # signed_result = acct.signHash("0xdaf5a779ae972f972197303d7b574746c7ef83eadac0f2791ad23db92e4c8e53")
    signed_result = acct.sign_msg_hash("0xdaf5a779ae972f972197303d7b574746c7ef83eadac0f2791ad23db92e4c8e53")
    print("r: ", signed_result.r)
    print("s: ", signed_result.s)

    transaction["r"] = signed_result.r
    transaction["s"] = signed_result.s
    transaction["v"] = 37

    print(transaction)
    encoded_signed_tx = Transaction.from_dict(transaction)

    raw_tx = rlp.encode(encoded_signed_tx).hex()
    print(raw_tx)

    sender = Account.recover_transaction(raw_tx)
    print("sender: ", sender)


def eth_key_obj(private_key=""):
    acct = Account.from_key(private_key)
    key_obj = acct._key_obj
    return key_obj


def print_sign_result(result):
    """
    打印签名结果
    """
    print("v: ", result.v)
    print("r: ", result.r)
    print("s: ", result.s)
    print("signature: ", result)


def test_sign_hash():
    """
    签名哈希
    """
    key_obj = eth_key_obj()

    # signing_hash = "dd54f25d0bbeae343a1dec3acce8dc5b3a0886bdb9c5e667f65d5bbbe11bc093"
    signing_hash = "22658f1dab0720e8bf599551cc6dd75230ed4efefc7f6694f0b389e0807a0e52"

    result = key_obj.sign_msg_hash(HexBytes(signing_hash))
    print_sign_result(result)


def test_sign_msg():
    """
    签名msg本身
    """
    key_obj = eth_key_obj()

    # message = "I will pay Bob 1 ETH."
    message = "0x22658f1dab0720e8bf599551cc6dd75230ed4efefc7f6694f0b389e0807a0e52"
    # message = "0x22658f1dab0720e8bf599551cc6dd75230ed4efefc7f6694f0b389e0807a"

    # 添加固定前缀
    total_msg = "\x19Ethereum Signed Message:\n" + str(len(message)) + message

    singing_msg = Web3.toBytes(text=total_msg)

    result = key_obj.sign_msg(singing_msg)
    print_sign_result(result)


def test_sign_msg_hash():
    """
    签名msg哈希
    """
    key_obj = eth_key_obj()

    message = "I will pay Bob 1 ETH."
    msg_hash = keccak(text=message)
    # print(msg_hash.hex())

    msg_hash = Web3.toBytes(hexstr="0x22658f1dab0720e8bf599551cc6dd75230ed4efefc7f6694f0b389e0807a0e52")

    singing_msg = Web3.toBytes(text="\x19Ethereum Signed Message:\n32") + msg_hash
    sig_msg_hash = keccak(singing_msg)
    # sig_msg_hash = Web3.toBytes(hexstr="0x22658f1dab0720e8bf599551cc6dd75230ed4efefc7f6694f0b389e0807a0e52")

    result = key_obj.sign_msg_hash(sig_msg_hash)
    print_sign_result(result)


def main():
    sign_legacy_tx()
    # sign_normal_tx()
    # test_sign_hash()
    # test_sign_msg()
    # test_sign_msg_hash()


if __name__ == "__main__":
    main()
