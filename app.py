from flask import Flask, request, redirect, url_for, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "CLAVE_SIMPLE"

# ==============================
# BASE DE DATOS
# ==============================
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

# Crear BD + usuarios
with app.app_context():
    db.create_all()

    if not Usuario.query.filter_by(username="demo").first():
        db.session.add(Usuario(username="demo", password="demo123"))

    if not Usuario.query.filter_by(username="miguel").first():
        db.session.add(Usuario(username="miguel", password="prueba"))

    db.session.commit()

# ==============================
# HTML
# ==============================
HTML_HOME = """
<h1>App Flask</h1>

{% if "usuario" in session %}
    <p>Bienvenido {{ session["usuario"] }}</p>
    <a href="/privado">Zona privada</a><br>
    <a href="/logout">Cerrar sesión</a>
{% else %}
    <a href="/login">Ir a login</a>
{% endif %}
"""

HTML_LOGIN = """
<h1>Login</h1>

{% if error %}
<p style="color:red">{{ error }}</p>
{% endif %}

<form method="post">
    <input name="username" placeholder="Usuario"><br><br>
    <input name="password" type="password" placeholder="Contraseña"><br><br>
    <button>Entrar</button>
</form>
"""

HTML_PRIVADO = """
<h1>Zona privada</h1>
<p>Hola {{ session["usuario"] }}</p>
<a href="/logout">Cerrar sesión</a>
"""

# ==============================
# RUTAS
# ==============================
@app.route("/")
def home():
    return render_template_string(HTML_HOME)

@app.route("/login", methods=["GET", "POST"])
def login():
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

    return render_template_string(HTML_LOGIN, error=error)

@app.route("/privado")
def privado():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template_string(HTML_PRIVADO)

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
