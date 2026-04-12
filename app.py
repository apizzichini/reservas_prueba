import os
from flask import Flask, render_template_string, request, Response
import requests
from fpdf import FPDF

app = Flask(__name__)
URL_API = os.getenv("APPS_SCRIPT_URL")

# --- LÓGICA DE PDF ---
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
    pdf.set_text_color(220, 53, 69)
    pdf.cell(0, 10, f"CODIGO: {datos.get('uuid')}", ln=True)
    return pdf.output()

# --- HTML MAESTRO (Sin bloques conflictivos) ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
    <title>Inscripciones UNTREF</title>
</head>
<body>
    <nav class="navbar is-dark">
        <div class="container">
            <div class="navbar-brand">
                <a class="navbar-item" href="/"><b>REGISTRO</b></a>
                <a class="navbar-item" href="/estado"><b>MI ESTADO</b></a>
            </div>
        </div>
    </nav>
    <section class="section">
        <div class="container" style="max-width: 500px;">
            <div class="box">
                {{ contenido_principal | safe }}
            </div>
        </div>
    </section>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def registro():
    mensaje_html = ""
    if request.method == 'POST':
        payload = {
            "accion": "registrar",
            "nombre": request.form.get('nombre'),
            "dni": request.form.get('dni'),
            "materia": request.form.get('materia'),
            "fecha": request.form.get('fecha')
        }
        try:
            r = requests.post(URL_API, json=payload, timeout=15).json()
            if r['status'] == 'success':
                mensaje_html = '<div class="notification is-success mt-4">✅ Inscripción realizada con éxito.</div>'
            elif r['status'] == 'exists':
                mensaje_html = f'<div class="notification is-warning mt-4">⚠️ Ya estás inscripto en {r["data"]["materia"]}.</div>'
            else:
                mensaje_html = f'<div class="notification is-danger mt-4">🚫 {r["data"]}</div>'
        except:
            mensaje_html = '<div class="notification is-danger mt-4">❌ Error de conexión con la base de datos.</div>'
    
    form_html = f'''
    <h1 class="title is-4">Inscripción</h1>
    <form method="POST">
        <label class="label">Nombre Completo</label>
        <input class="input mb-2" name="nombre" required>
        <label class="label">DNI</label>
        <input class="input mb-2" name="dni" type="number" required>
        <label class="label">Materia</label>
        <div class="select is-fullwidth mb-2">
            <select name="materia">
                <option>Informática I</option>
                <option>Informática II</option>
                <option>Informática III</option>
            </select>
        </div>
        <label class="label">Fecha</label>
        <input class="input mb-4" name="fecha" type="date" required>
        <button class="button is-link is-fullwidth">Inscribirse</button>
    </form>
    {mensaje_html}
    '''
    return render_template_string(HTML_TEMPLATE, contenido_principal=form_html)

@app.route('/estado', methods=['GET', 'POST'])
def estado():
    contenido_html = '<h1 class="title is-4">Consultar Estado</h1>'
    if request.method == 'POST':
        payload = {"accion": "consultar", "dni": request.form.get('dni')}
        try:
            r = requests.post(URL_API, json=payload).json()
            if r['status'] == 'exists':
                d = r['data']
                contenido_html += f'''
                <div class="notification is-info mt-4">
                    Hola {d['nombre']}, estás inscripto en {d['materia']}.
                    <hr>
                    <a href="/descargar_pdf?nombre={d['nombre']}&dni={d['dni']}&materia={d['materia']}&estado={d['estado']}&uuid={d['uuid']}" 
                    class="button is-dark is-fullwidth">Descargar Comprobante PDF</a>
                </div>'''
            else:
                contenido_html += '<div class="notification is-danger mt-4">No se encontró registro para este DNI.</div>'
        except:
            contenido_html += '<div class="notification is-danger mt-4">Error de conexión.</div>'
    
    contenido_html += '''
    <form method="POST">
        <label class="label">DNI</label>
        <input class="input mb-4" name="dni" placeholder="Ingresa tu DNI" required>
        <button class="button is-primary is-fullwidth">Buscar</button>
    </form>'''
    
    return render_template_string(HTML_TEMPLATE, contenido_principal=contenido_html)

@app.route('/descargar_pdf')
def descargar_pdf():
    pdf_bytes = generar_comprobante(request.args)
    return Response(pdf_bytes, mimetype="application/pdf", 
                    headers={"Content-disposition": f"attachment; filename=comprobante_{request.args.get('dni')}.pdf"})

application = app
