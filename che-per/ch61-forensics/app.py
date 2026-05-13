from flask import Flask, render_template_string, send_file
import os

app = Flask(__name__)

S = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Ghost in the Packet | COEDF CTF 2026</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',monospace;background:#060a12;color:#ddeeff;min-height:100vh;padding:30px 20px}
.wrap{max-width:920px;margin:0 auto}
.nav{display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:14px;border-bottom:1px solid #1a2a45}
.nav-brand{color:#00d4ff;font-weight:900;font-size:1.1rem}
.nav-cat{font-size:.72rem;background:rgba(0,255,204,.08);color:#00ffcc;border:1px solid rgba(0,255,204,.3);padding:3px 10px;border-radius:20px;font-weight:700}
.nav-diff{font-size:.72rem;background:rgba(0,212,255,.1);color:#00d4ff;border:1px solid rgba(0,212,255,.3);padding:3px 10px;border-radius:20px;font-weight:700}
h1{color:#00ffcc;font-size:1.6rem;margin-bottom:8px;text-shadow:0 0 14px rgba(0,255,204,.4)}
.pts{color:#f0a040;font-weight:700;margin-bottom:20px;font-size:.9rem}
.card{background:#0e1829;border:1px solid #1a2a45;border-radius:10px;padding:22px;margin-bottom:18px}
.card h3{color:#00ffcc;font-size:1rem;margin-bottom:12px}
.step{background:#060a12;border-left:3px solid #00ffcc;padding:8px 14px;margin:6px 0;font-size:.82rem;color:#aac8e8}
input{background:rgba(255,255,255,.04);color:#39ff14;border:1px solid rgba(57,255,20,.3);padding:10px 14px;border-radius:6px;width:100%;font-family:monospace;font-size:.95rem;outline:none;transition:border-color .2s}
input:focus{border-color:#39ff14}
input::placeholder{color:#6b8aaa}
.btn{background:linear-gradient(135deg,#00ffcc,#00b890);color:#000;border:none;padding:10px 28px;border-radius:6px;font-weight:700;cursor:pointer;font-size:.9rem;margin-top:8px}
.btn-dl{display:inline-block;background:linear-gradient(135deg,#1a6bff,#004de0);color:#fff;text-decoration:none;padding:12px 32px;border-radius:6px;font-weight:700;font-size:.95rem;margin-top:4px;letter-spacing:.03em}
.btn-dl:hover{background:linear-gradient(135deg,#2e7fff,#1a5ef0)}
.flag-box{background:#0a1f0a;border:1px solid rgba(57,255,20,.4);border-radius:6px;padding:14px;font-family:monospace;color:#39ff14;font-size:1.05rem;letter-spacing:.06em;text-shadow:0 0 8px rgba(57,255,20,.5)}
.err{color:#ff5252;font-size:.88rem;margin-top:8px}
code{background:rgba(121,192,255,.1);color:#79c0ff;padding:2px 6px;border-radius:4px;font-size:.85em}
.stat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:12px}
.stat{background:#060a12;border:1px solid #1a2a45;border-radius:6px;padding:12px;text-align:center}
.stat-val{font-size:1.4rem;font-weight:900;color:#00d4ff}
.stat-lbl{font-size:.72rem;color:#6b8aaa;margin-top:2px}
</style></head><body><div class="wrap">"""

FOOTER = "</div></body></html>"
FLAG = "codef{gh0st_1n_th3_p4ck3t_found}"
PCAP_FILE = os.path.join(os.path.dirname(__file__), "capture.pcap")


@app.route("/download")
def download():
    return send_file(PCAP_FILE, as_attachment=True, download_name="4SICS-network-capture.pcap", mimetype="application/vnd.tcpdump.pcap")


@app.route("/")
def index():
    pcap_size = f"{os.path.getsize(PCAP_FILE) // (1024*1024)} MB" if os.path.exists(PCAP_FILE) else "N/A"

    return render_template_string(S + f"""
<div class="nav">
    <span class="nav-brand">🔬 COEDF CTF 2026</span>
    <span class="nav-cat">Forensics</span>
    <span class="nav-diff">Medium — 150 pts</span>
</div>

<h1>👻 Ghost in the Packet</h1>
<div class="pts">⭐ 150 points &nbsp;|&nbsp; Category: Forensics &nbsp;|&nbsp; Difficulty: Medium</div>

<div class="card">
    <h3>Challenge Description</h3>
    <p style="color:#aac8e8;font-size:.88rem;line-height:1.7;margin-bottom:14px">
        During a security assessment at an industrial control facility, network traffic was captured
        from the OT/ICS segment. Among the industrial protocol traffic, a suspicious HTTP session
        was detected between internal nodes. The attacker exfiltrated a session token in cleartext
        inside an HTTP JSON response. Recover the token.
    </p>
    <div class="stat-grid">
        <div class="stat"><div class="stat-val">246K+</div><div class="stat-lbl">Total Frames</div></div>
        <div class="stat"><div class="stat-val">{pcap_size}</div><div class="stat-lbl">PCAP Size</div></div>
        <div class="stat"><div class="stat-val">Real</div><div class="stat-lbl">ICS Network Capture</div></div>
    </div>
</div>

<div class="card">
    <h3>📥 Download Packet Capture</h3>
    <a class="btn-dl" href="/download">⬇ Download 4SICS-network-capture.pcap</a>
</div>

""" + FOOTER)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
