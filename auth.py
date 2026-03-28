from flask import Flask, redirect, url_for, session, render_template_string, request, flash
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ==============================
# CONFIGURACIÓN
# ==============================
app.secret_key = os.environ.get("SECRET_KEY", "CLAVE_DEFAULT")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True
)

# ==============================
# BASE DE DATOS (SIMPLE)
# ==============================
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

# Crear BD + usuario demo
with app.app_context():
    db.create_all()

    if not Usuario.query.filter_by(username="demo").first():
        user = Usuario(username="demo", password="demo123")
        db.session.add(user)
        db.session.commit()

# ==============================
# OAUTH GOOGLE
# ==============================
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    },
)

# ==============================
# HTML
# ==============================
HTML_HOME = """
<h1>Login Flask</h1>

{% if user or usuario %}
    <p>Bienvenido</p>
    <a href="{{ url_for('privado') }}">Zona privada</a><br>
    <a href="{{ url_for('logout') }}">Cerrar sesión</a>
{% else %}
    <a href="{{ url_for('login') }}">Login con Google</a><br><br>
    <a href="{{ url_for('login_local') }}">Login con usuario</a>
{% endif %}
"""

HTML_PRIVADO = """
<h1>Zona privada</h1>
<p>Acceso autorizado</p>

<a href="{{ url_for('logout') }}">Cerrar sesión</a>
"""

# ==============================
# RUTAS
# ==============================
@app.route("/")
def home():
    return render_template_string(
        HTML_HOME,
        user=session.get("user"),
        usuario=session.get("usuario")
    )

# -------- LOGIN GOOGLE --------
@app.route("/login")
def login():
    redirect_uri = url_for("auth_callback", _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/callback")
def auth_callback():
    token = google.authorize_access_token()
    user_info = token.get("userinfo")

    session["user"] = user_info
    return redirect(url_for("privado"))

# -------- LOGIN LOCAL (BD) --------
@app.route("/login-local", methods=["GET", "POST"])
def login_local():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = Usuario.query.filter_by(username=username, password=password).first()

        if user:
            session["usuario"] = user.username
            return redirect(url_for("privado"))
        else:
            error = "Credenciales incorrectas"

    return """
    <h2>Login con base de datos</h2>
    <form method="post">
        <input name="username" placeholder="Usuario"><br><br>
        <input name="password" type="password" placeholder="Contraseña"><br><br>
        <button>Entrar</button>
    </form>
    """ + (f"<p style='color:red'>{error}</p>" if error else "")

# -------- PRIVADO --------
@app.route("/privado")
def privado():
    if not session.get("user") and not session.get("usuario"):
        return redirect(url_for("home"))

    return render_template_string(HTML_PRIVADO)

# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
