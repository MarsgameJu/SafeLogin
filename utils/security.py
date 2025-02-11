import bcrypt
import pyotp

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def generate_totp_secret():
    return pyotp.random_base32()

def get_totp_uri(secret, email):
    return pyotp.totp.TOTP(secret).provisioning_uri(email, issuer_name="SecureLoginApp")

def verify_totp(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
