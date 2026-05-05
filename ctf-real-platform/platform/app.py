from flask import (Flask, render_template, request, jsonify,
                   session, redirect, url_for, flash, Response)
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import secrets
import string
import functools
import re
import requests as ext_requests
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "changeme")

DB_PATH          = "/data/ctf.db"
MAX_TEAM_SIZE    = 3
ALLOWED_EMAILS_ENV = os.environ.get("ALLOWED_EMAILS", "")
ADMIN_PASSWORD   = os.environ.get("ADMIN_PASSWORD", "ctfadmin123")
ATTEMPT_LIMIT    = 5
COOLDOWN_SECONDS = 60


# ─── helpers ──────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=10000")
    return conn


def invite_code():
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(8))


def login_required(f):
    @functools.wraps(f)
    def dec(*a, **kw):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return f(*a, **kw)
    return dec


def admin_required(f):
    @functools.wraps(f)
    def dec(*a, **kw):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return f(*a, **kw)
    return dec


def team_required(f):
    @functools.wraps(f)
    def dec(*a, **kw):
        if not session.get("team_id"):
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"status": "error", "msg": "Join a team first."}), 403
            flash("You must create or join a team before accessing challenges.", "warning")
            return redirect(url_for("team_create"))
        return f(*a, **kw)
    return dec


def get_ctf_window():
    """Return (start_dt, end_dt) datetimes; either may be None (= no bound)."""
    with get_db() as db:
        row = db.execute("SELECT start_time, end_time FROM ctf_settings WHERE id=1").fetchone()
    if not row:
        return None, None
    fmt = "%Y-%m-%d %H:%M:%S"
    start = datetime.strptime(row["start_time"], fmt) if row["start_time"] else None
    end   = datetime.strptime(row["end_time"],   fmt) if row["end_time"]   else None
    return start, end


def ctf_is_open():
    """Return (is_open, state, boundary_dt).
    state is 'open', 'not_started', or 'ended'.
    """
    start, end = get_ctf_window()
    now = datetime.now()
    if start and now < start:
        return False, "not_started", start
    if end and now > end:
        return False, "ended", end
    return True, "open", None


# ─── database ─────────────────────────────────────────────────────────────────

def _migrate(db):
    """Safely add columns / tables missing from older database versions."""
    column_migrations = [
        "ALTER TABLE users ADD COLUMN team_id INTEGER REFERENCES teams(id)",
        "ALTER TABLE users ADD COLUMN score INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "ALTER TABLE challenges ADD COLUMN difficulty TEXT DEFAULT 'Easy'",
        "ALTER TABLE challenges ADD COLUMN hint TEXT",
        "ALTER TABLE challenges ADD COLUMN hint_cost INTEGER DEFAULT 10",
        "ALTER TABLE challenges ADD COLUMN port INTEGER",
    ]
    for sql in column_migrations:
        try:
            db.execute(sql)
        except sqlite3.OperationalError:
            pass  # column already exists — ignore

    # Ensure ctf_settings seed row exists
    db.execute("""
        INSERT OR IGNORE INTO ctf_settings (id, start_time, end_time) VALUES (1, NULL, NULL)
    """)

    # Remove duplicate challenge rows (keep the lowest-id copy of each name)
    db.execute("""
        DELETE FROM challenges WHERE id NOT IN (
            SELECT MIN(id) FROM challenges GROUP BY name
        )
    """)
    db.commit()


