from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
import uuid

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

users = {
    "u-admin": {
        "username": "admin",
        "password": "Admin@123",
        "role": "admin"
    },
    "u-user": {
        "username": "normal_user",
        "password": "User@123",
        "role": "user"
    }
}

documents = {
    "9f2a7c1e-1111-4c9a-aaaa-adminsecret01": {
        "owner_id": "u-admin",
        "title": "Admin Confidential Report",
        "content": "flag{advanced_idor_access_granted}"
    },
    "7b4d8a9c-2222-4f2b-bbbb-userfile02": {
        "owner_id": "u-user",
        "title": "User Profile Backup",
        "content": "normal user private note"
    }
}

audit_logs = [
    {
        "log_id": "log-1001",
        "user_id": "u-admin",
        "action": "Downloaded admin confidential report",
        "document_id": "9f2a7c1e-1111-4c9a-aaaa-adminsecret01"
    },
    {
        "log_id": "log-1002",
        "user_id": "u-user",
        "action": "Viewed user profile backup",
        "document_id": "7b4d8a9c-2222-4f2b-bbbb-userfile02"
    }
]


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return users.get(user_id)


def require_login():
    if not session.get("user_id"):
        return False
    return True


@app.route("/")
def home():
    if not require_login():
        return redirect(url_for("login"))

    return render_template_string("""
    <html>
    <head>
        <title>Advanced IDOR CTF</title>
        <style>
            body { font-family: Arial; background:#111827; color:white; padding:40px; }
            .box { background:#1f2937; padding:25px; border-radius:10px; width:760px; }
            a { color:#38bdf8; }
            code { background:#374151; padding:4px 8px; border-radius:5px; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Advanced IDOR Challenge</h1>

            <p>You are logged in as:</p>
            <code>{{ username }}</code>

            <h3>Your API</h3>
            <p><a href="/api/me">/api/me</a></p>
            <p><a href="/api/my-documents">/api/my-documents</a></p>

            <h3>Goal</h3>
            <p>Find the admin confidential document flag.</p>

            <h3>Hint</h3>
            <p>Not all object references are visible on the main page. Check APIs carefully.</p>

            <p><a href="/logout">Logout</a></p>
        </div>
    </body>
    </html>
    """, username=current_user()["username"])


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template_string("""
        <html>
        <head>
            <title>Login</title>
            <style>
                body { font-family: Arial; background:#111827; color:white; padding:40px; }
                .box { background:#1f2937; padding:25px; border-radius:10px; width:400px; }
                input { width:100%; padding:10px; margin:8px 0; }
                button { padding:10px 20px; cursor:pointer; }
                code { background:#374151; padding:4px 8px; border-radius:5px; }
            </style>
        </head>
        <body>
            <div class="box">
                <h2>Login</h2>
                <p>Use normal user:</p>
                <p><code>normal_user</code> / <code>User@123</code></p>

                <form method="POST">
                    <input name="username" placeholder="Username">
                    <input name="password" placeholder="Password" type="password">
                    <button type="submit">Login</button>
                </form>
            </div>
        </body>
        </html>
        """)

    username = request.form.get("username")
    password = request.form.get("password")

    for user_id, user in users.items():
        if user["username"] == username and user["password"] == password:
            session["user_id"] = user_id
            return redirect(url_for("home"))

    return "Invalid login", 401


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/api/me")
def api_me():
    if not require_login():
        return jsonify({"error": "login required"}), 401

    user_id = session["user_id"]
    user = users[user_id]

    return jsonify({
        "user_id": user_id,
        "username": user["username"],
        "role": user["role"]
    })


@app.route("/api/my-documents")
def my_documents():
    if not require_login():
        return jsonify({"error": "login required"}), 401

    user_id = session["user_id"]

    my_docs = []
    for doc_id, doc in documents.items():
        if doc["owner_id"] == user_id:
            my_docs.append({
                "document_id": doc_id,
                "title": doc["title"]
            })

    return jsonify(my_docs)


@app.route("/api/audit-logs")
def audit_log_list():
    if not require_login():
        return jsonify({"error": "login required"}), 401

    # Intentional information leak for CTF
    # This leaks document IDs from all users.
    return jsonify(audit_logs)


@app.route("/api/document")
def vulnerable_document():
    if not require_login():
        return jsonify({"error": "login required"}), 401

    document_id = request.args.get("id")

    if not document_id:
        return jsonify({
            "error": "missing id",
            "example": "/api/document?id=<document_id>"
        }), 400

    # Vulnerable IDOR:
    # Only checks if the user is logged in.
    # Does NOT check document ownership.
    if document_id in documents:
        return jsonify({
            "vulnerable": True,
            "document_id": document_id,
            "document": documents[document_id]
        })

    return jsonify({"error": "document not found"}), 404


@app.route("/api/secure-document")
def secure_document():
    if not require_login():
        return jsonify({"error": "login required"}), 401

    document_id = request.args.get("id")
    user_id = session["user_id"]

    if not document_id:
        return jsonify({
            "error": "missing id",
            "example": "/api/secure-document?id=<document_id>"
        }), 400

    if document_id not in documents:
        return jsonify({"error": "document not found"}), 404

    document = documents[document_id]

    # Secure authorization check
    if document["owner_id"] != user_id:
        return jsonify({
            "error": "access denied",
            "message": "You can only access your own documents"
        }), 403

    return jsonify({
        "vulnerable": False,
        "document_id": document_id,
        "document": document
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)