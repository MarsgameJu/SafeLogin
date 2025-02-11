import os

SECRET_KEY = os.urandom(32)  # Sicherer Schlüssel
SESSION_TYPE = "filesystem"
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True  # Signierte Cookies
SESSION_COOKIE_SECURE = True  # Nur HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
RATE_LIMIT = "5 per minute"  # Max. 5 Login-Versuche pro Minute
