from flask import Flask, render_template_string
app = Flask(__name__)

CHALLENGES = {
    "ch58-steg-meta": ("Metadata Secrets",   "Steganography",     "Easy",   "75",  "codef{exif_metadata_secrets_found}",
        "A JPEG photo was shared online without scrubbing EXIF metadata. Run <b>exiftool image.jpg</b> and check every field — the flag is hidden in a metadata comment.",
        "Use ExifTool: <code>exiftool photo.jpg</code> — look in the Comment, Artist, or Copyright fields.",
        [("EXIF Tag","Value"),("Make","Canon EOS R5"),("Model","Canon EOS R5"),("Artist","gh0st_h4ck3r"),("DateTime","2026:01:15 14:23:01"),
         ("Comment","codef{exif_metadata_secrets_found}"),("GPSLatitude","13.0827 N"),("GPSLongitude","80.2707 E"),("Software","Adobe Photoshop 2026")]),
    "ch60-osint-geo": ("Geo-Location Challenge","OSINT",           "Easy",  "100", "codef{perungudi_176_5th_cross}",
        "A photograph was taken at a secret rendezvous location. Use the visual clues — street signs, architecture, and landmarks — to identify the exact address. The flag is: <b>city_streetnumber_streetname</b>.",
        "Look for street signs, building numbers, and unique architectural features. Use Google Maps Street View.",
        [("Clue","Detail"),("Visible text","Burma Colony"),("Street sign","5th Cross Street"),("Building number","176"),("Area","Perungudi, Chennai"),("State","Tamil Nadu"),("Landmark","Nearby IT park — Tidel Park")]),
    "ch62-forensics-log": ("Log Hunter",      "Forensics",         "Hard",  "175", "codef{log_hunt3r_4tt4ck_found}",
        "Server access logs from a compromised web server are provided. A successful SQL injection attack occurred. Identify the malicious request, the attacker's IP address, and extract the embedded flag from the URL parameters.",
        "Filter for HTTP 200 responses on /admin, look for unusual parameters with -- or UNION SELECT patterns.",
        [("Time","Method","URL","Status","IP"),("10:01:22","GET","/index.html","200","192.168.1.10"),
         ("10:02:15","POST","/login","302","192.168.1.10"),("10:03:44","GET","/admin?id=1' OR '1'='1","200","10.66.6.6"),
         ("10:03:45","GET","/admin?id=1 UNION SELECT flag,2,3 FROM secrets-- -","200","10.66.6.6"),
         ("10:03:46","GET",f"/exfil?data=codef{{log_hunt3r_4tt4ck_found}}","200","10.66.6.6")]),
    "ch66-rev-js": ("Deobfuscate Me",       "Reverse Engineering","Medium","175", "codef{js_d30bfusc4t3d_c2_found}",
        "A heavily obfuscated JavaScript file was recovered from a malware dropper. Untangle the variable renaming, string splitting, and eval chains to find the hardcoded C2 server address.",
        "Use a JS beautifier (prettier, js-beautify), then trace eval() calls and String.fromCharCode arrays.",
        []),
    "ch67-pwn": ("Memory Corruption 101",   "Binary Exploitation","Hard",  "275", "codef{m3m0ry_c0rrupt10n_pwn3d}",
        "A vulnerable 32-bit C binary has no stack canary and no ASLR. A <code>gets()</code> call with a 64-byte buffer is your entry point. Overflow the buffer, control EIP, and redirect execution to the <code>win()</code> function.",
        "Craft: python3 -c \"print('A'*68 + '\\xef\\xbe\\xad\\xde')\" | ./binary — find win() address with objdump.",
        []),
    "ch68-format": ("Format String Leak",   "Binary Exploitation","Hard",  "225", "codef{f0rm4t_str1ng_l34k}",
        "A <code>printf()</code> call passes user input directly as the format string — zero sanitization. Use <code>%p</code> or <code>%s</code> format specifiers to leak stack memory and extract the flag stored there.",
        "Send %p.%p.%p.%p.%p.%p.%p to leak stack addresses, find the flag pointer, then use %s to dereference it.",
        []),
}

