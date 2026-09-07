import struct
import sys

def disassemble(filename):
    with open(filename, 'rb') as f:
        firmware = f.read()

    pc = 0
    while pc < len(firmware):
        if pc + 4 > len(firmware):
            break
        
        byte0 = firmware[pc]
        byte1 = firmware[pc+1]
        byte2 = firmware[pc+2]
        byte3 = firmware[pc+3] # Opcode
        
        opcode = byte3
        reg_dest = (byte2 >> 4) & 0xF
        reg_src1 = byte2 & 0xF
        reg_src2 = byte0 & 0xF
        
        imm16_u = (byte1 << 8) | byte0
        imm16_s = imm16_u if not (imm16_u & 0x8000) else imm16_u - 0x10000
        
        jmp_target = pc + 4 + imm16_s
        
        out = ""
        
        if opcode == 0x00: out = "HALT"
        elif opcode == 0x11: out = f"MOV r{reg_dest}, r{reg_src1}"
        elif opcode == 0x29: out = f"RORI r{reg_dest}, r{reg_src1}, {imm16_s}"
        elif opcode == 0x2a: out = f"ROR r{reg_dest}, r{reg_src1}, r{reg_src2}"
        elif opcode == 0x2b: out = f"SHL r{reg_dest}, r{reg_src1}, r{reg_src2}"
        elif opcode == 0x2c: out = f"SHR r{reg_dest}, r{reg_src1}, r{reg_src2}"
        elif opcode == 0x3a: out = f"MOVI r{reg_dest}, {imm16_u} (0x{imm16_u:04x})"
        elif opcode == 0x52: out = f"XOR r{reg_dest}, r{reg_src1}, r{reg_src2}"
        elif opcode == 0x53: out = f"AND r{reg_dest}, r{reg_src1}, r{reg_src2}"
        elif opcode == 0x54: out = f"OR r{reg_dest}, r{reg_src1}, r{reg_src2}"
        elif opcode == 0x6b: out = f"MUL r{reg_dest}, r{reg_src1}, r{reg_src2}"
        elif opcode == 0x7c: out = f"ADD r{reg_dest}, r{reg_src1}, r{reg_src2}"
        elif opcode == 0x7d: out = f"SUB r{reg_dest}, r{reg_src1}, r{reg_src2}"
        elif opcode == 0x80: out = f"ADDI r{reg_dest}, r{reg_src1}, {imm16_s}"
        elif opcode == 0x90: out = f"CMP r{reg_src1}, r{reg_src2}"
        elif opcode == 0xa0: out = f"JMP 0x{jmp_target:04x}"
        elif opcode == 0xa1: out = f"JNZ 0x{jmp_target:04x}"
        elif opcode == 0xa2: out = f"JZ 0x{jmp_target:04x}"
        elif opcode == 0xc4: out = f"LDR r{reg_dest}, [r{reg_src1} + {imm16_s}]"
        elif opcode == 0xc5: out = f"STR r{reg_dest}, [r{reg_src1} + {imm16_s}]"
        elif opcode == 0xc6: out = f"LDR_ROM r{reg_dest}, [r{reg_src1} + {imm16_s}]"
        elif opcode == 0xe0: out = f"GETC r{reg_dest}"
        elif opcode == 0xe1: out = f"PUTC r{reg_src1}"
        else: out = f"UNKNOWN_OPCODE (0x{opcode:02x})"
        
        hex_dump = f"{byte0:02x} {byte1:02x} {byte2:02x} {byte3:02x}"
        print(f"0x{pc:04x} | {hex_dump:<12} | {out}")
        
        pc += 4

if __name__ == "__main__":
    disassemble('firmware.bin')
