import os
from flask import Flask, render_template_string, request, Response, redirect, url_for, flash
import requests
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = "clave_secreta_untref" # Necesario para mostrar mensajes tras redirección
URL_API = os.getenv("APPS_SCRIPT_URL")

# --- LÓGICA DE PDF --- (Mantiene la misma estructura anterior)
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

# --- HTML MAESTRO ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
    <title>Inscripciones UNTREF</title>
</head>
<body>
    <nav class="navbar is-dark"><div class="container"><div class="navbar-brand">
        <a class="navbar-item" href="/"><b>REGISTRO</b></a>
        <a class="navbar-item" href="/estado"><b>MI ESTADO</b></a>
    </div></div></nav>
    <section class="section"><div class="container" style="max-width: 500px;">
        <div class="box">
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}
                {% for category, message in messages %}
                  <div class="notification {{ category }}">{{ message | safe }}</div>
                {% endfor %}
              {% endif %}
            {% endwith %}
            
            {{ contenido_principal | safe }}
        </div>
    </div></section>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def registro():
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
                flash("✅ Inscripción realizada con éxito.", "is-success")
            elif r['status'] == 'exists':
                flash(f"⚠️ Ya estás inscripto en {r['data']['materia']}.", "is-warning")
            else:
                flash(f"🚫 {r['data']}", "is-danger")
        except:
            flash("❌ Error de conexión con la base de datos.", "is-danger")
        
        # EL TRUCO: Redirigimos al usuario a la misma página (GET)
        # Esto limpia los datos del formulario de la memoria del navegador
        return redirect(url_for('registro'))
    
    form_html = '''
    <h1 class="title is-4">Inscripción</h1>
    <form method="POST">
        <label class="label">Nombre Completo</label><input class="input mb-2" name="nombre" required>
        <label class="label">DNI</label><input class="input mb-2" name="dni" type="number" required>
        <label class="label">Materia</label>
        <div class="select is-fullwidth mb-2"><select name="materia">
            <option>Informática I</option><option>Informática II</option><option>Informática III</option>
        </select></div>
        <label class="label">Fecha</label><input class="input mb-4" name="fecha" type="date" required>
        <button class="button is-link is-fullwidth">Inscribirse</button>
    </form>
    '''
    return render_template_string(HTML_TEMPLATE, contenido_principal=form_html)

@app.route('/estado', methods=['GET', 'POST'])
def estado():
    contenido_html = '<h1 class="title is-4">Consultar Estado</h1>'
    datos_consulta = None
    
    if request.method == 'POST':
        payload = {"accion": "consultar", "dni": request.form.get('dni')}
        try:
            r = requests.post(URL_API, json=payload).json()
            if r['status'] == 'exists':
                d = r['data']
                msg = f"Hola {d['nombre']}, estás inscripto en {d['materia']}.<hr>"
                msg += f'<a href="/descargar_pdf?nombre={d["nombre"]}&dni={d["dni"]}&materia={d["materia"]}&estado={d["estado"]}&uuid={d["uuid"]}" class="button is-dark is-fullwidth">Descargar Comprobante PDF</a>'
                flash(msg, "is-info")
            else:
                flash("No se encontró registro para este DNI.", "is-danger")
        except:
            flash("Error de conexión.", "is-danger")
        
        return redirect(url_for('estado'))

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
