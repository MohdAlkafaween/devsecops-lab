import os
import sqlite3
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# FLAW 1 (Gitleaks): hardcoded credential
INTERNAL_API_TOKEN = "kT9pR2mWx7QvL4nB8zYcF6hJ3dS5aG1uE0iO9rXw"

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
    # FLAW 2 (Semgrep): SQL injection - user input concatenated into query
    user_id = request.args.get("id")
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = '" + user_id + "'")
    return jsonify(rows=cur.fetchall())

@app.route("/ping")
def ping():
    # FLAW 3 (Semgrep): command injection - user input into shell
    host = request.args.get("host")
    output = subprocess.check_output("ping -c 1 " + host, shell=True)
    return output

@app.route("/greet")
def greet():
    # FLAW 4 (ZAP): reflected XSS - user input echoed into HTML
    name = request.args.get("name", "guest")
    return f"<h1>Hello {name}</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
