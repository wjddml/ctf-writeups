from pwn import *
import subprocess, re

io = remote("whatwho.instances.ctf.l3ak.team", 1337, ssl=True)
seed = re.search(rb"Instance seed: ([0-9a-f]{16})",
                 io.recvuntil(b"case-sensitive.")).group(1).decode()
log.info(f"seed = {seed}")

out = subprocess.run(["python3", "solve.py", seed],
                     capture_output=True, text=True).stdout
answers = [l.split(": ", 1)[1] for l in out.strip().splitlines()]

for a in answers:
    io.recvuntil(b"? ")
    io.sendline(a.encode("latin1"))
io.interactive()
