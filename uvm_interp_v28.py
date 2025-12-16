import argparse
import json


def extract_bits(value, start, length):
    """Извлекает биты из значения"""
    return (value >> start) & ((1 << length) - 1)


def execute(bytecode):
    """Выполнение байткода"""
    registers = [0] * 64
    memory = [0] * 65536

    for i in range(0, len(bytecode), 8):
        command_bytes = bytecode[i:i + 8]
        if len(command_bytes) < 8:
            break

        cmd = int.from_bytes(command_bytes, 'little')
        opcode = extract_bits(cmd, 0, 4)  # A: биты 0-3

        if opcode == 14:  # load_const
            addr = extract_bits(cmd, 4, 6)  # B: биты 4-9
            const = extract_bits(cmd, 10, 21)  # C: биты 10-30
            registers[addr] = const

        elif opcode == 5:  # read_value
            addr_src = extract_bits(cmd, 4, 6)  # B: биты 4-9
            addr_dst = extract_bits(cmd, 10, 6)  # C: биты 10-15
            offset = extract_bits(cmd, 16, 6)  # D: биты 16-21

            mem_addr = registers[addr_src] + offset
            if mem_addr < len(memory):
                registers[addr_dst] = memory[mem_addr]

        elif opcode == 3:  # write_value
            addr_src = extract_bits(cmd, 4, 6)  # B: биты 4-9
            addr_dst = extract_bits(cmd, 10, 6)  # C: биты 10-15
            offset = extract_bits(cmd, 16, 6)  # D: биты 16-21

            mem_addr = registers[addr_dst] + offset
            if mem_addr < len(memory):
                memory[mem_addr] = registers[addr_src]

        elif opcode == 10:  # greater_or_equal
            addr_dst = extract_bits(cmd, 4, 6)  # B: биты 4-9
            mem_addr = extract_bits(cmd, 10, 28)  # C: биты 10-37 (28 бит)
            addr_src = extract_bits(cmd, 38, 6)  # D: биты 38-43

            if mem_addr < len(memory):
                result = 1 if registers[addr_src] >= memory[mem_addr] else 0
                dest_addr = registers[addr_dst]
                if dest_addr < len(memory):
                    memory[dest_addr] = result

    return registers, memory


def memory_dump_json(memory, start_addr, end_addr, filename):
    """Создание дампа памяти в формате JSON"""
    dump = {
        "memory_dump": {
            "range": f"{start_addr}-{end_addr}",
            "data": {}
        }
    }

    for addr in range(start_addr, min(end_addr + 1, len(memory))):
        dump["memory_dump"]["data"][str(addr)] = memory[addr]

    with open(filename, 'w') as f:
        json.dump(dump, f, indent=2)

    return dump


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help="Input binary file")
    parser.add_argument('-o', '--output', required=True, help="Output JSON dump file")
    parser.add_argument('-r', '--range', required=True, help="Memory range (e.g., '0-100')")
    args = parser.parse_args()

    with open(args.input, "rb") as file:
        bytecode = file.read()

    registers, memory = execute(bytecode)

    start_str, end_str = args.range.split('-')
    start_addr = int(start_str)
    end_addr = int(end_str)

    dump = memory_dump_json(memory, start_addr, end_addr, args.output)

    print(f"Program execution completed")
    print(f"Registers (non-zero): {[(i, reg) for i, reg in enumerate(registers) if reg != 0]}")
    print(f"Memory dump saved to {args.output}")


if __name__ == "__main__":
    main()