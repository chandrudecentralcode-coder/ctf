from flask import Flask, request, render_template_string
import jwt

app = Flask(__name__)
SECRET = "weaksecret"

S = """<style>
body{font-family:monospace;background:#0d1117;color:#c9d1d9;max-width:820px;margin:40px auto;padding:20px}
h1{color:#58a6ff;border-bottom:1px solid #21262d;padding-bottom:8px}
.card{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:22px;margin:14px 0}
.flag{background:#0f5132;border:1px solid #3fb950;padding:14px;border-radius:6px;font-size:1.1em;letter-spacing:.5px}
.token-box{background:#0d1117;border:1px solid #30363d;padding:12px;border-radius:6px;
            word-break:break-all;font-size:.9em;color:#79c0ff;line-height:1.6}
input{background:#0d1117;color:#c9d1d9;border:1px solid #30363d;padding:9px 12px;
      border-radius:6px;width:100%;box-sizing:border-box;font-family:monospace;margin-bottom:10px}
input:focus{outline:none;border-color:#58a6ff}
button{background:#1f6feb;color:white;border:none;padding:9px 18px;border-radius:6px;cursor:pointer;font-family:monospace}
.err{color:#f85149}
.warn{color:#9e6a03}
code{background:#21262d;padding:2px 6px;border-radius:4px}
.step{background:#161b22;border-left:3px solid #9e6a03;padding:8px 14px;margin:6px 0;font-size:.85em}
</style>"""


@app.route("/")
def index():
    token = jwt.encode({"username": "player", "role": "user"}, SECRET, algorithm="HS256")
    return render_template_string(S + """
<h1>🔑 JWT Auth Demo</h1>
<div class="card">
  <h4>Your token (role: user)</h4>
  <div class="token-box">{{ token }}</div>
  <p style="color:#8b949e;font-size:.85em;margin-top:10px">
    This token is signed with HMAC-SHA256 using a weak secret key.
    Decode it, change <code>role</code> to <code>admin</code>, re-sign with the cracked secret,
    then submit the forged token to <a href="/admin">/admin</a>.
  </p>
</div>
<div class="card">
  <h4>How to crack & forge</h4>
  <div class="step">1. Decode on jwt.io (or use python-jwt / hashcat)</div>
  <div class="step">2. Crack the HS256 secret (it's a common word)</div>
  <div class="step">3. Change payload: <code>"role": "admin"</code></div>
  <div class="step">4. Re-sign with the same secret and HS256 algorithm</div>
  <div class="step">5. Submit your forged token below</div>
</div>
<div class="card">
  <h4>Test admin access</h4>
  <form method="GET" action="/admin">
    <input name="token" placeholder="Paste your forged JWT token here">
    <button type="submit">Submit Token</button>
  </form>
</div>
""", token=token)


@app.route("/admin")
def admin():
    token = request.args.get("token", "").strip()

    if not token:
        return render_template_string(S + """
<h1>🔒 Admin Panel</h1>
<div class="card"><p class="err">No token provided.</p>
<p><a href="/" style="color:#58a6ff">← Get a token</a></p></div>""")

    try:
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return render_template_string(S + """<div class="card"><p class="err">Token has expired.</p></div>""")
    except jwt.InvalidTokenError as e:
        return render_template_string(S + f"""
<h1>🚫 Token Invalid</h1>
<div class="card">
  <p class="err">JWT error: {e}</p>
  <p class="warn">Make sure you're signing with the correct algorithm and secret.</p>
  <p><a href="/" style="color:#58a6ff">← Try again</a></p>
</div>""")

    if data.get("role") == "admin":
        return render_template_string(S + """
<h1>✅ Admin Panel</h1>
<div class="card">
  <p>Welcome, <strong>{{ data.username }}</strong>!</p>
  <p>You successfully forged a JWT token with elevated privileges.</p>
  <hr style="border-color:#21262d;margin:12px 0">
  <div class="flag">flag{jwt_role_admin_bypass}</div>
</div>""", data=data)

    return render_template_string(S + """
<h1>🚫 Access Denied</h1>
<div class="card">
  <p class="err">Token is valid but role is <strong>{{ data.role }}</strong>. Admin required.</p>
  <p>Decoded payload: <code>{{ data }}</code></p>
  <p><a href="/" style="color:#58a6ff">← Try again</a></p>
</div>""", data=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
