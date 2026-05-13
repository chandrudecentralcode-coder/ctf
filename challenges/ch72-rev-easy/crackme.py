#!/usr/bin/env python3
# crackme.py — License Validator v0.1
# Challenge: Find the valid license key.
import sys

# Obfuscated license token (do not modify)
_SECRET = "pbqrs{f1zcy3_e3i3ef1at}"

def _transform(s: str) -> str:
    """Apply character transformation to input."""
    out = []
    for c in s:
        if 'a' <= c <= 'z':
            out.append(chr((ord(c) - ord('a') + 13) % 26 + ord('a')))
        elif 'A' <= c <= 'Z':
            out.append(chr((ord(c) - ord('A') + 13) % 26 + ord('A')))
        else:
            out.append(c)
    return ''.join(out)

def validate(key: str) -> bool:
    return _transform(key) == _SECRET

if __name__ == "__main__":
    print("=== License Validator v0.1 ===")
    key = input("Enter license key: ").strip()
    if validate(key):
        print("[+] License accepted. Access granted.")
    else:
        print("[-] Invalid key.")
        sys.exit(1)
