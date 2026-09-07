FILE_PATH = 'the_cinder_engine/cinder'
OFFSET = 0xe80
SIZE = 0x131e

with open(FILE_PATH, 'rb') as f:
    f.seek(OFFSET)
    firmware_data = f.read(SIZE)

with open('firmware.bin', 'wb') as out:
    out.write(firmware_data)

print(f"[*] 펌웨어 덤프 완료! 크기: {len(firmware_data)} bytes")
