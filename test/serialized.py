#encoding=utf-8
from dataclasses import asdict, dataclass
from pprint import pprint
from typing import Optional
import rlp
from eth_typing import HexStr
from eth_utils import keccak, to_bytes
from rlp.sedes import Binary, big_endian_int, binary
from web3 import Web3
from web3.auto import w3


def hex_to_bytes(data: str) -> bytes:
    return to_bytes(hexstr=HexStr(data))


class Transaction(rlp.Serializable):
    fields = [
        ("nonce", big_endian_int),
        ("gas_price", big_endian_int),
        ("gas", big_endian_int),
        ("to", Binary.fixed_length(20, allow_empty=True)),
        ("value", big_endian_int),
        ("data", binary),
        ("v", big_endian_int),
        ("r", big_endian_int),
        ("s", big_endian_int),
    ]


@dataclass
class DecodedTx:
    hash_tx: str
    from_: str
    to: Optional[str]
    nonce: int
    gas: int
    gas_price: int
    value: int
    data: str
    chain_id: int
    r: str
    s: str
    v: int


def decode_raw_tx(raw_tx: str):
    tx = rlp.decode(hex_to_bytes(raw_tx), Transaction)
    hash_tx = Web3.toHex(keccak(hex_to_bytes(raw_tx)))
    from_ = w3.eth.account.recover_transaction(raw_tx)
    to = w3.toChecksumAddress(tx.to) if tx.to else None
    data = w3.toHex(tx.data)
    r = hex(tx.r)
    s = hex(tx.s)
    chain_id = (tx.v - 35) // 2 if tx.v % 2 else (tx.v - 36) // 2
    return DecodedTx(hash_tx, from_, to, tx.nonce, tx.gas, tx.gas_price, tx.value, data, chain_id, r, s, tx.v)


def main():
    raw_tx = "0xf86782036f1e82520894114e5a1570bf702a7ab2a94b90f138a9a6d12a5a8609184e72a000801ca05c35563ad6b8e99cdd404e4e0e26256ae4c4d9f157b5a00c1acbf711d0ae9756a014fbffb33fce44986623e02717ccff92ff2ba59c7f07467d69d7197d6701a3b1"
    res = decode_raw_tx(raw_tx)
    pprint(asdict(res))


def deserialized_tx():
    """
    此方法和ethernum包已淘汰 https://pypi.org/project/ethereum/
    """
    from ethereum.transactions import Transaction
    raw_tx = "0x02f873011585010dca68a385010dca68a382520894d5fbda4c79f38920159fe5f22df9655fde292d4787471264ac24c4e880c080a0cc9ce23baf0d3f756e9951e5ebb6fa5f8dbcdf4f254d292f0c4885e43916227fa01697187c6782ca4367f9e4ab73a4aeec6ce49900a8f764fe63c7d530ba6078a1"
    txs = rlp.decode(hex_to_bytes(raw_tx), Transaction)
    rt = txs.to_dict()
    print(rt)


def deserialized_new_tx():
    """
    支持EIP2718 EIP1559
    """
    from eth.vm.forks.arrow_glacier.transactions import ArrowGlacierTransactionBuilder as TransactionBuilder
    # raw_tx = "0x02f873011585010dca68a385010dca68a382520894d5fbda4c79f38920159fe5f22df9655fde292d4787471264ac24c4e880c080a0cc9ce23baf0d3f756e9951e5ebb6fa5f8dbcdf4f254d292f0c4885e43916227fa01697187c6782ca4367f9e4ab73a4aeec6ce49900a8f764fe63c7d530ba6078a1"
    # raw_tx = "0xf86782036f1e82520894114e5a1570bf702a7ab2a94b90f138a9a6d12a5a8609184e72a000801ca05c35563ad6b8e99cdd404e4e0e26256ae4c4d9f157b5a00c1acbf711d0ae9756a014fbffb33fce44986623e02717ccff92ff2ba59c7f07467d69d7197d6701a3b1"
    raw_tx = "0x01f86d01820383850342770c0082526c94a2d3cb65d9c05da645a0206304d8ef7d7e67f82c851bf08eb00080c001a068b63afb78b7f1d213bdb15d81552efc9874f9ebb8152f19b88fece39df7c2f8a0110675d405d2ab838e9f9be81c81293e115926c4d7480d67aba9a5a1051b6f78"
    decode_tx = TransactionBuilder().decode(hex_to_bytes(raw_tx))
    # print(decode_tx.__dict__)
    print(decode_tx.type_id)
    print(decode_tx.chain_id)
    print(decode_tx.sender.hex())
    print(decode_tx.to.hex())
    print(decode_tx.value)



if __name__ == "__main__":
    # main()
    deserialized_new_tx()
