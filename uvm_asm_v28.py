import argparse
import pprint


def set_bits(byte_array, start_bit, length, value):
    """Устанавливает биты в массиве байт"""
    for i in range(length):
        bit = (value >> i) & 1
        bit_index = start_bit + i
        byte_index = bit_index // 8
        bit_in_byte = bit_index % 8
        if bit:
            byte_array[byte_index] |= (1 << bit_in_byte)
        else:
            byte_array[byte_index] &= ~(1 << bit_in_byte)
    return byte_array


def asm_load_const(addr: int, const: int):
    """Код 14: load_const;addr;const"""
    byte_array = [0] * 8
    set_bits(byte_array, 0, 4, 14)  # A: код операции
    set_bits(byte_array, 4, 6, addr)  # B: адрес регистра (6 бит)
    set_bits(byte_array, 10, 21, const)  # C: константа (21 бит)
    return bytes(byte_array)


def asm_read_value(addr_src: int, addr_dst: int, offset: int):
    """Код 5: read_value;addr_src;addr_dst;offset"""
    byte_array = [0] * 8
    set_bits(byte_array, 0, 4, 5)  # A: код операции
    set_bits(byte_array, 4, 6, addr_src)  # B: адрес регистра-источника
    set_bits(byte_array, 10, 6, addr_dst)  # C: адрес регистра-назначения
    set_bits(byte_array, 16, 6, offset)  # D: смещение
    return bytes(byte_array)


def asm_write_value(addr_src: int, addr_dst: int, offset: int):
    """Код 3: write_value;addr_src;addr_dst;offset"""
    byte_array = [0] * 8
    set_bits(byte_array, 0, 4, 3)  # A: код операции
    set_bits(byte_array, 4, 6, addr_src)  # B: адрес регистра-источника
    set_bits(byte_array, 10, 6, addr_dst)  # C: адрес регистра-назначения
    set_bits(byte_array, 16, 6, offset)  # D: смещение
    return bytes(byte_array)


def asm_greater_or_equal(addr_dst: int, mem_addr: int, addr_src: int):
    """Код 10: greater_or_equal;addr_dst;mem_addr;addr_src"""
    byte_array = [0] * 8
    set_bits(byte_array, 0, 4, 10)  # A: код операции
    set_bits(byte_array, 4, 6, addr_dst)  # B: адрес регистра-назначения
    set_bits(byte_array, 10, 28, mem_addr)  # C: адрес памяти (28 бит)
    set_bits(byte_array, 38, 6, addr_src)  # D: адрес регистра
    return bytes(byte_array)


def asm(IR):
    """Преобразование промежуточного представления в байткод"""
    bytecode = bytes()
    for op, *args in IR:
        if op == 'load_const':
            bytecode += asm_load_const(args[0], args[1])
        elif op == 'read_value':
            bytecode += asm_read_value(args[0], args[1], args[2])
        elif op == 'write_value':
            bytecode += asm_write_value(args[0], args[1], args[2])
        elif op == 'greater_or_equal':
            bytecode += asm_greater_or_equal(args[0], args[1], args[2])
        else:
            print(f"ERROR: Unknown operation {op}")
    return bytecode


def test():
    """Тесты из спецификации"""
    # Тест load_const (A=14, B=51, C=817)
    expected1 = bytes([0x3E, 0xC7, 0x0C, 0x00, 0x00, 0x00, 0x00, 0x00])
    assert list(asm_load_const(51, 817)) == list(expected1)

    # Тест read_value (A=5, B=58, C=46, D=23)
    expected2 = bytes([0xA5, 0xBB, 0x17, 0x00, 0x00, 0x00, 0x00, 0x00])
    assert list(asm_read_value(58, 46, 23)) == list(expected2)

    # Тест write_value (A=3, B=12, C=62, D=51)
    expected3 = bytes([0xC3, 0xF8, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00])
    assert list(asm_write_value(12, 62, 51)) == list(expected3)

    # Тест greater_or_equal (A=10, B=2, C=811, D=31)
    expected4 = bytes([0x2A, 0xAC, 0x0C, 0x00, 0xC0, 0x07, 0x00, 0x00])
    assert list(asm_greater_or_equal(2, 811, 31)) == list(expected4)

    print("All tests passed!")


def full_asm(text):
    """Полный ассемблирование из текста"""
    text = text.strip()
    IR = []
    for line in text.splitlines():
        parts = line.strip().split(';')
        op = parts[0]
        args = list(map(int, parts[1:])) if len(parts) > 1 else []
        IR.append((op, *args))
    return asm(IR), IR


def main():
    test()
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-t', '--test', required=True)
    args = parser.parse_args()

    with open(args.input) as file:
        text = file.read()

    with open(args.output, 'wb') as output_file:
        bytecode, IR = full_asm(text)
        output_file.write(bytecode)

    print(f"Number of assembled commands: {len(IR)}")

    if args.test == '1':
        pprint.pprint(IR)
        print("Bytecode:", ' '.join([f'0x{i:02x}' for i in bytecode]))


if __name__ == "__main__":
    main()