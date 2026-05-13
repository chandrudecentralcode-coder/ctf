from flask import Flask, render_template_string

app = Flask(__name__)

S = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>The Lost APK | COEDF CTF 2026</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#060a12;color:#ddeeff;min-height:100vh;padding:30px 20px}
.wrap{max-width:860px;margin:0 auto}
.nav{display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:14px;border-bottom:1px solid #1a2a45}
.nav-brand{color:#00d4ff;font-weight:900;font-size:1.1rem}
.nav-cat{font-size:.72rem;background:rgba(255,154,0,.1);color:#ff9a00;border:1px solid rgba(255,154,0,.3);padding:3px 10px;border-radius:20px;font-weight:700}
.nav-diff{font-size:.72rem;background:rgba(0,212,255,.1);color:#00d4ff;border:1px solid rgba(0,212,255,.3);padding:3px 10px;border-radius:20px;font-weight:700}
h1{color:#ff9a00;font-size:1.6rem;margin-bottom:8px;text-shadow:0 0 14px rgba(255,154,0,.4)}
.pts{color:#f0a040;font-weight:700;margin-bottom:20px;font-size:.9rem}
.card{background:#0e1829;border:1px solid #1a2a45;border-radius:10px;padding:22px;margin-bottom:18px}
.card h3{color:#ff9a00;font-size:1rem;margin-bottom:12px}
pre{background:#000d1a;border:1px solid #1a2a45;border-radius:6px;padding:14px;font-family:monospace;font-size:.75rem;color:#aac8e8;overflow-x:auto;line-height:1.65;max-height:340px;overflow-y:auto}
.kw{color:#f97583}.fn{color:#b392f0}.str{color:#9ecbff}.cmt{color:#6b8aaa}.ann{color:#79b8ff}
.step{background:#060a12;border-left:3px solid #ff9a00;padding:8px 14px;margin:6px 0;font-size:.82rem;color:#aac8e8}
input{background:rgba(255,255,255,.04);color:#39ff14;border:1px solid rgba(57,255,20,.3);padding:10px 14px;border-radius:6px;width:100%;font-family:monospace;font-size:.95rem;outline:none;transition:border-color .2s}
input:focus{border-color:#39ff14}
input::placeholder{color:#6b8aaa}
.btn{background:linear-gradient(135deg,#ff9a00,#cc6600);color:#000;border:none;padding:10px 28px;border-radius:6px;font-weight:700;cursor:pointer;font-size:.9rem;margin-top:8px}
.flag-box{background:#0a1f0a;border:1px solid rgba(57,255,20,.4);border-radius:6px;padding:14px;font-family:monospace;color:#39ff14;font-size:1.05rem;letter-spacing:.06em;text-shadow:0 0 8px rgba(57,255,20,.5);margin-top:8px}
.err{color:#ff5252;font-size:.88rem;margin-top:8px}
code{background:rgba(121,192,255,.1);color:#79c0ff;padding:2px 6px;border-radius:4px;font-size:.85em}
</style></head><body><div class="wrap">"""

FOOTER = "</div></body></html>"
SECRET_KEY = "mY_s3cr3t_k3y_coedf2026"
FLAG = "codef{l0st_4pk_r3v3rs3d_s3cr3t}"

SMALI = """<span class="cmt"># Decompiled Java → Smali (jadx output)</span>
<span class="cmt"># Class: com.acmecorp.app.MainActivity</span>

<span class="kw">public class</span> <span class="fn">MainActivity</span> <span class="kw">extends</span> AppCompatActivity {

    <span class="cmt">// BuildConfig constant — hardcoded during build</span>
    <span class="kw">private static final</span> <span class="ann">String</span> <span class="fn">API_KEY</span> = <span class="str">"sk_live_REDACTED_0xDEADBEEF"</span>;

    <span class="cmt">// Hardcoded secret key used for local encryption</span>
    <span class="kw">private static final</span> <span class="ann">String</span> <span class="fn">SECRET_KEY</span> = <span class="str">"mY_s3cr3t_k3y_coedf2026"</span>;

    <span class="kw">private static final</span> <span class="ann">String</span> <span class="fn">BASE_URL</span> = <span class="str">"https://api.acmecorp.internal/v1"</span>;

    @Override
    <span class="kw">protected void</span> <span class="fn">onCreate</span>(Bundle savedInstanceState) {
        <span class="kw">super</span>.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        <span class="cmt">// Initialize encrypted storage with hardcoded key</span>
        EncryptedStorage storage = <span class="kw">new</span> EncryptedStorage(<span class="fn">SECRET_KEY</span>);

        <span class="cmt">// Load user data</span>
        loadUserProfile(storage);
    }

    <span class="kw">private void</span> <span class="fn">loadUserProfile</span>(EncryptedStorage s) {
        <span class="ann">String</span> userData = s.decrypt(getSharedPreferences(<span class="str">"user_data"</span>, MODE_PRIVATE)
                             .getString(<span class="str">"profile"</span>, <span class="str">""</span>));
        <span class="cmt">// Process user data...</span>
    }

    <span class="kw">private void</span> <span class="fn">syncToServer</span>() {
        <span class="cmt">// Uses API_KEY for authentication — leaked in APK!</span>
        Request req = <span class="kw">new</span> Request.Builder()
            .url(<span class="fn">BASE_URL</span> + <span class="str">"/sync"</span>)
            .addHeader(<span class="str">"Authorization"</span>, <span class="str">"Bearer "</span> + <span class="fn">API_KEY</span>)
            .build();
    }
}

<span class="cmt">/* strings.xml (res/values/strings.xml) */</span>
&lt;resources&gt;
    &lt;string name=<span class="str">"app_name"</span>&gt;AcmeCorp&lt;/string&gt;
    &lt;string name=<span class="str">"debug_mode"</span>&gt;false&lt;/string&gt;
    &lt;string name=<span class="str">"secret_backup"</span>&gt;<span class="str">mY_s3cr3t_k3y_coedf2026</span>&lt;/string&gt;
&lt;/resources&gt;"""


@app.route("/")
def index():
    return render_template_string(S + f"""
<div class="nav">
    <span class="nav-brand">📱 COEDF CTF 2026</span>
    <span class="nav-cat">Mobile Security</span>
    <span class="nav-diff">Medium — 200 pts</span>
</div>

<h1>📱 The Lost APK</h1>
<div class="pts">⭐ 200 points &nbsp;|&nbsp; Category: Mobile Security &nbsp;|&nbsp; Difficulty: Medium</div>

<div class="card">
    <h3>Challenge Description</h3>
    <p style="color:#aac8e8;font-size:.88rem;line-height:1.7;margin-bottom:12px">
        An APK file was recovered from a seized Android device during a forensic investigation.
        The application contains a hardcoded secret key used for local data encryption.
        Using <strong style="color:#ff9a00">jadx</strong> or <strong style="color:#ff9a00">apktool</strong>,
        the APK was decompiled and the Java/Smali source code was recovered.
        Find the hardcoded secret key embedded in the application's source code.
    </p>
</div>

<div class="card">
    <h3>Decompiled APK Source</h3>
    <pre>{SMALI}</pre>
</div>

""" + FOOTER)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
