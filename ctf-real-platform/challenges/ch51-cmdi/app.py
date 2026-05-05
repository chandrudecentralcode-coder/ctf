from flask import Flask, request, render_template_string
import subprocess
import os

app = Flask(__name__)

# Flag file lives at /app/flag.txt — inject a command to read it
with open("/app/flag.txt", "w") as _f:
    _f.write("flag{command_injection_success}\n")

S = """<style>
body{font-family:monospace;background:#0d1117;color:#c9d1d9;max-width:800px;margin:40px auto;padding:20px}
h1{color:#58a6ff;border-bottom:1px solid #21262d;padding-bottom:8px}
.card{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:20px;margin:14px 0}
input{background:#0d1117;color:#c9d1d9;border:1px solid #30363d;padding:9px 12px;
      border-radius:6px;width:280px;font-family:monospace}
input:focus{outline:none;border-color:#58a6ff}
button{background:#238636;color:white;border:none;padding:9px 18px;border-radius:6px;cursor:pointer;font-family:monospace}
pre{background:#0d1117;border:1px solid #21262d;padding:16px;border-radius:6px;
    overflow-x:auto;white-space:pre-wrap;max-height:400px;font-size:.9em}
.hint{color:#8b949e;font-size:.85em;margin-top:8px}
</style>"""


@app.route("/")
def index():
    host   = request.args.get("host", "").strip()
    output = ""
    error  = ""

    if host:
        try:
            # Intentionally vulnerable — shell=True with unsanitised input
            result = subprocess.run(
                f"ping -c 2 -W 1 {host}",
                shell=True, capture_output=True, text=True, timeout=8
            )
            output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            error = "Command timed out after 8 seconds."
        except Exception as e:
            error = str(e)

    return render_template_string(S + """
<h1>🌐 NetDiag — Network Diagnostics</h1>
<div class="card">
  <h4>Ping Tool</h4>
  <form method="GET">
    <input name="host" placeholder="hostname or IP" value="{{ host }}">
    <button type="submit">▶ Run</button>
  </form>
  <p class="hint">Try: 127.0.0.1 &nbsp;|&nbsp; Goal: read /app/flag.txt</p>
</div>
{% if output %}
<div class="card">
  <strong>$ ping -c 2 -W 1 {{ host }}</strong>
  <pre>{{ output }}</pre>
</div>
{% elif error %}
<div class="card" style="border-color:#f85149">
  <p style="color:#f85149">{{ error }}</p>
</div>
{% endif %}
""", host=host, output=output, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