def init_db():
    os.makedirs("/data", exist_ok=True)
    db = get_db()

    # 1. Create all tables (safe to run on existing DB)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS allowed_emails (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            note  TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS teams (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT UNIQUE NOT NULL,
            invite_code TEXT UNIQUE NOT NULL,
            score       INTEGER DEFAULT 0,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            team_id       INTEGER REFERENCES teams(id),
            score         INTEGER DEFAULT 0,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS challenges (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            category    TEXT NOT NULL,
            description TEXT NOT NULL,
            points      INTEGER NOT NULL,
            flag        TEXT NOT NULL,
            hint        TEXT,
            hint_cost   INTEGER DEFAULT 10,
            port        INTEGER,
            difficulty  TEXT DEFAULT 'Easy'
        );

        CREATE TABLE IF NOT EXISTS solves (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            solved_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, challenge_id)
        );

        CREATE TABLE IF NOT EXISTS team_solves (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id      INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            user_id      INTEGER NOT NULL,
            solved_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(team_id, challenge_id)
        );

        CREATE TABLE IF NOT EXISTS hints_used (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            UNIQUE(user_id, challenge_id)
        );

        CREATE TABLE IF NOT EXISTS flag_attempts (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS ctf_settings (
            id         INTEGER PRIMARY KEY,
            start_time TEXT,
            end_time   TEXT
        );
    """)

    # 2. Run column migrations (adds new columns to pre-existing tables)
    _migrate(db)

    # 3. Seed challenges (only if not already present by name)
    challenges = [
        ("Hidden File",          "Web", "A company website blocks certain paths from search engines. Find the hidden admin path and retrieve the flag.", 50,  "flag{robots_txt_hidden_file_found}",  "Check /robots.txt for disallowed paths", 10, 5001, "Easy"),
        ("JS Hidden Flag",       "Web", "Developers left something sensitive in the JavaScript source of this login page. Inspect it carefully.",         75,  "flag{javascript_source_flag}",        "View page source — check the <script> tags", 15, 5002, "Easy"),
        ("SQL Injection",        "Web", "The admin portal login form passes user input directly into a SQL query. Bypass authentication.",                 100, "flag{sqli_login_bypass}",             "Try classic SQLi: admin' --", 20, 5003, "Easy"),
        ("Advanced IDOR",        "Web", "You have a player account on this document manager. The admin has a secret document. Find and read it.",          150, "flag{advanced_idor_access_granted}",  "Log in as player, then check the audit log endpoint", 25, 5004, "Medium"),
        ("Command Injection",    "Web", "A network diagnostic tool runs ping without sanitizing input. Inject a command to read /app/flag.txt.",           150, "flag{command_injection_success}",     "Chain commands with ; or &&", 25, 5005, "Medium"),
        ("Local File Inclusion", "Web", "A file viewer reads files by name without validation. Use path traversal to read the flag outside the web root.", 125, "flag{local_file_inclusion_success}",  "Try ?file=../flag.txt", 20, 5006, "Medium"),
        ("Cookie Manipulation",  "Web", "Your session role is stored in a plain cookie. Become admin.",                                                    100, "flag{cookie_role_admin}",             "DevTools → Application → Cookies → change role to admin", 15, 5007, "Easy"),
        ("JWT Manipulation",     "Web", "The app issues JWTs signed with a weak secret. Forge a token with admin role.",                                   200, "flag{jwt_role_admin_bypass}",         "Decode, change role to admin, re-sign with secret: weaksecret", 30, 5008, "Hard"),
    ]
    for ch in challenges:
        exists = db.execute(
            "SELECT 1 FROM challenges WHERE name=?", (ch[0],)
        ).fetchone()
        if not exists:
            db.execute("""
                INSERT INTO challenges
                    (name,category,description,points,flag,hint,hint_cost,port,difficulty)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, ch)

    # 4. Seed whitelisted emails from environment variable
    if ALLOWED_EMAILS_ENV:
        for em in ALLOWED_EMAILS_ENV.split(","):
            em = em.strip().lower()
            if em:
                try:
                    db.execute("INSERT INTO allowed_emails (email) VALUES (?)", (em,))
                except sqlite3.IntegrityError:
                    pass

    db.commit()
    db.close()


# ─── home ──────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    with get_db() as db:
        stats = {
            "challenges": db.execute("SELECT COUNT(*) FROM challenges").fetchone()[0],
            "users":      db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "teams":      db.execute("SELECT COUNT(*) FROM teams").fetchone()[0],
            "solves":     db.execute("SELECT COUNT(*) FROM solves").fetchone()[0],
        }
        email_restricted = db.execute("SELECT COUNT(*) FROM allowed_emails").fetchone()[0] > 0
    return render_template("home.html", stats=stats, email_restricted=email_restricted,
                           max_team=MAX_TEAM_SIZE, attempt_limit=ATTEMPT_LIMIT,
                           cooldown=COOLDOWN_SECONDS)