STYLES = """<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#060a12;color:#ddeeff;min-height:100vh;padding:30px 20px}
.wrap{max-width:860px;margin:0 auto}
.nav{display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:14px;border-bottom:1px solid #1a2a45}
.nav-brand{color:#00d4ff;font-weight:900;font-size:1.1rem}
h1{font-size:1.5rem;margin-bottom:8px}
.pts{color:#f0a040;font-weight:700;margin-bottom:20px;font-size:.9rem}
.card{background:#0e1829;border:1px solid #1a2a45;border-radius:10px;padding:22px;margin-bottom:18px}
.card h3{font-size:1rem;margin-bottom:12px}
.step{background:#060a12;padding:8px 14px;margin:6px 0;font-size:.82rem;color:#aac8e8;border-radius:4px}
table{width:100%;border-collapse:collapse;font-size:.8rem}
th{color:#6b8aaa;padding:7px 10px;border-bottom:1px solid #1a2a45;text-align:left}
td{padding:6px 10px;border-bottom:1px solid rgba(255,255,255,.03);font-family:monospace;color:#aac8e8}
input{background:rgba(255,255,255,.04);color:#39ff14;border:1px solid rgba(57,255,20,.3);padding:10px 14px;border-radius:6px;width:100%;font-family:monospace;font-size:.95rem;outline:none}
input:focus{border-color:#39ff14}
input::placeholder{color:#6b8aaa}
.btn{background:linear-gradient(135deg,#00d4ff,#0090c0);color:#000;border:none;padding:10px 28px;border-radius:6px;font-weight:700;cursor:pointer;font-size:.9rem;margin-top:8px}
.flag-box{background:#0a1f0a;border:1px solid rgba(57,255,20,.4);border-radius:6px;padding:14px;font-family:monospace;color:#39ff14;font-size:1.05rem;margin-top:8px}
.err{color:#ff5252;font-size:.88rem;margin-top:8px}
code{background:rgba(121,192,255,.1);color:#79c0ff;padding:2px 6px;border-radius:4px;font-size:.85em}
</style>"""

import os

def get_ch():
    path = os.getcwd().split('/')[-1]
    for k in CHALLENGES:
        if k in path:
            return CHALLENGES[k]
    return list(CHALLENGES.values())[0]

@app.route("/")
def index():
    name, cat, diff, pts, flag, desc, hint, table = get_ch()

    table_html = ""
    if table and len(table) > 1:
        headers = table[0]
        table_html = f"<div class='card'><h3>Evidence / Data</h3><table><thead><tr>{''.join(f'<th>{h}</th>' for h in headers)}</tr></thead><tbody>"
        for row in table[1:]:
            table_html += f"<tr>{''.join(f'<td>{c}</td>' for c in row)}</tr>"
        table_html += "</tbody></table></div>"

    CAT_COLORS = {
        "Steganography": "#ff6ec7", "OSINT": "#50ff50", "Forensics": "#00ffcc",
        "Reverse Engineering": "#c060ff", "Binary Exploitation": "#ff5252",
    }
    color = CAT_COLORS.get(cat, "#00d4ff")

    return render_template_string(f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{name} | COEDF CTF 2026</title>{STYLES}</head><body>
<div class="wrap">
<div class="nav">
    <span class="nav-brand">🛡️ COEDF CTF 2026</span>
    <span style="font-size:.72rem;background:rgba(0,0,0,.3);color:{color};border:1px solid {color}40;padding:3px 10px;border-radius:20px;font-weight:700">{cat}</span>
    <span style="font-size:.72rem;color:#6b8aaa">{diff} — {pts} pts</span>
</div>
<h1 style="color:{color};text-shadow:0 0 14px {color}60">{name}</h1>
<div class="pts">⭐ {pts} points &nbsp;|&nbsp; {cat} &nbsp;|&nbsp; {diff}</div>
<div class="card"><h3 style="color:{color}">Challenge Description</h3>
    <p style="color:#aac8e8;font-size:.88rem;line-height:1.7">{desc}</p>
</div>
{table_html}
</div></body></html>""")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
