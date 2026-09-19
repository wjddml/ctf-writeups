import struct

REG = {
 0x06:("ROR32","r{A}, {imm}"), 0x0C:("MODE_STACK",""),
 0x16:("XOR","r{A}, r{B}"),    0x25:("SHL","r{A}, {imm}"),
 0x2E:("JF","{imm}"),          0x31:("MOV","r{A}, KEY"),
 0x39:("MOV","r{A}, r{B}"),    0x43:("CMPI","r{A}, {imm}"),
 0x4B:("ADD","r{A}, r{B}"),    0x52:("MUL","r{A}, {imm}"),
 0x5F:("INPUT","r{A}"),        0x69:("ROL64","r{A}, {imm}"),
 0x71:("ROL32","r{A}, {imm}"), 0x7B:("SUBMIT","{imm}"),
 0x8D:("XOR","r{A}, {imm}"),   0x95:("JMP","{imm}"),
 0x9A:("ROR64","r{A}, {imm}"), 0xA7:("MOV","r{A}, {imm}"),
 0xB4:("SHR","r{A}, {imm}"),   0xBC:("JT","{imm}"),
 0xC3:("MUL","r{A}, r{B}"),    0xCA:("MOV","r{A}, SEED"),
 0xD2:("LD8","r{A}, data[r{B}+{imm}]"), 0xDD:("CMP","r{A}, r{B}"),
 0xE1:("FLAG",""),             0xE8:("AND","r{A}, {imm}"),
 0xF0:("ADD","r{A}, {imm}"),   0xF7:("HALT",""),
}
STK = {
 0x0F:"LD8", 0xC8:"LD16", 0xA3:"LD64BE", 0x75:"LD64LE",
 0x9D:"PUSH r{A}", 0x23:"POP r{A}", 0x44:"PUSHI {imm}",
 0xF2:"DUP", 0xB1:"DROP", 0x68:"SWAP",
 0x37:"ADD", 0xDE:"SUB", 0x19:"MUL", 0x6B:"MOD",
 0x82:"XOR", 0xEF:"AND", 0x56:"OR",
 0xC1:"SHL", 0x2A:"SHR", 0x97:"ROL", 0x4C:"ROR",
 0x14:"EQ", 0x30:"JMP {imm}", 0xAB:"JZ {imm}", 0x7E:"JNZ {imm}",
 0x5C:"HALT", 0xFA:"MODE_REG",
}
FMT = {0:"raw", 1:"hex8", 2:"hex16", 3:"hex32", 4:"dec"}

code = open("code.bin","rb").read()
data = open("data.bin","rb").read()
sat = lambda o: data[o:data.find(b"\0", o)].decode("latin1","replace")

stack_mode = False
for pc in range(len(code)//12):
    op, A, B, C = code[12*pc:12*pc+4]
    imm = struct.unpack_from("<Q", code, 12*pc+4)[0]

    if stack_mode:
        t = STK.get(op, f"OP_{op:02X}")
        line = t.format(A=A, B=B, imm=hex(imm))
        if op == 0xFA: stack_mode = False
    else:
        mn, ops = REG.get(op, (f"OP_{op:02X}", "A={A} B={B} imm={imm}"))
        line = (mn + " " + ops).format(A=A, B=B, imm=hex(imm))
        if op == 0x5F:
            line += f'   ; fmt={FMT.get(B,B)} max={C} "{sat(imm)[:48]}"'
        if op == 0x0C: stack_mode = True

    mark = "  <<<" if op in (0x7B, 0xE1) else ""
    print(f"{pc:04x}: {op:02X} {A:3} {B:3} {C:3} {imm:#018x}  {line}{mark}")
