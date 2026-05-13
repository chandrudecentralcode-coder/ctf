from flask import Flask, render_template_string

app = Flask(__name__)

S = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Dark Web Trail | COEDF CTF 2026</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#060a12;color:#ddeeff;min-height:100vh;padding:30px 20px}
.wrap{max-width:860px;margin:0 auto}
.nav{display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:14px;border-bottom:1px solid #1a2a45}
.nav-brand{color:#00d4ff;font-weight:900;font-size:1.1rem;letter-spacing:.06em}
.nav-cat{font-size:.72rem;background:rgba(57,255,20,.1);color:#50ff50;border:1px solid rgba(57,255,20,.3);padding:3px 10px;border-radius:20px;font-weight:700;letter-spacing:.1em}
.nav-diff{font-size:.72rem;background:rgba(0,212,255,.1);color:#00d4ff;border:1px solid rgba(0,212,255,.3);padding:3px 10px;border-radius:20px;font-weight:700}
h1{color:#50ff50;font-size:1.6rem;margin-bottom:8px;text-shadow:0 0 14px rgba(57,255,20,.4)}
.pts{color:#f0a040;font-weight:700;margin-bottom:20px;font-size:.9rem}
.card{background:#0e1829;border:1px solid #1a2a45;border-radius:10px;padding:22px;margin-bottom:18px}
.card h3{color:#50ff50;font-size:1rem;margin-bottom:12px;letter-spacing:.06em}
.profile{background:#060a12;border:1px solid #1a2a45;border-radius:8px;padding:16px;margin-bottom:12px}
.profile-hdr{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.avatar{width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#1a2a45,#0e1829);border:2px solid #1a2a45;display:flex;align-items:center;justify-content:center;font-size:1.4rem;flex-shrink:0}
.uname{font-weight:700;color:#ddeeff;font-size:.95rem}
.handle{color:#6b8aaa;font-size:.78rem;margin-top:2px}
.bio{font-size:.82rem;color:#aac8e8;line-height:1.65;margin-bottom:8px}
.meta{font-size:.72rem;color:#6b8aaa}
.tag{display:inline-block;background:rgba(57,255,20,.08);color:#50ff50;border:1px solid rgba(57,255,20,.2);padding:2px 8px;border-radius:4px;font-size:.7rem;margin:2px}
.step{background:#060a12;border-left:3px solid #50ff50;padding:8px 14px;margin:6px 0;font-size:.82rem;color:#aac8e8}
input{background:rgba(255,255,255,.04);color:#39ff14;border:1px solid rgba(57,255,20,.3);padding:10px 14px;border-radius:6px;width:100%;font-family:monospace;font-size:.95rem;outline:none;transition:border-color .2s}
input:focus{border-color:#39ff14;box-shadow:0 0 0 2px rgba(57,255,20,.15)}
input::placeholder{color:#6b8aaa}
.btn{background:linear-gradient(135deg,#39ff14,#20c000);color:#000;border:none;padding:10px 28px;border-radius:6px;font-weight:700;cursor:pointer;font-size:.9rem;margin-top:8px}
.flag-box{background:#0a1f0a;border:1px solid rgba(57,255,20,.4);border-radius:6px;padding:14px;font-family:monospace;color:#39ff14;font-size:1.05rem;letter-spacing:.06em;text-shadow:0 0 8px rgba(57,255,20,.5)}
.err{color:#ff5252;font-size:.88rem;margin-top:8px}
code{background:rgba(121,192,255,.1);color:#79c0ff;padding:2px 6px;border-radius:4px;font-size:.85em}
</style></head><body><div class="wrap">"""

FOOTER = "</div></body></html>"
SECRET = "d4rk_w3b_osint_tr41l"
FLAG = f"codef{{{SECRET}}}"


@app.route("/")
def index():
    return render_template_string(S + f"""
<div class="nav">
    <span class="nav-brand">🔭 COEDF CTF 2026</span>
    <span class="nav-cat">OSINT</span>
    <span class="nav-diff">Medium — 125 pts</span>
</div>

<h1>🔭 Dark Web Trail</h1>
<div class="pts">⭐ 125 points &nbsp;|&nbsp; Category: OSINT &nbsp;|&nbsp; Difficulty: Medium</div>

<div class="card">
    <h3>Mission Briefing</h3>
    <p style="color:#aac8e8;font-size:.88rem;line-height:1.7;margin-bottom:12px">
        A suspected threat actor with the username <code>gh0st_h4ck3r</code> has been operating
        across multiple platforms. Intelligence reports suggest they left a secret code embedded
        in their profile biography across social media platforms.
        Your mission: find their presence, piece together the clues, and extract the flag.
    </p>
    <div class="step">Username to track: <strong style="color:#50ff50">gh0st_h4ck3r</strong></div>
    <div class="step">Platforms: GitHub, Twitter/X, Reddit, Pastebin, HackTheBox</div>
    <div class="step">The secret is split across multiple profiles — combine the clues</div>
</div>

<div class="card">
    <h3>Intel Report — Recovered Profiles</h3>

    <div class="profile">
        <div class="profile-hdr">
            <div class="avatar">👤</div>
            <div>
                <div class="uname">gh0st_h4ck3r</div>
                <div class="handle">@gh0st_h4ck3r &bull; GitHub</div>
            </div>
        </div>
        <div class="bio">Security researcher. Interested in OSINT, malware analysis, and red teaming.
        "The truth is always hidden in plain sight. Part 1: d4rk_w3b"</div>
        <div class="meta">📌 Chennai, India &bull; 12 repositories &bull; Joined 2022</div>
    </div>

    <div class="profile">
        <div class="profile-hdr">
            <div class="avatar">🐦</div>
            <div>
                <div class="uname">gh0st_h4ck3r</div>
                <div class="handle">@gh0st_h4ck3r &bull; Twitter / X</div>
            </div>
        </div>
        <div class="bio">🔐 Hacker. OSINT enthusiast. CTF player.
        Last tweet: "Congrats if you found Part 2: _osint_ — you're on the right track"</div>
        <div class="meta">🔁 47 retweets &bull; ❤️ 213 likes</div>
    </div>

    <div class="profile">
        <div class="profile-hdr">
            <div class="avatar">📋</div>
            <div>
                <div class="uname">gh0st_h4ck3r</div>
                <div class="handle">u/gh0st_h4ck3r &bull; Reddit</div>
            </div>
        </div>
        <div class="bio">r/netsec regular. "If you've made it this far, combine what you found:
        d4rk_w3b + _osint_ + tr41l = the secret. Submit it as the flag content."</div>
        <div class="meta">🏆 Karma: 1,337 &bull; Joined: 3 years ago</div>
    </div>
</div>

""" + FOOTER)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
