from flask import Flask, request, render_template_string, make_response

app = Flask(__name__)

S = """<style>
body{font-family:Arial;background:#0d1117;color:#c9d1d9;max-width:700px;margin:60px auto;padding:20px}
h1{color:#58a6ff}
.card{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:24px;margin:14px 0}
.flag{background:#0f5132;border:1px solid #3fb950;padding:14px;border-radius:6px;
       font-family:monospace;font-size:1.1em;letter-spacing:.5px}
.role-user{color:#1f6feb;font-weight:bold}
.role-admin{color:#3fb950;font-weight:bold}
code{background:#21262d;padding:2px 6px;border-radius:4px;font-family:monospace}
.step{background:#161b22;border-left:3px solid #9e6a03;padding:10px 14px;margin:6px 0;font-size:.9em}
</style>"""


@app.route("/")
def index():
    role = request.cookies.get("role", "user")

    if role == "admin":
        resp = make_response(render_template_string(S + """
<h1>⚙️ Admin Dashboard</h1>
<div class="card">
  <p>Current role: <span class="role-admin">ADMIN</span></p>
  <p>You successfully escalated your privileges via cookie manipulation!</p>
  <hr style="border-color:#21262d;margin:14px 0">
  <div class="flag">flag{cookie_role_admin}</div>
</div>
"""))
    else:
        resp = make_response(render_template_string(S + """
<h1>🌐 UserPortal</h1>
<div class="card">
  <p>Current role: <span class="role-user">{{ role }}</span></p>
  <p>Welcome! You are in the standard user area. Admin content is restricted.</p>
  <hr style="border-color:#21262d;margin:14px 0">
  <p style="color:#8b949e;font-size:.9em"><strong>Hint:</strong> Your role is controlled by a cookie named <code>role</code>.
  Change its value to gain elevated access.</p>
  <div class="step">1. Open DevTools (F12) → Application tab → Cookies</div>
  <div class="step">2. Find the cookie named <code>role</code> with value <code>user</code></div>
  <div class="step">3. Double-click the value and change it to <code>admin</code></div>
  <div class="step">4. Refresh the page</div>
</div>
""", role=role))
        resp.set_cookie("role", "user", httponly=False, samesite="Lax")

    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
