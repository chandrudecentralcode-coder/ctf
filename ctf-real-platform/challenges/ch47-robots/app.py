from flask import Flask, render_template_string

app = Flask(__name__)

S = """<style>
body{font-family:monospace;background:#0d1117;color:#c9d1d9;max-width:800px;margin:40px auto;padding:20px}
h1{color:#58a6ff;border-bottom:1px solid #21262d;padding-bottom:8px}
nav a{color:#58a6ff;margin-right:15px;text-decoration:none}
.box{background:#161b22;border:1px solid #21262d;border-radius:6px;padding:20px;margin:15px 0}
.flag{background:#0f5132;border:1px solid #3fb950;padding:14px;border-radius:6px;font-size:1.1em;letter-spacing:.5px}
</style>"""


@app.route("/")
def home():
    return render_template_string(S + """
<h1>AcmeCorp</h1>
<nav><a href="/">Home</a><a href="/about">About</a><a href="/services">Services</a><a href="/robots.txt">robots.txt</a></nav>
<div class="box">
  <h2>Enterprise Solutions for Modern Business</h2>
  <p>Welcome to AcmeCorp. We deliver world-class software services.</p>
  <p>Our website is indexed by all major search engines — though some areas are restricted.</p>
</div>
<footer style="color:#8b949e;font-size:.85em;margin-top:40px">© 2024 AcmeCorp Inc.</footer>
""")


@app.route("/about")
def about():
    return render_template_string(S + "<h1>About AcmeCorp</h1><div class='box'><p>Founded in 2010. 500+ employees worldwide.</p></div>")


@app.route("/services")
def services():
    return render_template_string(S + "<h1>Services</h1><div class='box'><p>Cloud infrastructure, DevOps, Security consulting.</p></div>")


@app.route("/robots.txt")
def robots():
    content = (
        "User-agent: *\n"
        "Disallow: /tmp/\n"
        "Disallow: /backup/\n"
        "Disallow: /admin-secret-vault\n"
        "Disallow: /internal/\n"
    )
    return content, 200, {"Content-Type": "text/plain"}


@app.route("/admin-secret-vault")
def vault():
    return render_template_string(S + """
<h1>Admin Secret Vault</h1>
<div class="box">
  <p>This page was hidden from search engines via robots.txt — but you found it anyway.</p>
  <p style="color:#8b949e">Sometimes security through obscurity is the only protection...</p>
</div>
<div class="flag">flag{robots_txt_hidden_file_found}</div>
""")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
