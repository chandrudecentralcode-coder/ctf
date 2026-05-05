from flask import Flask, request, jsonify, render_template_string
import jwt
import time

app = Flask(__name__)

# Weak key store - intentionally vulnerable for CTF
KEYS = {
    "user-key": "normal-user-secret",
    "public-key": "public-key-used-as-hmac-secret",
    "old-key": "old-secret-do-not-use"
}

documents = {
    "doc-user-1001": {
        "owner": "player",
        "title": "Player Notes",
        "content": "This is your normal document."
    },
    "doc-admin-9001": {
        "owner": "admin",
        "title": "Admin Confidential",
        "content": "flag{advanced_jwt_kid_idor_chain_success}"
    },
    "doc-test-0000": {
        "owner": "tester",
        "title": "Test Document",
        "content": "fake_flag{this_is_not_the_real_flag}"
    }
}

audit_logs = [
    {
        "event": "document_view",
        "user": "player",
        "doc_id": "doc-user-1001"
    },
    {
        "event": "admin_backup",
        "user": "admin",
        "doc_id": "doc-admin-9001"
    },
    {
        "event": "test_flag_created",
        "user": "tester",
        "doc_id": "doc-test-0000"
    }
]


def create_player_token():
    payload = {
        "user": "player",
        "role": "user",
        "iat": int(time.time()),
        "hint": "headers matter"
    }

    headers = {
        "kid": "user-key",
        "typ": "JWT"
    }

    return jwt.encode(
        payload,
        KEYS["user-key"],
        algorithm="HS256",
        headers=headers
    )


def decode_token(token):
    # Decode header without verification
    header = jwt.get_unverified_header(token)

    kid = header.get("kid", "user-key")

    # Vulnerable: trusts kid from user-controlled JWT header
    secret = KEYS.get(kid)

    if not secret:
        raise Exception("Unknown kid")

    # Vulnerable: accepts token based on user-selected key
    return jwt.decode(token, secret, algorithms=["HS256"])


@app.route("/")
def home():
    token = create_player_token()

    return render_template_string("""
    <html>
    <head>
        <title>Advanced JWT CTF</title>
        <style>
            body {
                background: #111827;
                color: white;
                font-family: Arial;
                padding: 40px;
            }
            .box {
                background: #1f2937;
                padding: 25px;
                border-radius: 10px;
                width: 850px;
            }
            code {
                background: #374151;
                padding: 5px 8px;
                border-radius: 5px;
                display: block;
                word-break: break-all;
            }
            a { color: #38bdf8; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Advanced JWT Challenge</h1>

            <p>You are a normal user. Your JWT token:</p>
            <code>{{ token }}</code>

            <h3>Allowed APIs</h3>
            <p><a href="/api/me">/api/me</a></p>
            <p><a href="/api/audit">/api/audit</a></p>
            <p><code>/api/document?id=doc-user-1001</code></p>
            <p><code>/api/admin</code></p>

            <h3>Goal</h3>
            <p>Get the real admin flag.</p>

            <h3>Hint</h3>
            <p>Payload is not the only place where JWT stores data.</p>
        </div>
    </body>
    </html>
    """, token=token)


@app.route("/api/me")
def me():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({
            "error": "Missing Authorization header",
            "example": "Authorization: Bearer <token>"
        }), 401

    try:
        token = token.replace("Bearer ", "")
        data = decode_token(token)

        return jsonify({
            "message": "Token accepted",
            "user": data.get("user"),
            "role": data.get("role"),
            "note": "Only admins can access /api/admin"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/audit")
def audit():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "Missing token"}), 401

    try:
        token = token.replace("Bearer ", "")
        decode_token(token)

        # Intentional leak
        return jsonify({
            "logs": audit_logs,
            "warning": "Some logs may be internal."
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/document")
def document():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "Missing token"}), 401

    try:
        token = token.replace("Bearer ", "")
        data = decode_token(token)

        doc_id = request.args.get("id")

        if not doc_id:
            return jsonify({
                "error": "Missing id",
                "example": "/api/document?id=doc-user-1001"
            }), 400

        if doc_id not in documents:
            return jsonify({"error": "Document not found"}), 404

        doc = documents[doc_id]

        # Vulnerable IDOR:
        # only checks logged-in token, not document ownership
        return jsonify({
            "requested_by": data.get("user"),
            "document": doc
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/admin")
def admin():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "Missing token"}), 401

    try:
        token = token.replace("Bearer ", "")
        data = decode_token(token)

        if data.get("role") != "admin":
            return jsonify({
                "error": "Access denied",
                "message": "Admin role required",
                "decoy": "fake_flag{normal_user_blocked}"
            }), 403

        return jsonify({
            "message": "Welcome admin",
            "flag": "flag{jwt_kid_header_admin_access}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/.well-known/jwks.json")
def jwks():
    # Confusing endpoint for players
    return jsonify({
        "keys": [
            {
                "kid": "public-key",
                "kty": "oct",
                "use": "sig",
                "alg": "HS256",
                "hint": "This key looks public, but it is used as HMAC secret."
            }
        ]
    })


@app.route("/hint")
def hint():
    return jsonify({
        "hint_1": "Check JWT header.",
        "hint_2": "kid decides which key is used.",
        "hint_3": "Try changing role and kid together."
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000, debug=True)