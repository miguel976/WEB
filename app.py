from flask import Flask, request, redirect, url_for, session, render_template_string

app = Flask(__name__)
app.secret_key = "CLAVE_FIJA_DE_PRUEBA_2026"

USUARIO_PRUEBA = "demo"
CLAVE_PRUEBA = "demo123"

HTML_HOME = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Inicio</title>
</head>
<body>
    <h1>App web simple en Flask</h1>

    {% if "usuario" in session %}
        <p>Bienvenido, {{ session["usuario"] }}</p>
        <p><a href="{{ url_for('privado') }}">Ir a zona privada</a></p>
        <p><a href="{{ url_for('logout') }}">Cerrar sesión</a></p>
    {% else %}
        <p>No has iniciado sesión.</p>
        <p><a href="{{ url_for('login') }}">Ir a login</a></p>
    {% endif %}
</body>
</html>
"""

HTML_LOGIN = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Login</title>
</head>
<body>
    <h1>Iniciar sesión</h1>

    {% if error %}
        <p style="color:red;">{{ error }}</p>
    {% endif %}

    <form method="post">
        <label>Usuario:</label><br>
        <input type="text" name="username" required><br><br>

        <label>Contraseña:</label><br>
        <input type="password" name="password" required><br><br>

        <button type="submit">Entrar</button>
    </form>

    <br>
    <a href="{{ url_for('home') }}">Volver al inicio</a>
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
    <p>Has iniciado sesión como: <b>{{ session["usuario"] }}</b></p>
    <p>Este contenido solo lo ve un usuario autenticado.</p>
    <p><a href="{{ url_for('logout') }}">Cerrar sesión</a></p>
    <p><a href="{{ url_for('home') }}">Volver al inicio</a></p>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_HOME)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == USUARIO_PRUEBA and password == CLAVE_PRUEBA:
            session["usuario"] = username
            return redirect(url_for("privado"))
        else:
            error = "Usuario o contraseña incorrectos"

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
