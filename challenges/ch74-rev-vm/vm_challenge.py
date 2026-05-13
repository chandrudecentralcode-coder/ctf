#!/usr/bin/env python3
"""
vm_challenge.py — Custom Stack VM
The flag has been compiled into bytecode for a custom stack-based virtual machine.
Reverse the VM instruction set and execute the bytecode mentally to recover the flag.
"""

# VM Instruction set
NOP  = 0x00
PUSH = 0x01  # PUSH <byte>
POP  = 0x02
ADD  = 0x03  # stack[-2] + stack[-1]
XOR  = 0x04  # stack[-2] ^ stack[-1]
ROT  = 0x05  # rotate top 2 items
DUP  = 0x06  # duplicate top
EMIT = 0x07  # pop and store as output char
HLT  = 0xFF  # halt

# Bytecode program — "computes" the flag character by character
BYTECODE = bytes([
    # 'c' = 0x63 = 0x51 ^ 0x32
    PUSH, 0x51, PUSH, 0x32, XOR, EMIT,
    # 'o' = 0x6f = 0x40 ^ 0x2f
    PUSH, 0x40, PUSH, 0x2f, XOR, EMIT,
    # 'd' = 0x64 = 0x71 ^ 0x15
    PUSH, 0x71, PUSH, 0x15, XOR, EMIT,
    # 'e' = 0x65 = 0x04 + 0x61
    PUSH, 0x04, PUSH, 0x61, ADD, EMIT,
    # 'f' = 0x66 = 0x60 ^ 0x06
    PUSH, 0x60, PUSH, 0x06, XOR, EMIT,
    # '{' = 0x7b = 0x7b ^ 0x00
    PUSH, 0x7b, PUSH, 0x00, XOR, EMIT,
    # 'v' = 0x76 = 0x37 + 0x3f
    PUSH, 0x37, PUSH, 0x3f, ADD, EMIT,
    # 'm' = 0x6d = 0x5a ^ 0x37
    PUSH, 0x5a, PUSH, 0x37, XOR, EMIT,
    # '_' = 0x5f = 0x1f ^ 0x40
    PUSH, 0x1f, PUSH, 0x40, XOR, EMIT,
    # 'r' = 0x72 = 0x72 ^ 0x00
    PUSH, 0x72, PUSH, 0x00, XOR, EMIT,
    # '3' = 0x33 = 0x10 + 0x23
    PUSH, 0x10, PUSH, 0x23, ADD, EMIT,
    # 'v' = 0x76 = 0x37 + 0x3f
    PUSH, 0x37, PUSH, 0x3f, ADD, EMIT,
    # '_' = 0x5f
    PUSH, 0x5f, PUSH, 0x00, XOR, EMIT,
    # 'b' = 0x62 = 0x62 ^ 0x00
    PUSH, 0x62, PUSH, 0x00, XOR, EMIT,
    # 'y' = 0x79 = 0x40 + 0x39
    PUSH, 0x40, PUSH, 0x39, ADD, EMIT,
    # 't' = 0x74
    PUSH, 0x74, PUSH, 0x00, XOR, EMIT,
    # 'e' = 0x65
    PUSH, 0x65, PUSH, 0x00, XOR, EMIT,
    # 'c' = 0x63
    PUSH, 0x51, PUSH, 0x32, XOR, EMIT,
    # '0' = 0x30
    PUSH, 0x18, PUSH, 0x18, ADD, EMIT,
    # 'd' = 0x64
    PUSH, 0x71, PUSH, 0x15, XOR, EMIT,
    # 'e' = 0x65
    PUSH, 0x04, PUSH, 0x61, ADD, EMIT,
    # '_' = 0x5f
    PUSH, 0x5f, PUSH, 0x00, XOR, EMIT,
    # 'c' = 0x63
    PUSH, 0x51, PUSH, 0x32, XOR, EMIT,
    # 'r' = 0x72
    PUSH, 0x72, PUSH, 0x00, XOR, EMIT,
    # '4' = 0x34
    PUSH, 0x1a, PUSH, 0x1a, ADD, EMIT,
    # 'c' = 0x63
    PUSH, 0x51, PUSH, 0x32, XOR, EMIT,
    # 'k' = 0x6b = 0x30 + 0x3b
    PUSH, 0x30, PUSH, 0x3b, ADD, EMIT,
    # '3' = 0x33
    PUSH, 0x10, PUSH, 0x23, ADD, EMIT,
    # 'd' = 0x64
    PUSH, 0x71, PUSH, 0x15, XOR, EMIT,
    # '}' = 0x7d
    PUSH, 0x7d, PUSH, 0x00, XOR, EMIT,
    HLT,
])

def run_vm(code: bytes) -> str:
    stack = []
    output = []
    ip = 0
    while ip < len(code):
        op = code[ip]; ip += 1
        if   op == NOP:  pass
        elif op == PUSH: stack.append(code[ip]); ip += 1
        elif op == POP:  stack.pop()
        elif op == ADD:  b = stack.pop(); a = stack.pop(); stack.append((a + b) & 0xff)
        elif op == XOR:  b = stack.pop(); a = stack.pop(); stack.append(a ^ b)
        elif op == ROT:  a = stack.pop(); b = stack.pop(); stack.append(a); stack.append(b)
        elif op == DUP:  stack.append(stack[-1])
        elif op == EMIT: output.append(chr(stack.pop()))
        elif op == HLT:  break
    return ''.join(output)

def check_flag(user_input: str) -> bool:
    return user_input == run_vm(BYTECODE)

if __name__ == "__main__":
    print("=== Custom VM Challenge ===")
    print(f"Bytecode length: {len(BYTECODE)} bytes")
    print(f"Instructions: NOP=0x00 PUSH=0x01 POP=0x02 ADD=0x03 XOR=0x04 ROT=0x05 DUP=0x06 EMIT=0x07 HLT=0xFF")
    print()
    answer = input("Enter the flag computed by the VM: ").strip()
    if check_flag(answer):
        print("[+] Correct!")
    else:
        print("[-] Incorrect.")
