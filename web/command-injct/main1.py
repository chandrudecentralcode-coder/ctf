from flask import Flask, request
import subprocess

app = Flask(__name__)

FLAG = "CTF{command_injection_filter_bypass}"

with open("flag_cmd.txt", "w") as f:
    f.write(FLAG)

@app.route("/")
def home():
    return """
    <h2>Task 51 - Command Injection</h2>
    <p>Endpoint: /dns?domain=google.com</p>
    <p>Goal: Read flag_cmd.txt</p>
    <p>Hint: Payload is blocked, but command separators are not only semicolons.</p>
    """

@app.route("/dns")
def dns_lookup():
    domain = request.args.get("domain", "")

    blacklist = [
        "cat",
        "flag",
        ";",
        "&",
        "|",
        "`",
        "$",
        ">",
        "<",
        " "
    ]

    for bad in blacklist:
        if bad in domain.lower():
            return "Blocked input detected!"

    cmd = f"nslookup {domain}"
    result = subprocess.getoutput(cmd)

    return f"""
    <h2>DNS Lookup Tool</h2>
    <p>Domain: {domain}</p>
    <pre>{result}</pre>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)