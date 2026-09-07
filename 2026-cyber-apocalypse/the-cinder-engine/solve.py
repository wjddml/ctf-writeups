import sys

def get_inverse_matrix(matrix):
    n = len(matrix)
    aug = [row[:] + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(matrix)]
    for i in range(n):
        pivot = -1
        for k in range(i, n):
            if aug[k][i] == 1:
                pivot = k
                break
        if pivot == -1:
            sys.exit(1)
        aug[i], aug[pivot] = aug[pivot], aug[i]
        for k in range(n):
            if k != i and aug[k][i] == 1:
                for j in range(2*n):
                    aug[k][j] ^= aug[i][j]
    return [row[n:] for row in aug]

def run_mix_block(rom, input_state):
    mem = [0] * 256
    for i in range(32):
        mem[i] = input_state[i]
    regs = [0] * 16
    pc = 0x0070
    
    while pc < 0x1018:
        b0, b1, b2, opcode = rom[pc:pc+4]
        imm = (b1 << 8) | b0
        if opcode == 0xc4:
            regs[(b2 >> 4) & 0xF] = mem[regs[b2 & 0xF] + imm]
        elif opcode == 0xc5:
            mem[regs[b2 & 0xF] + imm] = regs[(b2 >> 4) & 0xF]
        elif opcode == 0x52:
            regs[(b2 >> 4) & 0xF] = regs[b2 & 0xF] ^ regs[b0 & 0xF]
        pc += 4
    return mem[128:160]

def solve():
    with open('firmware.bin', 'rb') as f:
        rom = f.read()

    sbox = list(rom[0x10c4 : 0x10c4 + 256])
    target = list(rom[0x12e4 : 0x12e4 + 32])
    round_keys = [list(rom[0x11c4 + i*32 : 0x11c4 + (i+1)*32]) for i in range(9)]

    inv_sbox = {v: i for i, v in enumerate(sbox)}

    print("[*] 1단계")
    base_out = run_mix_block(rom, [0]*32)
    mix_matrix = [[0] * 32 for _ in range(32)]
    for i in range(32):
        test_in = [0] * 32
        test_in[i] = 1
        out = run_mix_block(rom, test_in)
        for j in range(32):
            mix_matrix[j][i] = out[j] ^ base_out[j]

    inv_mix_matrix = get_inverse_matrix(mix_matrix)

    # Decryption
    state = target[:]
    for r in range(8, 0, -1):
        state = [state[i] ^ round_keys[r][i] for i in range(32)]
        state = [state[i] ^ base_out[i] for i in range(32)]
        new_state = [0] * 32
        for i in range(32):
            for j in range(32):
                if inv_mix_matrix[i][j]:
                    new_state[i] ^= state[j]
        state = [inv_sbox[b] for b in new_state]

    required_input = [state[i] ^ round_keys[0][i] for i in range(32)]
    
    print(f"[*] 2단계")
    
    enc_flag = list(rom[0x1304 : 0x1304 + 26])
    flag = "".join(chr(required_input[i] ^ enc_flag[i]) for i in range(26))
    
    print("[*] 3단계")
    print(f"\n=> FLAG: {flag}")

if __name__ == '__main__':
    solve()
