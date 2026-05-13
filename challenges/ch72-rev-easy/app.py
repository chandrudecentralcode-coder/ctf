from flask import Flask, render_template_string, send_file
import os

app = Flask(__name__)

FLAG = "codef{s1mpl3_r3v3rs1ng}"
SCRIPT = os.path.join(os.path.dirname(__file__), "crackme.py")

S = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Crackme 101 | COEDF CTF 2026</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',monospace;background:#060a12;color:#ddeeff;min-height:100vh;padding:30px 20px}
.wrap{max-width:860px;margin:0 auto}
.nav{display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:14px;border-bottom:1px solid #1a2a45}
.nav-brand{color:#00d4ff;font-weight:900;font-size:1.1rem}
h1{color:#c060ff;font-size:1.6rem;margin-bottom:8px;text-shadow:0 0 14px rgba(180,0,255,.4)}
.pts{color:#f0a040;font-weight:700;margin-bottom:20px;font-size:.9rem}
.card{background:#0e1829;border:1px solid #1a2a45;border-radius:10px;padding:22px;margin-bottom:18px}
.card h3{color:#c060ff;font-size:1rem;margin-bottom:12px}
pre{background:#000d1a;border:1px solid #1a2a45;border-radius:6px;padding:14px;font-family:monospace;font-size:.8rem;color:#aac8e8;overflow-x:auto;line-height:1.7}
.step{background:#060a12;border-left:3px solid #c060ff;padding:8px 14px;margin:6px 0;font-size:.82rem;color:#aac8e8}
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

PREVIEW = """\
#!/usr/bin/env python3
# crackme.py — License Validator v0.1

_SECRET = "pbqrs{f1zcy3_e3i3ef1at}"

def _transform(s: str) -> str:
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
# ... (download for full source)"""


@app.route("/download")
def download():
    return send_file(SCRIPT, as_attachment=True, download_name="crackme.py", mimetype="text/plain")


@app.route("/")
def index():
    return render_template_string(S + f"""
<div class="nav">
    <span class="nav-brand">⚙️ COEDF CTF 2026</span>
    <span style="font-size:.72rem;background:rgba(180,0,255,.1);color:#c060ff;border:1px solid rgba(180,0,255,.3);padding:3px 10px;border-radius:20px;font-weight:700">Reverse Engineering</span>
    <span style="font-size:.72rem;color:#39ff14">Easy — 75 pts</span>
</div>
<h1>🔍 Crackme 101</h1>
<div class="pts">⭐ 75 points &nbsp;|&nbsp; Reverse Engineering &nbsp;|&nbsp; Easy</div>

<div class="card">
    <h3>Challenge Description</h3>
    <p style="color:#aac8e8;font-size:.88rem;line-height:1.7">
        A license validator script was found on a compromised machine. It checks a secret key using
        a character transformation. Download the script, read the source code, reverse the
        <code>_transform</code> function, and determine what input produces a successful validation.
        The flag is the valid license key.
    </p>
</div>

<div class="card">
    <h3>📥 Download Script</h3>
    <a class="btn-dl" href="/download">⬇ Download crackme.py</a>
</div>

""" + FOOTER)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
