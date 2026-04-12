import os
from flask import Flask, render_template_string, request, Response
import requests
from fpdf import FPDF

app = Flask(__name__)
URL_API = os.getenv("APPS_SCRIPT_URL")

# --- LÓGICA DE GENERACIÓN DE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'COMPROBANTE DE RESERVA - UNTREF', 0, 1, 'C')
        self.ln(10)

def generar_comprobante(datos):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)
    
    pdf.cell(0, 10, f"Estudiante: {datos.get('nombre')}", ln=True)
    pdf.cell(0, 10, f"DNI: {datos.get('dni')}", ln=True)
    pdf.cell(0, 10, f"Materia: {datos.get('materia')}", ln=True)
    pdf.cell(0, 10, f"Estado: {datos.get('estado')}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(220, 53, 69) # Rojo para el código
    pdf.cell(0, 10, f"CÓDIGO ÚNICO DE RESERVA: {datos.get('uuid')}", ln=True)
    
    return pdf.output()

# --- PLANTILLA HTML BASE ---
BASE_HTML = '''
<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
<title>Inscripciones Informática</title></head><body>
<nav class="navbar is-dark"><div class="container"><div class="navbar-brand">
<a class="navbar-item" href="/"><b>REGISTRO</b></a><a class="navbar-item" href="/estado"><b>MI ESTADO</b></a>
</div></div></nav>
<section class="section"><div class="container" style="max-width: 500px;">{% block content %}{% endblock %}</div></section>
</body></html>
'''

@app.route('/', methods=['GET', 'POST'])
def registro():
    res, clase = None, ""
    if request.method == 'POST':
        payload = {"accion": "registrar", "nombre": request.form.get('nombre'), "dni": request.form.get('dni'), 
                   "materia": request.form.get('materia'), "fecha": request.form.get('fecha')}
        try:
            r = requests.post(URL_API, json=payload, timeout=15).json()
            if r['status'] == 'success':
                res, clase = "✅ Inscripción realizada con éxito.", "is-success"
            elif r['status'] == 'exists':
                res, clase = f"⚠️ Ya estás inscripto en {r['data']['materia']}.", "is-warning"
            else:
                res, clase = f"🚫 {r['data']}", "is-danger"
        except:
            res, clase = "❌ Error de conexión.", "is-danger"
    
    return render_template_string(BASE_HTML + '{% block content %}<div class="box"><h1 class="title is-4">Inscripción</h1>'
        '<form method="POST"><label class="label">Nombre</label><input class="input mb-2" name="nombre" required>'
        '<label class="label">DNI</label><input class="input mb-2" name="dni" type="number" required>'
        '<label class="label">Materia</label><div class="select is-fullwidth mb-2"><select name="materia">'
        '<option>Informática I</option><option>Informática II</option><option>Informática III</option></select></div>'
        '<label class="label">Fecha</label><input class="input mb-4" name="fecha" type="date" required>'
        '<button class="button is-link is-fullwidth">Inscribirse</button></form>'
        '{% if res %}<div class="notification {{clase}} mt-4">{{res}}</div>{% endif %}</div>{% endblock %}', res=res, clase=clase)

@app.route('/estado', methods=['GET', 'POST'])
def estado():
    info, datos = None, None
    if request.method == 'POST':
        payload = {"accion": "consultar", "dni": request.form.get('dni')}
        try:
            r = requests.post(URL_API, json=payload).json()
            if r['status'] == 'exists':
                datos = r['data']
                info = f"Hola {datos['nombre']}, estás inscripto en {datos['materia']}."
            else:
                info = "No se encontró registro para este DNI."
        except:
            info = "Error de conexión."
            
    return render_template_string(BASE_HTML + '{% block content %}<div class="box"><h1 class="title is-4">Consultar Estado</h1>'
        '<form method="POST"><label class="label">DNI</label><input class="input mb-4" name="dni" placeholder="Ingresa tu DNI" required>'
        '<button class="button is-primary is-fullwidth">Buscar</button></form>'
        '{% if info %}<div class="notification is-light mt-4">{{info}}'
        '{% if datos %}<hr><a href="/descargar_pdf?nombre={{datos.nombre}}&dni={{datos.dni}}&materia={{datos.materia}}&estado={{datos.estado}}&uuid={{datos.uuid}}" '
        'class="button is-dark is-fullwidth">Descargar Comprobante PDF</a>{% endif %}</div>{% endif %}</div>{% endblock %}', info=info, datos=datos)

@app.route('/descargar_pdf')
def descargar_pdf():
    pdf_bytes = generar_comprobante(request.args)
    return Response(pdf_bytes, mimetype="application/pdf", 
                    headers={"Content-disposition": f"attachment; filename=comprobante_{request.args.get('dni')}.pdf"})

application = app
