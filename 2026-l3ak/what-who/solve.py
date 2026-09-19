#!/usr/bin/env python3
import sys, struct

M, m32 = (1 << 64) - 1, 0xFFFFFFFF
rol64 = lambda x, n: ((x << (n & 63)) | ((x & M) >> (64 - (n & 63)))) & M if n & 63 else x & M
ror64 = lambda x, n: (((x & M) >> (n & 63)) | (x << (64 - (n & 63)))) & M if n & 63 else x & M
rol32 = lambda x, n: ((x << (n & 31)) | ((x & m32) >> (32 - (n & 31)))) & m32 if n & 31 else x & m32
ror32 = lambda x, n: (((x & m32) >> (n & 31)) | (x << (32 - (n & 31)))) & m32 if n & 31 else x & m32
ror8  = lambda x, n: (((x & 0xff) >> (n & 7)) | (x << (8 - (n & 7)))) & 0xff if n & 7 else x & 0xff

data = open("data.bin", "rb").read()
LE = lambda o: struct.unpack_from("<Q", data, o)[0]

def mix(h):
    h &= M
    h ^= h >> 28; h = (h * 0xA3B195354A39B70D) & M
    h ^= h >> 33; h = (h * 0xF1357AEA2E62A9C5) & M
    return h ^ (h >> 29)

def submit(key, raw, q):
    if raw:
        a, b = ((len(raw) << 48) ^ 0x243F6A8885A308D3) & M, 0x9B1D2D6B42F0A7B5
        for ch in raw:
            a = (0xD1342543DE82EF95 * rol64(a ^ ((b + ch) & M), 11) - 0x3943D8696D4A337D) & M
            b = (b - 0x64E2D294BD0F584B) & M
    else:
        a = 0x243F6A8885A308D3
    v = rol64((key ^ ((mix(a) - 0x7346D458D0C27229 * q) & M)) & M, 9 * q + 5)
    p = (0xDB4F0B9175AE2165 * v) & M
    return (p >> 27) ^ p

def q1():
    x = rol32(0xFB5647DA, 3)
    x = (x - 0x7F4A7C15) & m32
    y = x
    for _ in range(4):
        y = x ^ (y >> 15)
    x = (y * pow(0x045D9F3B, -1, 1 << 32)) & m32
    return (ror32(x, 9) ^ 0xC13FA9A9).to_bytes(4, "big")

def q2():
    A, B, C, Dt, acc, out = 0xE9, 0xF9, 0x109, 0x119, 0x5A, bytearray()
    for i in range(16):
        t = ror8(data[Dt + i] ^ data[C + i], data[B + i])
        c = ((t - data[A + i]) & 0xFF) ^ acc
        out.append(c)
        acc = (acc + data[Dt + i] + c + 0x13) & 0xFF
    return bytes(out)

def q3(N=102, W=17, base=0x129, start=18, goal=96):
    ok = lambda p: 0 <= p < 289 and data[base + p] == 1
    can = [[False] * (N + 1) for _ in range(289)]
    can[goal][0] = True
    for k in range(1, N + 1):
        for p in range(289):
            can[p][k] = any(ok(p + d) and can[p + d][k - 1] for d in (-W, 1, W, -1))
    assert can[start][N], "경로 없음"
    p, res = start, []
    for k in range(N, 0, -1):
        for d, ch in ((-W, "N"), (1, "E"), (W, "S"), (-1, "W")):
            if ok(p + d) and can[p + d][k - 1]:
                res.append(ch); p += d; break
    return "".join(res)

def q4(seed):
    r1 = (seed ^ 0x4F1BBCDCBFA54001) & M
    for r3 in range(0x89):
        r1 ^= r1 >> 0x1B
        r1 = (r1 * 0xC83A91E1D74B5F27) & M
        r1 = (r1 + rol64((r3 * 0xB5AD4ECEDA1CE2A9) & M, 0x1F) + 0x165667B19E3779F9) & M
        r1 = rol64(r1, 0x17)
        r1 ^= r1 >> 0x1F
    return r1

def q5(seed):
    r1 = (seed ^ 0xA0761D6478BD642F) & M
    for r3 in range(((seed >> 9) & 0x3FF) + 0x500):
        r1 = (r1 ^ (r1 << 13)) & M
        r1 ^= r1 >> 7
        r1 = (r1 ^ (r1 << 17)) & M
        r1 = (r1 + rol64((r3 * 0xE7037ED1A0B428DB) & M, 0x17) + 0x8EBC6AF09C88C6E3) & M
    return (r1 ^ rol64(seed, 0x1D) ^ 0x589965CC75374CC3) & M

def q6(seed, key):
    r2 = (rol64((seed ^ key) & M, 0x11) * 0xD6E8FEB86659FD93 + 0xA4093822299F31D0) & M
    r3 = (rol64(key, 0x29) ^ ((seed * 0x9E6C63D0676A9A99) & M))
    r3 = ((r3 + 0x13198A2E03707344) & M) ^ ror64(r2, 0xB)
    K1 = [LE(0x250 + 8 * i) for i in range(10)]
    K2 = [LE(0x2A0 + 8 * i) for i in range(10)]
    S  = [data[0x2F0 + i] for i in range(10)]
    F = lambda x, i: ((rol64(((x ^ K1[i]) + seed) & M, S[i]) ^ ((x * K2[i]) & M))
                      + (key ^ ((i * 0xC2B2AE3D27D4EB4F) & M))) & M
    a, b = r2, r3
    for i in range(9, -1, -1):
        a, b = b ^ F(a, i), a
    return a.to_bytes(8, "big") + b.to_bytes(8, "big")

seed = int(sys.argv[1], 16)
key = mix((seed ^ 0x57484F5F57415443) & M)
ans = [q1().decode("latin1"), q2().decode("latin1"), q3(),
       str(q4(seed)), f"{q5(seed):016x}"]
for i, a in enumerate(ans, 1):
    key = submit(key, a.encode("latin1"), i)
ans.append(q6(seed, key).hex())

for i, a in enumerate(ans, 1):
    print(f"Q{i}: {a}")
