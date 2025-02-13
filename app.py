from flask import Flask, render_template, request, redirect, session, url_for, flash, send_file
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
import qrcode
import os
import urllib.parse
from io import BytesIO
import base64
import io

app = Flask(__name__)
app.config.from_object(config)

# Session & Rate-Limiting aktivieren
Session(app)
limiter = Limiter(key_func=get_remote_address, default_limits=[config.RATE_LIMIT])
limiter.init_app(app)


def generate_qr_code(uri):
    img = qrcode.make(uri)
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


# Datenbank-Verbindung und Insert-Funktion
def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'users.db')
    conn = sqlite3.connect(db_path)
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
            return redirect(url_for("verify_2fa"))  # Zu 2FA-Überprüfung weiterleiten
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
            return redirect(url_for("show_2fa", email=email))  # Weiterleitung zur 2FA-Seite
        except sqlite3.IntegrityError:
            flash("Benutzername oder E-Mail bereits vergeben.", "danger")
    
    return render_template("register.html")


@app.route("/2fa/<email>", methods=["GET", "POST"])
def show_2fa(email):
    # Mit der Datenbank verbinden und das Benutzer-TOTP-Secret abfragen
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT totp_secret FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if not user:
        flash("Benutzer nicht gefunden.", "danger")
        return redirect(url_for("register"))

    secret = user[0]
    
    # URL-codierte E-Mail-Adresse
    encoded_email = urllib.parse.quote(email)
    
    # URI für den QR-Code generieren
    totp_uri = f"otpauth://totp/SecureLoginApp:{encoded_email}?secret={secret}&issuer=SecureLoginApp"
    
    # QR-Code aus der URI generieren
    img = qrcode.make(totp_uri)
    
    # QR-Code in einen BytesIO-Stream speichern
    img_stream = io.BytesIO()
    img.save(img_stream, format='PNG')
    img_stream.seek(0)

    # QR-Code als Base64-kodiertes Bild für das Template bereitstellen
    img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')

    if request.method == "POST":
        # Der Benutzer hat den 2FA-Code eingegeben, also überprüfen
        code = request.form["code"]
        
        # Überprüfen des TOTP-Codes
        if verify_totp(secret, code):
            # Code ist korrekt, Benutzer einloggen und weiterleiten
            flash("2FA erfolgreich abgeschlossen!", "success")
            return redirect(url_for("login"))
        else:
            flash("Falscher 2FA-Code. Bitte versuche es noch einmal.", "danger")

    return render_template("2fa.html", totp_uri=totp_uri, img_base64=img_base64)


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
