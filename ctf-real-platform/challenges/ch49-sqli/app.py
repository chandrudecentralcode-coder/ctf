from flask import Flask, request, render_template_string
import html

app = Flask(__name__)

BASE = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Admin Portal</title>
<style>
  body{margin:0;background:#0d1117;font-family:Arial;display:flex;
       justify-content:center;align-items:center;min-height:100vh;flex-direction:column}
  .card{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:32px;width:380px}
  h2{color:#58a6ff;text-align:center;margin-bottom:20px}
  label{color:#8b949e;font-size:.85em;display:block;margin-bottom:4px}
  input{width:100%;background:#0d1117;color:#c9d1d9;border:1px solid #30363d;
        padding:10px;border-radius:6px;margin-bottom:12px;font-size:1em;box-sizing:border-box}
  button{width:100%;background:#1f6feb;color:white;border:none;padding:12px;
         border-radius:6px;font-size:1em;cursor:pointer;font-weight:bold}
  .error{color:#f85149;text-align:center;margin-top:10px;font-size:.9em}
  .success{background:#0f5132;border:1px solid #3fb950;padding:14px;border-radius:6px;
            font-family:monospace;font-size:1.1em;margin-top:14px;text-align:center}
  .query-box{background:#0d1117;border:1px solid #21262d;padding:10px;border-radius:4px;
              font-family:monospace;font-size:.8em;color:#8b949e;margin-top:12px;word-break:break-all}
  .hint{color:#8b949e;font-size:.8em;text-align:center;margin-top:12px}
</style>
</head><body>"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template_string(BASE + """
<div class="card">
  <h2>🔐 Admin Portal</h2>
  <form method="POST">
    <label>Username</label>
    <input name="username" placeholder="Enter username" autocomplete="off">
    <label>Password</label>
    <input name="password" type="password" placeholder="Enter password">
    <button>Login</button>
  </form>
  <p class="hint">The database query uses raw string concatenation</p>
</div></body></html>""")

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    safe_u   = html.escape(username)
    query    = f"SELECT * FROM users WHERE username='{safe_u}' AND password='{html.escape(password)}'"

    bypassed = (
        "' --" in username or "' #" in username or
        "or 1=1" in username.lower() or
        "'or'" in username.replace(" ", "").lower() or
        "admin'--" in username.replace(" ", "").lower()
    )

    if bypassed:
        return render_template_string(BASE + f"""
<div class="card">
  <h2 style="color:#3fb950">✅ Login Bypassed!</h2>
  <p style="color:#c9d1d9;text-align:center">SQL injection successful. Welcome, admin.</p>
  <div class="query-box">Executed: {query}</div>
  <div class="success">flag{{sqli_login_bypass}}</div>
</div></body></html>""")

    return render_template_string(BASE + f"""
<div class="card">
  <h2>🔐 Admin Portal</h2>
  <form method="POST">
    <label>Username</label>
    <input name="username" value="{safe_u}" autocomplete="off">
    <label>Password</label>
    <input name="password" type="password">
    <button>Login</button>
  </form>
  <p class="error">Invalid credentials</p>
  <div class="query-box">Query: {query}</div>
  <p class="hint">Hint: try <code style="background:#21262d;padding:2px 5px">admin' --</code> as username</p>
</div></body></html>""")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
