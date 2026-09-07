# The Cinder Engine

Cyber Apocalypse 2026 / reversing / medium

ARM aarch64 stripped 바이너리에 내장된 커스텀 VM. ISA를 복원하고
펌웨어 안의 8라운드 SPN 블록 암호를 역산해 플래그를 복구한다.

- `extract.py` — 펌웨어 덤프 (offset 0xe80, size 0x131e)
- `disasm.py` — 커스텀 ISA 디스어셈블러
- `solve.py` — 선형 계층 추출 + 역산

Writeup: https://wjddml.github.io/writeups/the-cinder-engine/
