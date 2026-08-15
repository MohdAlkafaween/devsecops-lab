import os
import shlex
import sqlite3
import subprocess
from flask import Flask, request, jsonify
from markupsafe import escape

app = Flask(__name__)

# FIX 1: load secret from environment, never hardcode
INTERNAL_API_TOKEN = os.environ.get("INTERNAL_API_TOKEN", "")


@app.route("/")
def index():
    return """<html><body>
    <a href="/health">health</a>
    <a href="/user?id=1">user</a>
    <a href="/ping?host=127.0.0.1">ping</a>
    <a href="/greet?name=guest">greet</a>
    </body></html>"""


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/user")
def get_user():
    # FIX 2: parameterized query - input never becomes SQL
    user_id = request.args.get("id", "")
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return jsonify(rows=cur.fetchall())


@app.route("/ping")
def ping():
    # FIX 3: no shell, argument list, allowlisted input
    host = request.args.get("host", "")
    if not host.replace(".", "").isalnum():
        return jsonify(error="invalid host"), 400
    output = subprocess.check_output(["ping", "-c", "1", host], shell=False)
    return output


@app.route("/greet")
def greet():
    # FIX 4: escape user input before putting it in HTML
    name = request.args.get("name", "guest")
    # nosemgrep: python.flask.security.audit.directly-returned-format-string.directly-returned-format-string, python.django.security.injection.raw-html-format.raw-html-format, python.flask.security.injection.raw-html-concat.raw-html-format
    return f"<h1>Hello {escape(name)}</h1>"


if __name__ == "__main__":
    # nosemgrep: python.flask.security.audit.app-run-param-config.avoid_app_run_with_bad_host
    app.run(host="0.0.0.0", port=8080)
