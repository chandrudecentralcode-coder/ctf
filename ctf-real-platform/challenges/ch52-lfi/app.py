from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

# Files served from /var/www/files/ — flag is one level up at /var/www/flag.txt
os.makedirs("/var/www/files", exist_ok=True)

with open("/var/www/files/welcome.txt", "w") as _f:
    _f.write("Welcome to FileViewer! Browse our public document library.\n")
with open("/var/www/files/readme.txt", "w") as _f:
    _f.write("Use the ?file= parameter to view a file by name.\nExample: ?file=welcome.txt\n")
with open("/var/www/files/notes.txt", "w") as _f:
    _f.write("Project notes:\n- Launch date: Q3 2024\n- Team size: 12\n- Stack: Python/Flask\n")
with open("/var/www/flag.txt", "w") as _f:
    _f.write("flag{local_file_inclusion_success}\n")

S = """<style>
body{font-family:monospace;background:#0d1117;color:#c9d1d9;max-width:800px;margin:40px auto;padding:20px}
h1{color:#58a6ff;border-bottom:1px solid #21262d;padding-bottom:8px}
.card{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:20px;margin:14px 0}
a{color:#58a6ff;text-decoration:none}a:hover{text-decoration:underline}
input{background:#0d1117;color:#c9d1d9;border:1px solid #30363d;padding:8px 12px;
      border-radius:6px;width:280px;font-family:monospace}
button{background:#1f6feb;color:white;border:none;padding:8px 16px;border-radius:6px;cursor:pointer}
pre{background:#0d1117;border:1px solid #21262d;padding:14px;border-radius:6px;overflow-x:auto;white-space:pre-wrap}
.err{color:#f85149}
.hint{color:#8b949e;font-size:.85em;margin-top:6px}
</style>"""


@app.route("/")
def index():
    filename = request.args.get("file", "")
    content  = ""
    error    = ""

    if filename:
        # Intentionally vulnerable — os.path.join does NOT prevent traversal
        filepath = os.path.join("/var/www/files", filename)
        try:
            with open(filepath, "r") as fh:
                content = fh.read()
        except FileNotFoundError:
            error = f"File not found: {filename}"
        except IsADirectoryError:
            error = f"Is a directory: {filename}"
        except Exception as e:
            error = str(e)

    return render_template_string(S + """
<h1>📂 FileViewer</h1>
<div class="card">
  <p>Public files:
    <a href="/?file=welcome.txt">welcome.txt</a> &nbsp;|&nbsp;
    <a href="/?file=readme.txt">readme.txt</a> &nbsp;|&nbsp;
    <a href="/?file=notes.txt">notes.txt</a>
  </p>
  <form method="GET">
    <input name="file" placeholder="filename" value="{{ filename }}">
    <button>View</button>
  </form>
  <p class="hint">Files are served from /var/www/files/ — can you escape the directory?</p>
</div>
{% if content %}
<div class="card">
  <strong>{{ filename }}</strong>
  <pre>{{ content }}</pre>
</div>
{% elif error %}
<div class="card" style="border-color:#f85149">
  <p class="err">{{ error }}</p>
</div>
{% endif %}
""", filename=filename, content=content, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
