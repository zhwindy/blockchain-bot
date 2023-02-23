#encoding=UTF-8
import rlp
from rlp.sedes import big_endian_int, Binary, binary
from eth_rlp import HashableRLP
from eth_utils.curried import keccak
from hexbytes import HexBytes


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


def calc_tx_hash():
    """
    根据交易信息计算txid
    hash -> 0x36ddb3f70342df549baedffe003ef83135f602bbb83a322d4baa3551887bfa73
    """
    tx_1 = {
        "to": HexBytes("0xba9193fe0768008d1928a23a31f1ddb0b1d2ec53"),
        "nonce": 896,
        "value": 130000000000,
        "gas": 21100,
        "gasPrice": 15000000000,
        "data": HexBytes("0x54657374"),
        "r": 51023773841636720645149149726976275097076670065050936192028049303897811118177,
        "s": 22016167616636097922969612854712271387470573855501079162965546036255888421769,
        "v": 28,
    }
    tx_2 = {
        "to": HexBytes("0xba9193fe0768008d1928a23a31f1ddb0b1d2ec53"),
        "nonce": 897,
        "value": 130000000000,
        "gas": 21100,
        "gasPrice": 13000000000,
        "data": HexBytes(""),
        "r": 67325963513153196585755999219055555788031880235441262461852322136602384365308,
        "s": 3781697335848271801542357045983226115340286817398090402097202291675311908898,
        "v": 38,
    }
    # 不适用type=2的交易
    tx = {
        "to": HexBytes("0x7fa31d53aaa649bbf08ba2fea0ae5b6b71cd2ccd"),
        "nonce": 879,
        "value": 123456,
        "gas": 21000,
        "gasPrice": 24703574854,
        "data": HexBytes(""),
        "r": 96798898795283778156482881145947583124583008660550670642215953162828651750904,
        "s": 43341865430107220614878181281196388390370079076037315232442735039025985204681,
        "v": 1,
    }
    tx_obj = Transaction.from_dict(tx)
    raw_tx = rlp.encode(tx_obj).hex()
    print("rawTx:", raw_tx)
    tx_hash = keccak(HexBytes(raw_tx)).hex()
    print("txid:", tx_hash)


if __name__ == "__main__":
    calc_tx_hash()
