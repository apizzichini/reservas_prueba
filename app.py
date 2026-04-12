import os
from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)
URL_API = os.getenv("APPS_SCRIPT_URL")

# --- PLANTILLAS HTML ---
BASE_HTML = '''
<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
<title>Sistema UNTREF</title></head><body>
<nav class="navbar is-dark"><div class="navbar-brand"><a class="navbar-item" href="/">Inscribirse</a><a class="navbar-item" href="/estado">Mi Estado</a></div></nav>
<section class="section"><div class="container" style="max-width: 500px;">{% block content %}{% endblock %}</div></section>
</body></html>
'''

@app.route('/', methods=['GET', 'POST'])
def registro():
    msg, clase = None, ""
    if request.method == 'POST':
        payload = {"accion": "registrar", "nombre": request.form.get('nombre'), "dni": request.form.get('dni'), 
                   "materia": request.form.get('materia'), "fecha": request.form.get('fecha')}
        r = requests.post(URL_API, json=payload).json()
        if r['status'] == 'success':
            msg, clase = "✅ Inscripción realizada.", "is-success"
        elif r['status'] == 'exists':
            msg, clase = f"⚠️ Ya estás inscripto en {r['data']['materia']}. Estado: {r['data']['estado']}", "is-warning"
        else:
            msg, clase = "❌ " + r['data'], "is-danger"
    
    return render_template_string(BASE_HTML + '{% block content %}<div class="box"><h1 class="title">Registro</h1>'
        '<form method="POST"><input class="input mb-2" name="nombre" placeholder="Nombre" required>'
        '<input class="input mb-2" name="dni" type="number" placeholder="DNI" required>'
        '<div class="select is-fullwidth mb-2"><select name="materia"><option>Informática I</option><option>Informática II</option><option>Informática III</option></select></div>'
        '<input class="input mb-4" name="fecha" type="date" required><button class="button is-link is-fullwidth">Enviar</button></form>'
        '{% if msg %}<div class="notification {{clase}} mt-4">{{msg}}</div>{% endif %}</div>{% endblock %}', msg=msg, clase=clase)

@app.route('/estado', methods=['GET', 'POST'])
def estado():
    info, clase = None, ""
    if request.method == 'POST':
        payload = {"accion": "consultar", "dni": request.form.get('dni')}
        r = requests.post(URL_API, json=payload).json()
        if r['status'] == 'exists':
            info = f"Hola {r['data']['nombre']}, tu inscripción en {r['data']['materia']} está {r['data']['estado']}."
            clase = "is-info"
        else:
            info = "No se encontró ningún registro con ese DNI."
            clase = "is-danger"
            
    return render_template_string(BASE_HTML + '{% block content %}<div class="box"><h1 class="title">Consultar Estado</h1>'
        '<form method="POST"><input class="input mb-4" name="dni" placeholder="Ingresa tu DNI" required>'
        '<button class="button is-primary is-fullwidth">Consultar</button></form>'
        '{% if info %}<div class="notification {{clase}} mt-4">{{info}}</div>{% endif %}</div>{% endblock %}', info=info, clase=clase)

application = app
