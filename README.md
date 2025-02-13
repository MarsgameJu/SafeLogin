Hier ist eine aktualisierte und vollständige Version der `README.md` und `requirements.txt` basierend auf den neuesten Änderungen.

### **README.md**

```markdown
# SafeLogin - Secure User Authentication with Flask  

SafeLogin is a Flask-based web application that provides **secure user authentication** with modern security features.

## 🚀 Features

✅ **Secure Password Storage** – Hashed with `bcrypt`  
✅ **Two-Factor Authentication (2FA)** – Google Authenticator support  
✅ **Session Management** – Secure and configurable sessions  
✅ **Rate Limiting** – Protects against brute-force attacks  
✅ **SQLite Database** – Simple and efficient user storage  
✅ **Static File Security** – QR code is accessible only during registration

---

## 🔒 Security  

- **Passwords are hashed** (never stored in plain text).  
- **Two-Factor Authentication (2FA)** provides extra security.  
- **Rate Limiting** prevents excessive login attempts.  
- **Sessions are securely stored and managed**.  
- **Static files (QR codes)** are protected to avoid unauthorized access.

---

## 📥 Installation  

### 1️⃣ Clone the repository  

```sh
git clone https://github.com/your-user/safelogin.git
cd safelogin
```

### 2️⃣ Create a virtual environment (recommended)  

```sh
python -m venv venv
source venv/bin/activate  # macOS & Linux
venv\Scripts\activate  # Windows
```

### 3️⃣ Install dependencies  

```sh
pip install -r requirements.txt
```

### 4️⃣ Set up the database  
Make sure the SQLite database is set up correctly. You can manually create it, or it will be created automatically when the app runs.

### 5️⃣ Start the application  

```sh
python app.py
```

🔗 **Now visit:** [`http://127.0.0.1:5000`](http://127.0.0.1:5000)  

---

## 🎮 How to Use

### Register a New User
1. Go to [`http://127.0.0.1:5000/register`](http://127.0.0.1:5000/register).
2. Enter a **username**, **email**, and **password**.
3. Scan the **QR code** for 2FA (Google Authenticator).
4. Enter the generated **authentication code**.
5. 🎉 **Done!** You are now registered.

### Login
1. Visit [`http://127.0.0.1:5000/login`](http://127.0.0.1:5000/login).
2. Enter your **email** and **password**.
3. Enter your **2FA code** from Google Authenticator.
4. ✅ If successful, you will be redirected to the **dashboard**.

---

## 📁 Project Structure  

```
SafeLogin/
│── static/              # Static files (CSS, JS, images)
│   ├── style.css        # Dark mode styling
│── templates/           # HTML templates for Flask
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── 2fa.html         # 2FA verification page
│   ├── dashboard.html   # Dashboard after login
│── utils/               # Helper functions for security & database
│   ├── database.py      # SQLite database connection
│   ├── security.py      # Password hashing and 2FA functions
│── app.py               # Main Flask application
│── config.py            # Configuration settings
│── requirements.txt     # Dependencies
│── README.md            # Documentation
```

---

## ⚙️ Configuration  

Modify `config.py` to customize settings:  

```python
SECRET_KEY = "your-secret-key"
SESSION_TYPE = "filesystem"
RATE_LIMIT = "5 per minute"  # Limits to 5 requests per minute
```

🔴 **Important:** Replace `SECRET_KEY` with a strong random value!  

---

## 👥 Contributors

If you have any suggestions, bug reports, or pull requests, feel free to contribute! 🎉

```

### **requirements.txt**

```text
Flask==2.2.3
Flask-Limiter==2.1.0
Flask-SQLAlchemy==3.0.3
pyotp==2.8.0
bcrypt==4.0.1
qrcode==7.3.1
```

