import struct, sys

M = (1 << 64) - 1
CODE_DOM = 0x434152445F564549
DATA_DOM = 0x4C45444745525F56

def dec(buf, key, dom):
    out = bytearray()
    for i, c in enumerate(buf):
        t = (dom ^ key ^ (0xA24BAED4963EE407 * (i + 1))) & M
        t ^= t >> 27
        v5 = (0x3C79AC492BA7B653 * t) & M
        u = (0x1C69B3F74AC4AE35 * ((v5 >> 33) ^ v5)) & M
        w = (u >> 27) ^ u
        x = ((w >> ((5 * i) & 0x38)) ^ c) & 0xFF
        rot = (key + ((dom & ~0xFF) | ((dom + 3 * i) & 0xFF))) & 7
        x = ((x << rot) | (x >> (8 - rot))) & 0xFF
        sub = (((key >> 16) & 0xFF) + ((dom >> 8) & 0xFF) + 29 * i) & 0xFF
        out.append((x - sub) & 0xFF)
    return bytes(out)

def cksum(buf, dom):
    v3 = (dom ^ (0x9E6C63D0676A9A99 * len(buf))) & M
    v4 = 0x6A09E667F3BCC909
    for b in buf:
        y = (v3 ^ ((v4 + b) & M)) & M
        v4 = (v4 + 0x6A09E667F3BCC909) & M
        v8 = (0xD6E8FEB86659FD93 * (((y << 13) | (y >> 51)) & M)) & M
        v3 = v8 ^ (v8 >> 29)
    v9 = (0xBEA225F9EB34556D * (v3 ^ (v3 >> 32))) & M
    v9 = (0x94D049BB133111EB * (v9 ^ (v9 >> 31))) & M
    return v9 ^ (v9 >> 30)

raw = open(sys.argv[1] if len(sys.argv) > 1 else "vault.wwc", "rb").read()
magic, ver, hsz, n, dsz, entry, key, ck, dk = struct.unpack_from("<QHHIIIQQQ", raw, 0)
assert magic == 0x1A0A0D4F48575789 and ver == 3 and hsz == 64
print(f"insn={n} data={dsz} entry={entry} key={key:016x}")

code = dec(raw[64:64 + 12*n], key, CODE_DOM)
data = dec(raw[64 + 12*n:64 + 12*n + dsz], key, DATA_DOM)
print("code seal", cksum(code, CODE_DOM) == ck, " data seal", cksum(data, DATA_DOM) == dk)

open("code.bin", "wb").write(code)
open("data.bin", "wb").write(data)

import re
for m in re.finditer(rb"[ -~]{6,}", data):
    print(f"  data+0x{m.start():04x}  {m.group().decode()}")
