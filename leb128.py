
def decode_leb128_varints(data):
    rt = []
    tmp = []
    for byte in data:
        tmp.append(byte & 0x7F)  # 取字节的低7位
        if not byte & 0x80:  # 如果最高位为0，说明这是最后一个字节
            value = 0
            for i, byte in enumerate(tmp):
                value |= (byte << (7 * i))
            rt.append(value)
            tmp = []
    return rt

# 示例数据
def decode_sequence():
    """
    data = [0x00, 0xe2, 0xa7, 0x33, 0xd9, 0x1a, 0x64, 0x02]
    """
    # transfer
    hex_string = "00e2a733d91a6402"
    # etching
    # hex_string = "0203049af8b1b1ed88a3ccc602039122052406a08d060a904e08a08d06"
    # hex_string = "020503880204e4fce3c6e8a4acb90805cce60706017f8190e912"
    # hex_string = "14e2a73314d91a1600"

    data = [int(hex_string[i:i+2], 16) for i in range(0, len(hex_string), 2)]

    decoded_value = decode_leb128_varints(data)

    return decoded_value

print("Decoded sequence:", decode_sequence())
