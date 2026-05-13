from flask import Flask, render_template_string

app = Flask(__name__)

S = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Weak RSA | COEDF CTF 2026</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',monospace;background:#060a12;color:#ddeeff;min-height:100vh;padding:30px 20px}
.wrap{max-width:860px;margin:0 auto}
.nav{display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:14px;border-bottom:1px solid #1a2a45}
.nav-brand{color:#00d4ff;font-weight:900;font-size:1.1rem}
.nav-cat{font-size:.72rem;background:rgba(255,215,0,.1);color:#ffd700;border:1px solid rgba(255,215,0,.3);padding:3px 10px;border-radius:20px;font-weight:700}
.nav-diff{font-size:.72rem;background:rgba(255,0,60,.1);color:#ff5252;border:1px solid rgba(255,0,60,.3);padding:3px 10px;border-radius:20px;font-weight:700}
h1{color:#ffd700;font-size:1.6rem;margin-bottom:8px;text-shadow:0 0 14px rgba(255,215,0,.4)}
.pts{color:#f0a040;font-weight:700;margin-bottom:20px;font-size:.9rem}
.card{background:#0e1829;border:1px solid #1a2a45;border-radius:10px;padding:22px;margin-bottom:18px}
.card h3{color:#ffd700;font-size:1rem;margin-bottom:12px}
.param{font-family:monospace;font-size:.85rem;background:#060a12;border:1px solid #1a2a45;border-radius:6px;padding:14px;color:#79c0ff;line-height:1.8;word-break:break-all}
.step{background:#060a12;border-left:3px solid #ffd700;padding:8px 14px;margin:6px 0;font-size:.82rem;color:#aac8e8}
input{background:rgba(255,255,255,.04);color:#39ff14;border:1px solid rgba(57,255,20,.3);padding:10px 14px;border-radius:6px;width:100%;font-family:monospace;font-size:.95rem;outline:none;transition:border-color .2s}
input:focus{border-color:#39ff14}
input::placeholder{color:#6b8aaa}
.btn{background:linear-gradient(135deg,#ffd700,#f0a040);color:#000;border:none;padding:10px 28px;border-radius:6px;font-weight:700;cursor:pointer;font-size:.9rem;margin-top:8px}
.flag-box{background:#0a1f0a;border:1px solid rgba(57,255,20,.4);border-radius:6px;padding:14px;font-family:monospace;color:#39ff14;font-size:1.05rem;letter-spacing:.06em;text-shadow:0 0 8px rgba(57,255,20,.5)}
.err{color:#ff5252;font-size:.88rem;margin-top:8px}
code{background:rgba(121,192,255,.1);color:#79c0ff;padding:2px 6px;border-radius:4px;font-size:.85em}
</style></head><body><div class="wrap">"""

FOOTER = "</div></body></html>"

# Small RSA parameters for educational challenge
# p=61, q=53, n=3233, e=17, d=2753
# message: 42 → ciphertext = pow(42, 17, 3233) = 2557
N = 3233
E = 17
CIPHERTEXT = 2557
FLAG = "codef{rsa_small_n_factored_easily}"


@app.route("/")
def index():
    return render_template_string(S + f"""
<div class="nav">
    <span class="nav-brand">🔑 COEDF CTF 2026</span>
    <span class="nav-cat">Cryptography</span>
    <span class="nav-diff">Hard — 250 pts</span>
</div>

<h1>🔓 Weak RSA</h1>
<div class="pts">⭐ 250 points &nbsp;|&nbsp; Category: Cryptography &nbsp;|&nbsp; Difficulty: Hard</div>

<div class="card">
    <h3>Challenge Description</h3>
    <p style="color:#aac8e8;font-size:.88rem;line-height:1.7;margin-bottom:12px">
        A developer implemented RSA encryption but used a dangerously small modulus N.
        The RSA modulus N = p × q where p and q are both small prime numbers — easy to factor.
        Once you factor N and recover the private key d, decrypt the ciphertext to get the flag.
    </p>
</div>

<div class="card">
    <h3>RSA Public Key Parameters</h3>
    <div class="param">
N (modulus)    = {N}  ← VERY small, easily factorable!<br>
e (public exp) = {E}<br>
C (ciphertext) = {CIPHERTEXT}<br><br>
Encryption: C = M^e mod N<br>
Decryption: M = C^d mod N<br>
Key gen:     d = e⁻¹ mod φ(N)  where φ(N) = (p-1)(q-1)
    </div>
</div>

""" + FOOTER)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
