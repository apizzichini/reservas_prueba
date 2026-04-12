from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# CONFIGURACIÓN: Pega aquí la URL de tu Apps Script
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz1PFmrsGGCCJ-XcbPFjGGYfgYbfichKPjv0SQNNuLNOg9OcyuxgS0NZ-f_bRz5iFNYKQ/exec"

# Plantilla HTML Profesional
HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Reserva de Laboratorios - UNTREF</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
</head>
<body>
    <section class="section">
        <div class="container">
            <h1 class="title">💻 Reserva de Laboratorio</h1>
            <p class="subtitle">Informática I, II y III</p>
            
            <form method="POST">
                <div class="field">
                    <label class="label">Nombre y Apellido</label>
                    <div class="control">
                        <input class="input" type="text" name="nombre" placeholder="Ej: Juan Pérez" required>
                    </div>
                </div>

                <div class="field">
                    <label class="label">Materia</label>
                    <div class="control">
                        <div class="select">
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
                    <div class="control">
                        <input class="input" type="date" name="fecha" required>
                    </div>
                </div>

                <div class="control">
                    <button class="button is-link">Confirmar Reserva</button>
                </div>
            </form>
            
            {% if mensaje %}
            <div class="notification is-success mt-5">
                {{ mensaje }}
            </div>
            {% endif %}
        </div>
    </section>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    mensaje = None
    if request.method == 'POST':
        # Capturar datos del formulario
        payload = {
            "nombre": request.form.get('nombre'),
            "materia": request.form.get('materia'),
            "fecha": request.form.get('fecha')
        }
        
        # Enviar a Google Sheets
        try:
            res = requests.post(APPS_SCRIPT_URL, json=payload)
            if res.status_code == 200:
                mensaje = "✅ ¡Reserva registrada con éxito en el Excel!"
            else:
                mensaje = "❌ Error al conectar con Google Sheets."
        except:
            mensaje = "❌ Error crítico de conexión."

    return render_template_string(HTML_FORM, mensaje=mensaje)

# Esto es vital para Vercel
app_obj = app
