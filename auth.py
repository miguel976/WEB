from flask import Flask, redirect, url_for, session, render_template_string
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)

# ==============================
# CONFIGURACIÓN DIRECTA EN CÓDIGO
# ==============================
app.secret_key = "CLAVE_SUPER_LARGA_Y_ALEATORIA_2026_CAMBIAR_EN_PRODUCCION"

GOOGLE_CLIENT_ID = "966775310840-78j9h1djoobjsbff5qd2n00va59cmljs.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "AIzaSyA2W9x8d7dmCCEp_xYwoDLAsn48BTtZzX0"

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False  # Cambiar a True si usas HTTPS real
)

# ==============================
# OAUTH GOOGLE
# ==============================
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
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Inicio</title>
</head>
<body>
    <h1>Login con Google en Flask</h1>

    {% if user %}
        <p><b>Nombre:</b> {{ user.get("name", "N/A") }}</p>
        <p><b>Correo:</b> {{ user.get("email", "N/A") }}</p>
        <p><b>Correo verificado:</b> {{ user.get("email_verified", False) }}</p>

        {% if user.get("picture") %}
            <p><img src="{{ user.get('picture') }}" width="100" alt="Foto de perfil"></p>
        {% endif %}

        <p><a href="{{ url_for('privado') }}">Ir a zona privada</a></p>
        <p><a href="{{ url_for('logout') }}">Cerrar sesión</a></p>
    {% else %}
        <p>No has iniciado sesión.</p>
        <p><a href="{{ url_for('login') }}">Iniciar sesión con Google</a></p>
    {% endif %}
</body>
</html>
"""

HTML_PRIVADO = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Zona privada</title>
</head>
<body>
    <h1>Zona privada</h1>
    <p>Has iniciado sesión como: <b>{{ user.get("email", "N/A") }}</b></p>
    <p>Nombre: <b>{{ user.get("name", "N/A") }}</b></p>
    <p>Este contenido solo es visible para usuarios autenticados con Google.</p>
    <p><a href="{{ url_for('home') }}">Volver al inicio</a></p>
    <p><a href="{{ url_for('logout') }}">Cerrar sesión</a></p>
</body>
</html>
"""

# ==============================
# RUTAS
# ==============================
@app.route("/")
def home():
    user = session.get("user")
    return render_template_string(HTML_HOME, user=user)

@app.route("/login")
def login():
    redirect_uri = url_for("auth_callback", _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/callback")
def auth_callback():
    token = google.authorize_access_token()
    user_info = token.get("userinfo")

    if not user_info:
        user_info = google.userinfo()

    session["user"] = {
        "sub": user_info.get("sub"),
        "name": user_info.get("name"),
        "email": user_info.get("email"),
        "email_verified": user_info.get("email_verified"),
        "picture": user_info.get("picture"),
    }

    return redirect(url_for("privado"))

@app.route("/privado")
def privado():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    return render_template_string(HTML_PRIVADO, user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
