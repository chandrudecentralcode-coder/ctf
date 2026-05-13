from flask import Flask, render_template_string

app = Flask(__name__)


@app.route("/")
def index():
    return render_template_string("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SecureBank — Login</title>
<style>
  *, *::before, *::after { box-sizing: border-box; }
  body { margin: 0; background: #0d1117; font-family: Arial, sans-serif; display: flex;
         justify-content: center; align-items: center; min-height: 100vh; }
  .card { background: #161b22; border: 1px solid #21262d; border-radius: 10px;
          padding: 36px 32px; width: 360px; }
  h2 { color: #58a6ff; text-align: center; margin-bottom: 24px; }
  label { color: #8b949e; font-size: .85em; display: block; margin-bottom: 4px; }
  input { width: 100%; background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
          padding: 10px 12px; border-radius: 6px; margin-bottom: 14px; font-size: 1em; }
  input:focus { outline: none; border-color: #58a6ff; }
  button { width: 100%; background: #1f6feb; color: white; border: none; padding: 12px;
           border-radius: 6px; font-size: 1em; cursor: pointer; font-weight: bold; }
  button:hover { background: #388bfd; }
  .hint { color: #8b949e; font-size: .8em; text-align: center; margin-top: 14px; }
</style>
</head>
<body>
<div class="card">
  <h2>🏦 SecureBank</h2>
  <label>Username</label>
  <input type="text" placeholder="Enter username">
  <label>Password</label>
  <input type="password" placeholder="Enter password">
  <button type="button">Sign In</button>
  <p class="hint">💡 Inspect the page source carefully</p>
</div>

<script>
  // ─── Developer Notes (remove before production!) ───────────────────────
  // Staging credentials for QA testing — DO NOT commit to git
  const _devConfig = {
    env: "staging",
    apiVersion: "v2",
    // internal access token: codef{javascript_source_flag}
    debugToken: "sk-dev-abc123",
    featureFlags: { newUI: true, betaDashboard: false }
  };

  function initApp() {
    // console.log("[dev] config loaded:", _devConfig);
  }
  initApp();
  // ────────────────────────────────────────────────────────────────────────
</script>
</body>
</html>
""")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
