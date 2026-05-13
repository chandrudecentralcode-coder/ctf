from flask import Flask, render_template_string

app = Flask(__name__)

S = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Caesar Cipher | COEDF CTF 2026</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',monospace;background:#060a12;color:#ddeeff;min-height:100vh;padding:30px 20px}
.wrap{max-width:820px;margin:0 auto}
.nav{display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:14px;border-bottom:1px solid #1a2a45}
.nav-brand{color:#00d4ff;font-weight:900;font-size:1.1rem;letter-spacing:.06em}
.nav-cat{font-size:.72rem;background:rgba(255,215,0,.1);color:#ffd700;border:1px solid rgba(255,215,0,.3);padding:3px 10px;border-radius:20px;font-weight:700;letter-spacing:.1em}
.nav-diff{font-size:.72rem;background:rgba(57,255,20,.1);color:#39ff14;border:1px solid rgba(57,255,20,.3);padding:3px 10px;border-radius:20px;font-weight:700}
h1{color:#ffd700;font-size:1.6rem;margin-bottom:8px;text-shadow:0 0 14px rgba(255,215,0,.4)}
.pts{color:#f0a040;font-weight:700;margin-bottom:20px;font-size:.9rem}
.card{background:#0e1829;border:1px solid #1a2a45;border-radius:10px;padding:22px;margin-bottom:18px}
.card h3{color:#00d4ff;font-size:1rem;margin-bottom:12px;letter-spacing:.06em}
.cipher{font-family:monospace;font-size:1.15rem;color:#fff;background:#060a12;border:1px solid #1a2a45;border-radius:6px;padding:16px;letter-spacing:.08em;word-break:break-all;margin-bottom:10px}
.hint{font-size:.8rem;color:#6b8aaa;line-height:1.6}
.step{background:#060a12;border-left:3px solid #ffd700;padding:8px 14px;margin:6px 0;font-size:.82rem;color:#aac8e8}
input{background:rgba(255,255,255,.04);color:#ddeeff;border:1px solid #1a2a45;padding:10px 14px;border-radius:6px;width:100%;font-family:monospace;font-size:.95rem;outline:none;transition:border-color .2s}
input:focus{border-color:#00d4ff}
input::placeholder{color:#6b8aaa}
.btn{background:linear-gradient(135deg,#ffd700,#f0a040);color:#000;border:none;padding:10px 28px;border-radius:6px;font-weight:700;cursor:pointer;font-size:.9rem;margin-top:8px}
.btn:hover{opacity:.9}
.flag-box{background:#0a1f0a;border:1px solid rgba(57,255,20,.4);border-radius:6px;padding:14px;font-family:monospace;color:#39ff14;font-size:1.05rem;letter-spacing:.06em;text-shadow:0 0 8px rgba(57,255,20,.5)}
.err{color:#ff5252;font-size:.88rem;margin-top:8px}
.ok{color:#39ff14;font-size:.88rem;margin-top:8px}
table{width:100%;border-collapse:collapse;font-size:.82rem}
th{color:#6b8aaa;padding:6px 10px;border-bottom:1px solid #1a2a45;text-align:left}
td{padding:5px 10px;color:#aac8e8;border-bottom:1px solid rgba(255,255,255,.03);font-family:monospace}
</style></head><body><div class="wrap">"""

FOOTER = "</div></body></html>"

CIPHERTEXT = "frqjudwxodwlrqv brx eurnhq wkh fdhvdu flskhu"
FLAG = "codef{congratulations_you_broken_the_caesar_cipher}"
SHIFT = 3


def caesar_decrypt(text, shift):
    result = []
    for c in text:
        if c.isalpha():
            base = ord('a') if c.islower() else ord('A')
            result.append(chr((ord(c) - base - shift) % 26 + base))
        else:
            result.append(c)
    return ''.join(result)


@app.route("/")
def index():
    return render_template_string(S + f"""
<div class="nav">
    <span class="nav-brand">🔐 COEDF CTF 2026</span>
    <span class="nav-cat">Cryptography</span>
    <span class="nav-diff">Easy — 75 pts</span>
</div>

<h1>🔑 Caesar Cipher</h1>
<div class="pts">⭐ 75 points &nbsp;|&nbsp; Category: Cryptography &nbsp;|&nbsp; Difficulty: Easy</div>

<div class="card">
    <h3>Challenge Description</h3>
    <p style="color:#aac8e8;font-size:.88rem;line-height:1.7;margin-bottom:14px">
        An intercepted message was encrypted using the ancient Caesar cipher — a simple substitution
        cipher where each letter is shifted by a fixed number of positions in the alphabet.
        The plaintext is an English sentence. Decrypt it and submit the decoded text as the flag.
    </p>
    <div class="hint">Flag format: <code style="color:#39ff14">codef{{the_decrypted_message_with_underscores}}</code></div>
</div>

<div class="card">
    <h3>Intercepted Ciphertext</h3>
    <div class="cipher">{CIPHERTEXT}</div>
    <div class="hint">The cipher uses a fixed shift applied to each alphabetic character. Spaces are preserved.</div>
</div>

""" + FOOTER)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
