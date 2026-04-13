import os
from flask import Flask, render_template_string, request, Response, redirect, url_for, flash
import requests
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = "innovar_untref_final_fix_v3"
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

# --- TEMPLATE CORREGIDO (Incluye el marcador de contenido) ---
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
        .footer-logos { 
            border-top: 1px solid #eee; 
            padding: 40px 0; 
            background: #ffffff; 
            margin-top: 50px; 
        }
        .footer-logos img { 
            height: 60px; 
            max-width: 200px;
            filter: grayscale(100%); 
            transition: 0.3s; 
            margin: 10px 25px; 
            display: inline-block;
            vertical-align: middle;
        }
        .footer-logos img:hover { filter: grayscale(0%); }
        .box { border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        .rocket-box { background: #1a1a1a; color: #00ff41; padding: 20px; border-radius: 8px; font-family: monospace; min-height: 100px; }
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
              {% if messages %}{% for c, m in messages %}
                <div class="notification {{c}} is-light">{{m|safe}}</div>
              {% endfor %}{% endif %}
            {% endwith %}
            
            {{ contenido_principal | safe }}
        </div>
    </section>

    <footer class="footer-logos has-text-centered">
        <div class="container">
            <div class="columns is-centered is-vcentered is-mobile is-multiline">
                <div class="column is-narrow">
                    <img src="{{ url_for('static', filename='Python.jpg') }}" alt="Python UNTREF">
                </div>
                <div class="column is-narrow">
                    <img src="{{ url_for('static', filename='Equipo De Investigación Tecnología Educativa.jpg') }}" alt="Investigación">
                </div>
                <div class="column is-narrow">
                    <img src="{{ url_for('static', filename='INNOVAR LOGO WEB (1).jpg') }}" alt="Innovar Logo">
                </div>
            </div>
            <p class="is-size-7 has-text-grey mt-4">Universidad Nacional de Tres de Febrero</p>
        </div>
    </footer>
    
    <script>
        function typeWriter(id, text, speed) {
            const el = document.getElementById(id);
            if (!el) return;
            el.innerHTML = "";
            let i = 0;
            function type() { if (i < text.length) { el.innerHTML += text.charAt(i); i++; setTimeout(type, speed); } }
            type();
        }
        window.onload = () => {
            const pData = document.getElementById('raw-prompt');
            if (pData) typeWriter('type-target', pData.value, 15);
        };
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        payload = {
            "accion": "registrar", "nombre": request.form.get('nombre'),
            "dni": request.form.get('dni'), "materia": request.form.get('materia'),
            "fecha": request.form.get('fecha')
        }
        try:
            requests.post(URL_API, json=payload, timeout=10)
            flash("✅ <b>Registro enviado.</b> Verifique su estado en unos minutos.", "is-success")
        except:
            flash("❌ Error de comunicación.", "is-danger")
        return redirect(url_for('registro'))
    
    contenido = '''<h1 class="title">Inscripción</h1><div class="box"><form method="POST">
        <div class="field"><label class="label">Nombre</label><input class="input" name="nombre" required></div>
        <div class="field"><label class="label">DNI</label><input class="input" name="dni" type="number" required></div>
        <div class="field"><label class="label">Materia</label><div class="select is-fullwidth"><select name="materia"><option>Informática II</option><option>Informática III</option></select></div></div>
        <div class="field"><label class="label">Fecha</label><input class="input" name="fecha" type="date" required></div>
        <button class="button is-link is-fullwidth">Enviar</button></form></div>'''
    return render_template_string(HTML_TEMPLATE, contenido_principal=contenido)

@app.route('/estado', methods=['GET', 'POST'])
def estado():
    res_html = ""
    if request.method == 'POST':
        dni_query = request.form.get('dni')
        try:
            r = requests.post(URL_API, json={"accion": "consultar", "dni": dni_query}, timeout=15).json()
            if r.get('status') == 'exists':
                d = r['data']
                res_html = f'''<div class="notification is-info is-light">
                    <p><b>Estudiante:</b> {d.get('nombre')}</p>
                    <p><b>Materia:</b> {d.get('materia')}</p><br>
                    <a href="/descargar_pdf?nombre={d.get('nombre')}&dni={d.get('dni')}&materia={d.get('materia')}&uuid={d.get('uuid')}" 
                    class="button is-dark is-fullwidth">DESCARGAR PDF</a></div>'''
            else:
                flash(f"⚠️ El DNI {dni_query} no está en la base de datos.", "is-warning")
        except:
            flash("❌ Error conectando con el servidor de datos.", "is-danger")
        
        if not res_html:
            return redirect(url_for('estado'))

    contenido = f'''<h1 class="title">Mi Estado</h1><div class="box">
        <form method="POST">
            <div class="field has-addons">
                <div class="control is-expanded"><input class="input" name="dni" placeholder="Ingresa tu DNI" required></div>
                <div class="control"><button class="button is-primary">Buscar</button></div>
            </div>
        </form>
        <div class="mt-4">{res_html}</div></div>'''
    return render_template_string(HTML_TEMPLATE, contenido_principal=contenido)

@app.route('/rocket', methods=['GET', 'POST'])
def rocket():
    output = ""
    if request.method == 'POST':
        tema = request.form.get('tema')
        detalles = TEMAS_ROCKET.get(tema)
        p = f"[ROLE]: Tutor Innovar UNTREF experto en {tema}.\\n[OBJECTIVE]: Explicar conceptos.\\n[KNOWLEDGE]: {detalles}."
        output = f'''<div class="mt-4"><input type="hidden" id="raw-prompt" value="{p}">
            <div class="rocket-box" id="type-target"></div>
            <button class="button is-success is-fullwidth mt-3" onclick="navigator.clipboard.writeText(document.getElementById('raw-prompt').value.replace(/\\\\n/g, '\\n')); alert('Copiado');">Copiar Prompt</button></div>'''
    
    opc = "".join([f'<option value="{t}">{t}</option>' for t in TEMAS_ROCKET.keys()])
    contenido = f'''<h1 class="title">Rocket Hub</h1><div class="box"><form method="POST">
        <div class="select is-fullwidth"><select name="tema">{opc}</select></div>
        <button class="button is-link mt-2 is-fullwidth">Generar Prompt</button></form>{output}</div>'''
    return render_template_string(HTML_TEMPLATE, contenido_principal=contenido)

@app.route('/descargar_pdf')
def descargar_pdf():
    pdf_bytes = generar_comprobante(request.args)
    return Response(pdf_bytes, mimetype="application/pdf", headers={"Content-disposition": "attachment; filename=comprobante.pdf"})

application = app
