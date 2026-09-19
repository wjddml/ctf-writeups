# What/Who

L3ak CTF 2026 / reverse engineering

12바이트 고정폭 명령의 커스텀 VM. 바이트코드는 `vault.wwc` 컨테이너 안에
봉인되어 있고, ELF는 인터프리터다. ISA를 복원해 6개 문제를 역산한다.

- `unpack.py` — 컨테이너 복호화, seal 검증, 프롬프트 문자열 덤프
- `disassemble.py` — VM 디스어셈블러
- `solve.py` — 시드를 받아 6개 답 출력
- `auto_solve.py` — 원격 접속 후 자동 제출

## 사용

    python3 unpack.py vault.wwc
    python3 disassemble.py
    python3 solve.py <instance_seed>
    python3 auto_solve.py

Writeup: https://wjddml.github.io/writeups/what-who/