# ─── auth ─────────────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    with get_db() as db:
        whitelist_active = db.execute("SELECT COUNT(*) FROM allowed_emails").fetchone()[0] > 0

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html", whitelist_active=whitelist_active)
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("register.html", whitelist_active=whitelist_active)

        with get_db() as db:
            if whitelist_active:
                if not db.execute(
                    "SELECT 1 FROM allowed_emails WHERE email = ?", (email,)
                ).fetchone():
                    flash("Your email is not on the approved list. Contact the admin.", "danger")
                    return render_template("register.html", whitelist_active=whitelist_active)
            try:
                db.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, generate_password_hash(password))
                )
                db.commit()
                flash("Account created! Please login.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Username or email already taken.", "danger")

    return render_template("register.html", whitelist_active=whitelist_active)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"]  = user["id"]
            session["username"] = user["username"]
            # team_id may be None — that's fine
            session["team_id"]  = user["team_id"] if "team_id" in user.keys() else None
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("challenges"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# ─── teams ────────────────────────────────────────────────────────────────────

def _user_team_id(db, user_id):
    """Return the team_id for a user, or None if column missing / not set."""
    try:
        row = db.execute("SELECT team_id FROM users WHERE id=?", (user_id,)).fetchone()
        return row["team_id"] if row else None
    except Exception:
        return None


@app.route("/teams/create", methods=["GET", "POST"])
@login_required
def team_create():
    with get_db() as db:
        current_team = _user_team_id(db, session["user_id"])
    if current_team:
        flash("You are already in a team. Leave it first.", "warning")
        return redirect(url_for("team_detail", tid=current_team))

    if request.method == "POST":
        name = request.form.get("team_name", "").strip()
        if not name or len(name) < 3:
            flash("Team name must be at least 3 characters.", "danger")
            return render_template("team_create.html")
        if len(name) > 32:
            flash("Team name must be 32 characters or less.", "danger")
            return render_template("team_create.html")

        code = invite_code()
        with get_db() as db:
            try:
                db.execute("INSERT INTO teams (name, invite_code) VALUES (?, ?)", (name, code))
                team = db.execute("SELECT id FROM teams WHERE name = ?", (name,)).fetchone()
                db.execute("UPDATE users SET team_id = ? WHERE id = ?",
                           (team["id"], session["user_id"]))
                db.commit()
                session["team_id"] = team["id"]
                flash(f"Team '{name}' created! Invite code: {code}", "success")
                return redirect(url_for("team_detail", tid=team["id"]))
            except sqlite3.IntegrityError:
                flash("Team name already taken.", "danger")

    return render_template("team_create.html")


@app.route("/teams/join", methods=["GET", "POST"])
@login_required
def team_join():
    with get_db() as db:
        current_team = _user_team_id(db, session["user_id"])
    if current_team:
        flash("You are already in a team.", "warning")
        return redirect(url_for("team_detail", tid=current_team))

    if request.method == "POST":
        code = request.form.get("invite_code", "").strip().upper()
        with get_db() as db:
            team = db.execute(
                "SELECT * FROM teams WHERE invite_code = ?", (code,)
            ).fetchone()
            if not team:
                flash("Invalid invite code.", "danger")
                return render_template("team_join.html")

            member_count = db.execute(
                "SELECT COUNT(*) FROM users WHERE team_id = ?", (team["id"],)
            ).fetchone()[0]

            if member_count >= MAX_TEAM_SIZE:
                flash(
                    f"Team '{team['name']}' is full ({MAX_TEAM_SIZE}/{MAX_TEAM_SIZE} members).",
                    "danger"
                )
                return render_template("team_join.html")

            db.execute("UPDATE users SET team_id = ? WHERE id = ?",
                       (team["id"], session["user_id"]))
            db.commit()
            session["team_id"] = team["id"]
            flash(f"Joined team '{team['name']}'!", "success")
            return redirect(url_for("team_detail", tid=team["id"]))

    return render_template("team_join.html")


@app.route("/teams/leave", methods=["POST"])
@login_required
def team_leave():
    with get_db() as db:
        db.execute("UPDATE users SET team_id = NULL WHERE id = ?", (session["user_id"],))
        db.commit()
    session["team_id"] = None
    flash("You have left your team.", "info")
    return redirect(url_for("home"))


@app.route("/teams/<int:tid>")
@login_required
def team_detail(tid):
    with get_db() as db:
        team = db.execute("SELECT * FROM teams WHERE id = ?", (tid,)).fetchone()
        if not team:
            flash("Team not found.", "danger")
            return redirect(url_for("scoreboard"))
        members = db.execute(
            "SELECT id, username, score FROM users WHERE team_id = ? ORDER BY score DESC",
            (tid,)
        ).fetchall()
        solved_challenges = db.execute("""
            SELECT c.name, c.points, ts.solved_at, u.username as solver
            FROM team_solves ts
            JOIN challenges c ON c.id = ts.challenge_id
            JOIN users u ON u.id = ts.user_id
            WHERE ts.team_id = ? ORDER BY ts.solved_at ASC
        """, (tid,)).fetchall()
        viewer_team = _user_team_id(db, session["user_id"])
        is_member   = (viewer_team == tid)
    return render_template("team_detail.html", team=team, members=members,
                           solved_challenges=solved_challenges,
                           is_member=is_member, max_team=MAX_TEAM_SIZE)


# ─── challenges ───────────────────────────────────────────────────────────────

@app.route("/challenges")
@login_required
@team_required
def challenges():
    open_, state, boundary = ctf_is_open()
    start, end = get_ctf_window()
    # Only hard-lock before the CTF starts; after it ends, show read-only
    if state == "not_started":
        return render_template("challenges.html", ctf_locked=True,
                               ctf_state=state, boundary=boundary,
                               ctf_start=start, ctf_end=end,
                               challenges=[], solved_ids=set(), solve_counts={})
    with get_db() as db:
        chs = db.execute("SELECT * FROM challenges ORDER BY points ASC").fetchall()
        solved_ids = {r["challenge_id"] for r in db.execute(
            "SELECT challenge_id FROM solves WHERE user_id = ?", (session["user_id"],)
        ).fetchall()}
        solve_counts = {r["challenge_id"]: r["cnt"] for r in db.execute(
            "SELECT challenge_id, COUNT(*) as cnt FROM solves GROUP BY challenge_id"
        ).fetchall()}
    return render_template("challenges.html", ctf_locked=False,
                           ctf_state=state, boundary=boundary,
                           ctf_start=start, ctf_end=end,
                           challenges=chs, solved_ids=solved_ids, solve_counts=solve_counts)


@app.route("/challenges/<int:cid>")
@login_required
@team_required
def challenge_detail(cid):
    open_, state, boundary = ctf_is_open()
    # Only block access before the CTF starts
    if state == "not_started":
        flash("Challenges are not open yet.", "warning")
        return redirect(url_for("challenges"))
    ctf_ended = (state == "ended")
    with get_db() as db:
        ch = db.execute("SELECT * FROM challenges WHERE id = ?", (cid,)).fetchone()
        if not ch:
            flash("Challenge not found.", "danger")
            return redirect(url_for("challenges"))
        solved = db.execute(
            "SELECT 1 FROM solves WHERE user_id=? AND challenge_id=?",
            (session["user_id"], cid)
        ).fetchone() is not None
        solve_count = db.execute(
            "SELECT COUNT(*) FROM solves WHERE challenge_id=?", (cid,)
        ).fetchone()[0]
        solvers = db.execute("""
            SELECT u.username, s.solved_at FROM solves s
            JOIN users u ON u.id = s.user_id
            WHERE s.challenge_id=? ORDER BY s.solved_at ASC LIMIT 10
        """, (cid,)).fetchall()
        cutoff = (datetime.utcnow() - timedelta(seconds=COOLDOWN_SECONDS)).strftime("%Y-%m-%d %H:%M:%S")
        recent_wrong = db.execute("""
            SELECT COUNT(*) FROM flag_attempts
            WHERE user_id=? AND challenge_id=? AND attempted_at > ?
        """, (session["user_id"], cid, cutoff)).fetchone()[0]
        locked = (not solved) and (recent_wrong >= ATTEMPT_LIMIT)
    return render_template("challenge_detail.html", ch=ch, solved=solved,
                           solve_count=solve_count, solvers=solvers,
                           locked=locked, ctf_ended=ctf_ended,
                           attempts_left=max(0, ATTEMPT_LIMIT - recent_wrong),
                           cooldown=COOLDOWN_SECONDS)


# ─── flag submit API ──────────────────────────────────────────────────────────

@app.route("/api/submit/<int:cid>", methods=["POST"])
@login_required
@team_required
def submit_flag(cid):
    _, state, _ = ctf_is_open()
    if state == "not_started":
        return jsonify({"status": "error", "msg": "CTF has not started yet."})
    if state == "ended":
        return jsonify({"status": "error", "msg": "CTF has ended. Submissions are closed."})

    flag = request.form.get("flag", "").strip()
    uid  = session["user_id"]

    with get_db() as db:
        ch = db.execute("SELECT * FROM challenges WHERE id=?", (cid,)).fetchone()
        if not ch:
            return jsonify({"status": "error", "msg": "Challenge not found"}), 404

        if db.execute("SELECT 1 FROM solves WHERE user_id=? AND challenge_id=?",
                      (uid, cid)).fetchone():
            return jsonify({"status": "already", "msg": "Already solved!"})

        cutoff = (datetime.utcnow() - timedelta(seconds=COOLDOWN_SECONDS)).strftime("%Y-%m-%d %H:%M:%S")
        recent = db.execute("""
            SELECT COUNT(*) FROM flag_attempts
            WHERE user_id=? AND challenge_id=? AND attempted_at > ?
        """, (uid, cid, cutoff)).fetchone()[0]

        if recent >= ATTEMPT_LIMIT:
            return jsonify({
                "status": "locked",
                "msg": f"Too many wrong attempts. Wait {COOLDOWN_SECONDS}s."
            })

        if flag == ch["flag"]:
            db.execute("INSERT INTO solves (user_id, challenge_id) VALUES (?,?)", (uid, cid))
            db.execute("UPDATE users SET score = score + ? WHERE id=?", (ch["points"], uid))

            team_id = _user_team_id(db, uid)
            if team_id:
                if not db.execute(
                    "SELECT 1 FROM team_solves WHERE team_id=? AND challenge_id=?",
                    (team_id, cid)
                ).fetchone():
                    db.execute(
                        "INSERT INTO team_solves (team_id,challenge_id,user_id) VALUES (?,?,?)",
                        (team_id, cid, uid)
                    )
                    db.execute("UPDATE teams SET score = score + ? WHERE id=?",
                               (ch["points"], team_id))

            db.commit()
            return jsonify({
                "status": "correct",
                "msg": f"Correct flag! +{ch['points']} points.",
                "points": ch["points"]
            })

        db.execute("INSERT INTO flag_attempts (user_id, challenge_id) VALUES (?,?)", (uid, cid))
        db.commit()
        attempts_left = max(0, ATTEMPT_LIMIT - (recent + 1))
        return jsonify({
            "status": "wrong",
            "msg": f"Wrong flag. {attempts_left} attempt(s) left before cooldown."
        })



# ─── scoreboard ───────────────────────────────────────────────────────────────

@app.route("/scoreboard")
def scoreboard():
    with get_db() as db:
        teams = db.execute("""
            SELECT t.id, t.name, t.score,
                   COUNT(ts.id) as solve_count,
                   MAX(ts.solved_at) as last_solve
            FROM teams t
            LEFT JOIN team_solves ts ON ts.team_id = t.id
            GROUP BY t.id
            ORDER BY t.score DESC, last_solve ASC
        """).fetchall()
        viewer_team_id = session.get("team_id")
        if viewer_team_id:
            players = db.execute("""
                SELECT u.id, u.username, u.score, t.name as team_name,
                       COUNT(s.id) as solve_count,
                       MAX(s.solved_at) as last_solve
                FROM users u
                JOIN teams t ON t.id = u.team_id
                LEFT JOIN solves s ON s.user_id = u.id
                WHERE u.team_id = ?
                GROUP BY u.id
                ORDER BY u.score DESC, last_solve ASC
            """, (viewer_team_id,)).fetchall()
        else:
            players = []
        challenges = db.execute(
            "SELECT id, name, points, difficulty FROM challenges ORDER BY points ASC"
        ).fetchall()
        total_points = sum(c["points"] for c in challenges)

        # Per-team: members + solved challenge IDs
        team_details = []
        for t in teams:
            members = db.execute(
                "SELECT username, score FROM users WHERE team_id=? ORDER BY score DESC",
                (t["id"],)
            ).fetchall()
            solved_ids = {r["challenge_id"] for r in db.execute(
                "SELECT challenge_id FROM team_solves WHERE team_id=?", (t["id"],)
            ).fetchall()}
            team_details.append({
                "id":        t["id"],
                "name":      t["name"],
                "score":     t["score"],
                "solve_count": t["solve_count"],
                "last_solve":  t["last_solve"],
                "members":   members,
                "solved_ids": solved_ids,
            })

    return render_template("scoreboard.html", teams=teams, players=players,
                           team_details=team_details, challenges=challenges,
                           total_points=total_points)


# ─── admin ────────────────────────────────────────────────────────────────────

@app.route("/yournotallow")
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html")


@app.route("/yournotallow/auth", methods=["POST"])
def admin_auth():
    if request.form.get("password", "") == ADMIN_PASSWORD:
        session["is_admin"] = True
        return redirect(url_for("admin_dashboard"))
    flash("Wrong admin password.", "danger")
    return render_template("admin_login.html")


@app.route("/yournotallow/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


@app.route("/yournotallow/dashboard")
@admin_required
def admin_dashboard():
    with get_db() as db:
        emails = db.execute("SELECT * FROM allowed_emails ORDER BY email").fetchall()
        users  = db.execute("""
            SELECT u.id, u.username, u.email, u.score, u.created_at, t.name as team_name
            FROM users u LEFT JOIN teams t ON t.id = u.team_id
            ORDER BY u.created_at DESC
        """).fetchall()
        teams  = db.execute("""
            SELECT t.*, COUNT(u.id) as member_count
            FROM teams t LEFT JOIN users u ON u.team_id = t.id
            GROUP BY t.id ORDER BY t.score DESC
        """).fetchall()
        stats  = {
            "total_users":      db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "total_teams":      db.execute("SELECT COUNT(*) FROM teams").fetchone()[0],
            "total_solves":     db.execute("SELECT COUNT(*) FROM solves").fetchone()[0],
            "whitelist_active": db.execute("SELECT COUNT(*) FROM allowed_emails").fetchone()[0] > 0,
        }
    ctf_start, ctf_end = get_ctf_window()
    open_, ctf_state, _ = ctf_is_open()
    return render_template("admin_dashboard.html", emails=emails, users=users,
                           teams=teams, stats=stats, max_team=MAX_TEAM_SIZE,
                           ctf_start=ctf_start, ctf_end=ctf_end,
                           ctf_state=ctf_state, ctf_open=open_)


@app.route("/yournotallow/settings/time", methods=["POST"])
@admin_required
def admin_set_time():
    def parse_dt(val):
        val = val.strip()
        if not val:
            return None
        # datetime-local gives "YYYY-MM-DDTHH:MM"
        try:
            return datetime.strptime(val, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None

    start_str = parse_dt(request.form.get("start_time", ""))
    end_str   = parse_dt(request.form.get("end_time", ""))

    with get_db() as db:
        db.execute("""
            INSERT INTO ctf_settings (id, start_time, end_time) VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET start_time=excluded.start_time, end_time=excluded.end_time
        """, (start_str, end_str))
        db.commit()

    flash("CTF time window updated.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/yournotallow/emails/add", methods=["POST"])
@admin_required
def admin_add_email():
    email = request.form.get("email", "").strip().lower()
    note  = request.form.get("note", "").strip()
    if not email:
        flash("Email cannot be empty.", "danger")
        return redirect(url_for("admin_dashboard"))
    with get_db() as db:
        try:
            db.execute("INSERT INTO allowed_emails (email, note) VALUES (?,?)", (email, note))
            db.commit()
            flash(f"Added '{email}' to whitelist.", "success")
        except sqlite3.IntegrityError:
            flash(f"'{email}' is already whitelisted.", "warning")
    return redirect(url_for("admin_dashboard"))


@app.route("/yournotallow/emails/remove/<int:eid>", methods=["POST"])
@admin_required
def admin_remove_email(eid):
    with get_db() as db:
        row = db.execute("SELECT email FROM allowed_emails WHERE id=?", (eid,)).fetchone()
        if row:
            db.execute("DELETE FROM allowed_emails WHERE id=?", (eid,))
            db.commit()
            flash(f"Removed '{row['email']}' from whitelist.", "info")
    return redirect(url_for("admin_dashboard"))


@app.route("/yournotallow/users/remove/<int:uid>", methods=["POST"])
@admin_required
def admin_remove_user(uid):
    with get_db() as db:
        row = db.execute("SELECT username FROM users WHERE id=?", (uid,)).fetchone()
        if row:
            db.execute("DELETE FROM solves WHERE user_id=?", (uid,))
            db.execute("DELETE FROM hints_used WHERE user_id=?", (uid,))
            db.execute("DELETE FROM flag_attempts WHERE user_id=?", (uid,))
            db.execute("DELETE FROM users WHERE id=?", (uid,))
            db.commit()
            flash(f"User '{row['username']}' removed.", "info")
    return redirect(url_for("admin_dashboard"))


@app.route("/yournotallow/teams/remove/<int:tid>", methods=["POST"])
@admin_required
def admin_remove_team(tid):
    with get_db() as db:
        row = db.execute("SELECT name FROM teams WHERE id=?", (tid,)).fetchone()
        if row:
            db.execute("UPDATE users SET team_id=NULL WHERE team_id=?", (tid,))
            db.execute("DELETE FROM team_solves WHERE team_id=?", (tid,))
            db.execute("DELETE FROM teams WHERE id=?", (tid,))
            db.commit()
            flash(f"Team '{row['name']}' dissolved.", "info")
    return redirect(url_for("admin_dashboard"))


# ─── challenge reverse proxy ──────────────────────────────────────────────────

_PORT_TO_SERVICE = {
    5001: "ch47", 5002: "ch48", 5003: "ch49", 5004: "ch50",
    5005: "ch51", 5006: "ch52", 5007: "ch53", 5008: "ch54",
}

_ABS_PATH_RE = re.compile(r'((?:href|src|action)=["\'])(/(?!//))')


def _rewrite_html(html_bytes, proxy_prefix):
    """Prepend proxy_prefix to every absolute-path URL in HTML."""
    html = html_bytes.decode("utf-8", errors="replace")
    html = _ABS_PATH_RE.sub(lambda m: m.group(1) + proxy_prefix + "/", html)
    return html.encode("utf-8")


@app.route("/proxy/<int:port>", defaults={"subpath": ""})
@app.route("/proxy/<int:port>/", defaults={"subpath": ""})
@app.route("/proxy/<int:port>/<path:subpath>")
@login_required
def challenge_proxy(port, subpath):
    service = _PORT_TO_SERVICE.get(port)
    if not service:
        return "Invalid challenge port", 404

    target = f"http://{service}:5000/{subpath}"
    if request.query_string:
        target += "?" + request.query_string.decode()

    proxy_prefix = f"/proxy/{port}"

    # Forward only safe headers; drop hop-by-hop and host
    skip = {"host", "content-length", "transfer-encoding", "connection"}
    fwd_headers = {k: v for k, v in request.headers if k.lower() not in skip}

    try:
        resp = ext_requests.request(
            method=request.method,
            url=target,
            headers=fwd_headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=10,
        )
    except ext_requests.exceptions.RequestException:
        return "<h2>Challenge service unavailable. Please try again.</h2>", 502

    content_type = resp.headers.get("content-type", "")
    content = resp.content

    if "text/html" in content_type:
        content = _rewrite_html(content, proxy_prefix)

    # Build response headers — strip hop-by-hop, rewrite Location
    drop = {"content-encoding", "content-length", "transfer-encoding", "connection"}
    out_headers = {}
    for k, v in resp.headers.items():
        if k.lower() in drop:
            continue
        if k.lower() == "location" and v.startswith("/"):
            v = proxy_prefix + v
        out_headers[k] = v

    return Response(content, status=resp.status_code,
                    headers=out_headers, content_type=content_type)


# ─── entry ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000, debug=False)
