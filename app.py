import os
import requests
from flask import Flask, render_template_string, request, Response, redirect, url_for, flash
from fpdf import FPDF

# Vercel busca este objeto llamado 'app'
app = Flask(__name__)
app.secret_key = "innovar_untref_2026_final_v7"
URL_API = os.getenv("APPS_SCRIPT_URL")

# --- LÓGICA DE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'COMPROBANTE ACADEMICO - UNTREF', 0, 1, 'C')
        self.ln(10)

def generar_comprobante(datos):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Estudiante: {datos.get('nombre', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"DNI: {datos.get('dni', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"Materia: {datos.get('materia', 'N/A')}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(29, 67, 138)
    pdf.cell(0, 10, f"UUID DE VALIDACION: {datos.get('uuid', 'N/A')}", ln=True)
    return pdf.output()

TEMAS_ROCKET = {
    "Excel Avanzado": "Fórmulas complejas, Macros y automatización.",
    "Python e IA": "Lógica de programación y modelos generativos.",
    "Word Académico": "Normas APA y gestión de documentos extensos."
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <title>Innovar UNTREF</title>
    <style>
        :root { --untref-blue: #1d438a; }
        .navbar { background-color: var(--untref-blue) !important; }
        .footer-logos { border-top: 1px solid #eee; padding: 40px 0; background: #ffffff; margin-top: 50px; }
        .footer-logos img { height: 60px; max-width: 200px; filter: grayscale(100%); transition: 0.3s; margin: 10px 25px; display: inline-block; vertical-align: middle; }
        .footer-logos img:hover { filter: grayscale(0%); }
        .box { border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    </style>
</head>
<body class="has-background-light">
    <nav class="navbar is-info">
        <div class="container">
            <div class="navbar-brand">
                <a class="navbar-item" href="/"><b>REGISTRO</b></a>
                <a class="navbar-item" href="/estado"><b>MI ESTADO</b></a>
                <a class="navbar-item" href="/rocket"><b>ROCKET HUB</b></a>
            </div>
        </div>
    </nav>
    <section class="section">
        <div class="container" style="max-width: 700px;">
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}{% for c, m in messages %}<div class="notification {{c}} is-light">{{m|safe}}</div>{% endfor %}{% endif %}
            {% endwith %}
            {{ contenido_principal | safe }}
        </div>
    </section>
    <footer class="footer-logos has-text-centered">
        <div class="container">
            <div class="columns is-centered is-vcentered is-mobile is-multiline">
                <div class="column is-narrow"><img src="{{ url_for('static', filename='python-untref.jpg') }}" alt="Python"></div>
                <div class="column is-narrow"><img src="{{ url_for('static', filename='equipo-investigacion.jpg') }}" alt="Equipo"></div>
                <div class="column is-narrow"><img src="{{ url_for('static', filename='innovar-logo.jpg') }}" alt="Innovar"></div>
            </div>
        </div>
    </footer>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        payload = {"accion": "registrar", "nombre": request.form.get('nombre'), "dni": request.form.get('dni'), "materia": request.form.get('materia'), "fecha": request.form.get('fecha')}
        try:
            requests.post(URL_API, json=payload, timeout=10)
            flash("✅ Registro enviado correctamente.", "is-success")
        except:
            flash("❌ Error al registrar.", "is-danger")
        return redirect(url_for('registro'))
    
    contenido = '''<h1 class="title">Inscripción</h1><div class="box"><form method="POST">
        <div class="field"><label class="label">Nombre</label><input class="input" name="nombre" required></div>
        <div class="field"><label class="label">DNI</label><input class="input" name="dni" type="number" required></div>
        <div class="field"><label class="label">Materia</label
