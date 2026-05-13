from flask import Flask, render_template_string

app = Flask(__name__)

S = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>S3 Bucket Exposure | COEDF CTF 2026</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',monospace;background:#060a12;color:#ddeeff;min-height:100vh;padding:30px 20px}
.wrap{max-width:880px;margin:0 auto}
.nav{display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:14px;border-bottom:1px solid #1a2a45}
.nav-brand{color:#00d4ff;font-weight:900;font-size:1.1rem}
.nav-cat{font-size:.72rem;background:rgba(79,195,247,.1);color:#4fc3f7;border:1px solid rgba(79,195,247,.3);padding:3px 10px;border-radius:20px;font-weight:700}
.nav-diff{font-size:.72rem;background:rgba(0,212,255,.1);color:#00d4ff;border:1px solid rgba(0,212,255,.3);padding:3px 10px;border-radius:20px;font-weight:700}
h1{color:#4fc3f7;font-size:1.6rem;margin-bottom:8px;text-shadow:0 0 14px rgba(79,195,247,.4)}
.pts{color:#f0a040;font-weight:700;margin-bottom:20px;font-size:.9rem}
.card{background:#0e1829;border:1px solid #1a2a45;border-radius:10px;padding:22px;margin-bottom:18px}
.card h3{color:#4fc3f7;font-size:1rem;margin-bottom:12px}
pre{background:#000d1a;border:1px solid #1a2a45;border-radius:6px;padding:14px;font-family:monospace;font-size:.76rem;color:#aac8e8;overflow-x:auto;line-height:1.7;max-height:360px;overflow-y:auto}
.step{background:#060a12;border-left:3px solid #4fc3f7;padding:8px 14px;margin:6px 0;font-size:.82rem;color:#aac8e8}
input{background:rgba(255,255,255,.04);color:#39ff14;border:1px solid rgba(57,255,20,.3);padding:10px 14px;border-radius:6px;width:100%;font-family:monospace;font-size:.95rem;outline:none;transition:border-color .2s}
input:focus{border-color:#39ff14}
input::placeholder{color:#6b8aaa}
.btn{background:linear-gradient(135deg,#4fc3f7,#0288d1);color:#000;border:none;padding:10px 28px;border-radius:6px;font-weight:700;cursor:pointer;font-size:.9rem;margin-top:8px}
.flag-box{background:#0a1f0a;border:1px solid rgba(57,255,20,.4);border-radius:6px;padding:14px;font-family:monospace;color:#39ff14;font-size:1.05rem;letter-spacing:.06em;text-shadow:0 0 8px rgba(57,255,20,.5);margin-top:8px}
.err{color:#ff5252;font-size:.88rem;margin-top:8px}
code{background:rgba(121,192,255,.1);color:#79c0ff;padding:2px 6px;border-radius:4px;font-size:.85em}
</style></head><body><div class="wrap">"""

FOOTER = "</div></body></html>"
FLAG = "codef{s3_buck3t_3xp0sur3_found}"

BUCKET_CONTENTS = """$ aws s3 ls s3://acmecorp-backup --no-sign-request
                           PRE 2024/
                           PRE 2025/
                           PRE 2026/
2026-01-15 10:23:41      1024 config.json
2026-02-01 08:12:33      2048 database_backup_jan.sql.gz
2026-03-15 14:55:21       256 flag.txt
2026-04-01 09:00:00     10240 employee_records.csv
2026-05-01 12:00:00      4096 financial_report_q1.pdf

$ aws s3 cp s3://acmecorp-backup/flag.txt - --no-sign-request
codef{s3_buck3t_3xp0sur3_found}

$ aws s3 cp s3://acmecorp-backup/config.json - --no-sign-request
{
  "database": {
    "host": "db.internal.acmecorp.com",
    "port": 5432,
    "username": "admin",
    "password": "Sup3rS3cur3Pass!",
    "database": "production"
  },
  "aws": {
    "access_key_id": "AKIA5EXAMPLE12345678",
    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "region": "ap-south-1"
  }
}"""


@app.route("/")
def index():
    return render_template_string(S + f"""
<div class="nav">
    <span class="nav-brand">☁️ COEDF CTF 2026</span>
    <span class="nav-cat">Cloud Security</span>
    <span class="nav-diff">Medium — 175 pts</span>
</div>

<h1>☁️ S3 Bucket Exposure</h1>
<div class="pts">⭐ 175 points &nbsp;|&nbsp; Category: Cloud Security &nbsp;|&nbsp; Difficulty: Medium</div>

<div class="card">
    <h3>Challenge Description</h3>
    <p style="color:#aac8e8;font-size:.88rem;line-height:1.7;margin-bottom:12px">
        A DevOps engineer at AcmeCorp accidentally made an S3 bucket publicly accessible
        while setting up a backup workflow. The bucket contains sensitive files including
        credentials, database backups, employee records, and — the flag.
        The bucket name follows a predictable pattern: <code>&lt;company&gt;-backup</code>.
    </p>
</div>

<div class="card">
    <h3>Simulated AWS CLI Session — Bucket Enumeration</h3>
    <pre>{BUCKET_CONTENTS}</pre>
</div>

""" + FOOTER)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
