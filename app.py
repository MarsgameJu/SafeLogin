from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
import sqlite3
import bcrypt
import pyotp
from utils.database import get_db
from utils.security import hash_password, verify_password, generate_totp_secret, get_totp_uri, verify_totp
import config
import time

app = Flask(__name__)
app.config.from_object(config)

# Session & Rate-Limiting aktivieren
Session(app)
limiter = Limiter(get_remote_address, app=app, default_limits=[config.RATE_LIMIT])

# Datenbank-Verbindung und Insert-Funktion
def get_db():
    conn = sqlite3.connect('user.db')
    conn.execute('PRAGMA journal_mode=WAL;')  # WAL-Modus aktivieren
    conn.row_factory = sqlite3.Row  # Optional, falls du Zugriff auf die Spaltennamen brauchst
    return conn

def insert_user_to_db(username, email, hashed_pw, totp_secret):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password, totp_secret) VALUES (?, ?, ?, ?)",
                       (username, email, hashed_pw, totp_secret))
        conn.commit()
        conn.close()  # Verbindung nach dem Commit schließen
    except sqlite3.OperationalError:
        time.sleep(1)  # Kurz warten und dann erneut versuchen
        insert_user_to_db(username, email, hashed_pw, totp_secret)

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password, totp_secret FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user and verify_password(password, user[1]):
            session["temp_user_id"] = user[0]
            session["temp_totp_secret"] = user[2]
            return redirect(url_for("verify_2fa"))
        else:
            flash("Falsche Anmeldedaten.", "danger")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_pw = hash_password(password)
        totp_secret = generate_totp_secret()

        try:
            insert_user_to_db(username, email, hashed_pw, totp_secret)
            flash("Registrierung erfolgreich! Richten Sie nun 2FA ein.", "success")
            return redirect(url_for("show_2fa", email=email))
        except sqlite3.IntegrityError:
            flash("Benutzername oder E-Mail bereits vergeben.", "danger")
    
    return render_template("register.html")

@app.route("/2fa/<email>")
def show_2fa(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT totp_secret FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user:
        flash("Benutzer nicht gefunden.", "danger")
        return redirect(url_for("register"))

    secret = user[0]
    totp_uri = get_totp_uri(secret, email)
    return render_template("2fa.html", totp_uri=totp_uri)

@app.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():
    if "temp_user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        code = request.form["code"]
        if verify_totp(session["temp_totp_secret"], code):
            session["user_id"] = session.pop("temp_user_id")
            return redirect(url_for("dashboard"))
        else:
            flash("Ungültiger 2FA-Code.", "danger")

    return render_template("2fa.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return "Willkommen im Dashboard!"

@app.route("/logout")
def logout():
    session.clear()
    flash("Erfolgreich abgemeldet.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
