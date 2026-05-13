from flask import Flask, render_template_string, send_file
import os

app = Flask(__name__)

FLAG = "codef{vm_r3v_bytec0de_cr4ck3d}"
VM_FILE = os.path.join(os.path.dirname(__file__), "vm_challenge.py")

S = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Custom VM | COEDF CTF 2026</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',monospace;background:#060a12;color:#ddeeff;min-height:100vh;padding:30px 20px}
.wrap{max-width:900px;margin:0 auto}
.nav{display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:14px;border-bottom:1px solid #1a2a45}
.nav-brand{color:#00d4ff;font-weight:900;font-size:1.1rem}
h1{color:#c060ff;font-size:1.6rem;margin-bottom:8px;text-shadow:0 0 14px rgba(180,0,255,.4)}
.pts{color:#f0a040;font-weight:700;margin-bottom:20px;font-size:.9rem}
.card{background:#0e1829;border:1px solid #1a2a45;border-radius:10px;padding:22px;margin-bottom:18px}
.card h3{color:#c060ff;font-size:1rem;margin-bottom:12px}
pre{background:#000d1a;border:1px solid #1a2a45;border-radius:6px;padding:14px;font-family:monospace;font-size:.75rem;color:#aac8e8;overflow-x:auto;line-height:1.75;max-height:320px;overflow-y:auto}
.step{background:#060a12;border-left:3px solid #c060ff;padding:8px 14px;margin:6px 0;font-size:.82rem;color:#aac8e8}
.op-table{width:100%;border-collapse:collapse;font-size:.8rem;margin-top:8px}
.op-table th{color:#6b8aaa;padding:6px 10px;border-bottom:1px solid #1a2a45;text-align:left}
.op-table td{padding:5px 10px;border-bottom:1px solid rgba(255,255,255,.03);font-family:monospace;color:#aac8e8}
.op-table td:first-child{color:#c060ff;font-weight:700}
input{background:rgba(255,255,255,.04);color:#39ff14;border:1px solid rgba(57,255,20,.3);padding:10px 14px;border-radius:6px;width:100%;font-family:monospace;font-size:.95rem;outline:none}
input:focus{border-color:#39ff14}
input::placeholder{color:#6b8aaa}
.btn{background:linear-gradient(135deg,#c060ff,#8000c0);color:#fff;border:none;padding:10px 28px;border-radius:6px;font-weight:700;cursor:pointer;font-size:.9rem;margin-top:8px}
.btn-dl{display:inline-block;background:linear-gradient(135deg,#1a6bff,#004de0);color:#fff;text-decoration:none;padding:12px 32px;border-radius:6px;font-weight:700;font-size:.95rem;margin-top:4px}
.flag-box{background:#0a1f0a;border:1px solid rgba(57,255,20,.4);border-radius:6px;padding:14px;font-family:monospace;color:#39ff14;font-size:1.05rem;margin-top:8px}
.err{color:#ff5252;font-size:.88rem;margin-top:8px}
code{background:rgba(121,192,255,.1);color:#79c0ff;padding:2px 6px;border-radius:4px;font-size:.85em}
</style></head><body><div class="wrap">"""
FOOTER = "</div></body></html>"

BYTECODE_HEX = """
BYTECODE (181 bytes):

Offset  Hex  Mnemonic
------  ---  ----------------------------
0x000   01   PUSH 0x51
0x002   01   PUSH 0x32
0x004   04   XOR          ; 0x51^0x32 = ?
0x005   07   EMIT         ; output char
0x006   01   PUSH 0x40
0x008   01   PUSH 0x2f
0x00a   04   XOR          ; emit next char
0x00b   07   EMIT
... (30 EMIT instructions total)
0xb4    FF   HLT
"""


@app.route("/download")
def download():
    return send_file(VM_FILE, as_attachment=True, download_name="vm_challenge.py", mimetype="text/plain")


@app.route("/")
def index():
    return render_template_string(S + f"""
<div class="nav">
    <span class="nav-brand">⚙️ COEDF CTF 2026</span>
    <span style="font-size:.72rem;background:rgba(180,0,255,.1);color:#c060ff;border:1px solid rgba(180,0,255,.3);padding:3px 10px;border-radius:20px;font-weight:700">Reverse Engineering</span>
    <span style="font-size:.72rem;color:#ff5252">Hard — 250 pts</span>
</div>
<h1>🤖 Custom VM</h1>
<div class="pts">⭐ 250 points &nbsp;|&nbsp; Reverse Engineering &nbsp;|&nbsp; Hard</div>

<div class="card">
    <h3>Challenge Description</h3>
    <p style="color:#aac8e8;font-size:.88rem;line-height:1.7">
        A custom stack-based virtual machine was recovered from a protected application. The flag has
        been <strong style="color:#c060ff">compiled into VM bytecode</strong> — it is never stored as
        plaintext. The VM executes arithmetic and logic operations on a stack and emits characters one
        at a time to produce the flag. Download the VM, understand the instruction set, and manually
        (or programmatically) trace the bytecode execution to reconstruct the output.
    </p>
</div>

<div class="card">
    <h3>📥 Download VM Challenge</h3>
    <a class="btn-dl" href="/download">⬇ Download vm_challenge.py</a>
</div>

""" + FOOTER)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
