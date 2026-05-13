from flask import Flask, request, render_template_string, session, redirect, jsonify

app = Flask(__name__)
app.secret_key = "ch50-idor-secret"

USERS = {
    "1": {"username": "admin",  "password": "adminXx9!#2", "role": "admin"},
    "2": {"username": "player", "password": "player123",   "role": "user"},
}

DOCUMENTS = {
    "DOC-8821-ALPHA": {
        "owner": "1", "title": "Q1 Confidential Report",
        "content": "codef{advanced_idor_access_granted}",
        "date": "2024-01-15", "classification": "SECRET"
    },
    "DOC-1105-BETA": {
        "owner": "2", "title": "My Personal Notes",
        "content": "Meeting at 3pm. Remember to review the sprint backlog.",
        "date": "2024-03-20", "classification": "INTERNAL"
    },
}

AUDIT_LOG = [
    {"action": "VIEW",  "user": "admin",  "doc_id": "DOC-8821-ALPHA", "ts": "2024-04-01 09:12:33"},
    {"action": "EDIT",  "user": "admin",  "doc_id": "DOC-8821-ALPHA", "ts": "2024-04-01 11:05:44"},
    {"action": "VIEW",  "user": "player", "doc_id": "DOC-1105-BETA",  "ts": "2024-04-01 14:20:11"},
    {"action": "VIEW",  "user": "admin",  "doc_id": "DOC-8821-ALPHA", "ts": "2024-04-02 08:55:03"},
]

S = """<style>
body{font-family:Arial;background:#0d1117;color:#c9d1d9;max-width:960px;margin:40px auto;padding:20px}
h1{color:#58a6ff}
nav{margin-bottom:20px;color:#8b949e}
nav a{color:#58a6ff;text-decoration:none;margin-right:15px}
.card{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:20px;margin:12px 0}
table{width:100%;border-collapse:collapse}
th{background:#21262d;padding:10px 12px;text-align:left;font-size:.85em;color:#8b949e;text-transform:uppercase}
td{padding:10px 12px;border-bottom:1px solid #21262d;font-size:.9em}
a.btn{background:#1f6feb;color:white;padding:5px 12px;border-radius:4px;text-decoration:none;font-size:.85em}
.flag{background:#0f5132;border:1px solid #3fb950;padding:14px;border-radius:6px;font-family:monospace;font-size:1.1em}
code{background:#21262d;padding:2px 6px;border-radius:4px;font-family:monospace;font-size:.9em}
.badge-secret{color:#f85149;font-weight:bold;font-size:.8em}
.badge-internal{color:#9e6a03;font-size:.8em}
input{background:#0d1117;color:#c9d1d9;border:1px solid #30363d;padding:9px 12px;border-radius:6px;width:220px}
button{background:#1f6feb;color:white;border:none;padding:9px 16px;border-radius:6px;cursor:pointer}
.hint-text{color:#8b949e;font-size:.85em;margin-top:8px}
</style>"""


@app.route("/")
def home():
    if "uid" not in session:
        return redirect("/login")
    uid  = session["uid"]
    user = USERS[uid]
    my_docs = [(did, doc) for did, doc in DOCUMENTS.items() if doc["owner"] == uid]
    return render_template_string(S + """
<h1>📁 DocVault</h1>
<nav>
  Welcome, <strong>{{ user.username }}</strong> ({{ user.role }}) &nbsp;|&nbsp;
  <a href="/api/audit">Audit Log</a> &nbsp;|&nbsp;
  <a href="/logout">Logout</a>
</nav>
<div class="card">
  <h4>Your Documents</h4>
  <table>
    <thead><tr><th>Document ID</th><th>Title</th><th>Classification</th><th>Date</th><th></th></tr></thead>
    <tbody>
    {% for did, doc in my_docs %}
      <tr>
        <td><code>{{ did }}</code></td>
        <td>{{ doc.title }}</td>
        <td><span class="badge-{{ doc.classification|lower }}">{{ doc.classification }}</span></td>
        <td>{{ doc.date }}</td>
        <td><a class="btn" href="/view/{{ did }}">View</a></td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
</div>
<div class="card">
  <h4>🔍 Quick Document Lookup</h4>
  <form method="GET" action="/view">
    <input name="id" placeholder="Enter Document ID">
    <button>Fetch</button>
  </form>
  <p class="hint-text">Hint: <a href="/api/audit">Check the audit log</a> to discover other document IDs in the system</p>
</div>
""", user=user, my_docs=my_docs)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u, p = request.form.get("username", ""), request.form.get("password", "")
        for uid, usr in USERS.items():
            if usr["username"] == u and usr["password"] == p:
                session["uid"] = uid
                return redirect("/")
        err = "<p style='color:#f85149;margin-top:10px'>Invalid credentials</p>"
    else:
        err = ""
    return render_template_string(S + f"""
<div style="max-width:360px;margin:80px auto">
  <h2>🔑 DocVault Login</h2>
  <div class="card">
    <form method="POST">
      <label style="color:#8b949e;font-size:.85em">Username</label><br>
      <input name="username" style="width:100%;margin-bottom:10px;box-sizing:border-box"><br>
      <label style="color:#8b949e;font-size:.85em">Password</label><br>
      <input name="password" type="password" style="width:100%;margin-bottom:14px;box-sizing:border-box"><br>
      <button style="width:100%">Login</button>
    </form>
    {err}
    <p style="color:#8b949e;font-size:.8em;margin-top:12px">Credentials: player / player123</p>
  </div>
</div>""")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/api/audit")
def audit():
    if "uid" not in session:
        return jsonify({"error": "login required"}), 401
    return jsonify(AUDIT_LOG)


@app.route("/view")
@app.route("/view/<doc_id>")
def view_doc(doc_id=None):
    if "uid" not in session:
        return redirect("/login")
    if doc_id is None:
        doc_id = request.args.get("id", "")
    if doc_id not in DOCUMENTS:
        return render_template_string(S + f"<div class='card'><p style='color:#f85149'>Document not found: {doc_id}</p><a href='/'>← Back</a></div>")
    doc = DOCUMENTS[doc_id]
    # Intentionally no ownership check — IDOR vulnerability
    return render_template_string(S + """
<h1>📄 {{ doc.title }}</h1>
<a href="/" style="color:#58a6ff">← Back to dashboard</a>
<div class="card" style="margin-top:12px">
  <table style="width:auto">
    <tr><td style="color:#8b949e;padding:6px 16px 6px 0">Document ID</td><td><code>{{ doc_id }}</code></td></tr>
    <tr><td style="color:#8b949e;padding:6px 16px 6px 0">Classification</td>
        <td><span class="badge-{{ doc.classification|lower }}">{{ doc.classification }}</span></td></tr>
    <tr><td style="color:#8b949e;padding:6px 16px 6px 0">Date</td><td>{{ doc.date }}</td></tr>
  </table>
  <hr style="border-color:#21262d;margin:14px 0">
  {% if 'codef{' in doc.content %}
    <div class="flag">{{ doc.content }}</div>
  {% else %}
    <p style="line-height:1.7">{{ doc.content }}</p>
  {% endif %}
</div>
""", doc=doc, doc_id=doc_id)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
