import os
from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# SEGURIDAD: Lee la URL desde las variables de entorno de Vercel
# Si estás probando localmente, puedes reemplazar esto temporalmente por tu URL
URL_API = os.getenv("APPS_SCRIPT_URL")

HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Inscripción Laboratorios - UNTREF</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
    <style>
        body { background-color: #f4f6f9; }
        .box { border-top: 4px solid #003366; border-radius: 8px; }
        .button.is-link { background-color: #003366; }
    </style>
</head>
<body>
    <section class="section">
        <div class="container" style="max-width: 500px;">
            <div class="has-text-centered mb-5">
                <h1 class="title is-3">Reserva de Vacantes</h1>
                <p class="subtitle is-6">Cátedras de Informática</p>
            </div>
            <div class="box">
                <form method="POST">
                    <div class="field">
                        <label class="label">Nombre y Apellido</label>
                        <div class="control"><input class="input" type="text" name="nombre" required></div>
                    </div>
                    <div class="field">
                        <label class="label">DNI</label>
                        <div class="control"><input class="input" type="number" name="dni" placeholder="Sin puntos ni espacios" required></div>
                    </div>
                    <div class="field">
                        <label class="label">Materia</label>
                        <div class="control">
                            <div class="select is-fullwidth">
                                <select name="materia">
                                    <option>Informática I</option>
                                    <option>Informática II</option>
                                    <option>Informática III</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="field">
                        <label class="label">Fecha de Reserva</label>
                        <div class="control"><input class="input" type="date" name="fecha" required></div>
                    </div>
                    <button class="button is-link is-fullwidth">Registrar Inscripción</button>
                </form>

                {% if res %}
                <div class="notification {{ clase }} mt-5 has-text-centered">
                    {{ res }}
                </div>
                {% endif %}
            </div>
        </div>
    </section>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    res, clase = None, ""
    if request.method == 'POST':
        payload = {
            "nombre": request.form.get('nombre'),
            "dni": request.form.get('dni'),
            "materia": request.form.get('materia'),
            "fecha": request.form.get('fecha')
        }
        try:
            # Petición a la API de Google
            r = requests.post(URL_API, json=payload, timeout=12).json()
            status = r.get("status")
            res = r.get("message")
            
            if status == "success":
                clase = "is-success"
            elif status == "exists":
                clase = "is-warning"
            elif status == "full":
                clase = "is-danger"
            else:
                clase = "is-dark"
        except Exception:
            res, clase = "Error de conexión con la base de datos.", "is-danger"
            
    return render_template_string(HTML_LAYOUT, res=res, clase=clase)

application = app
