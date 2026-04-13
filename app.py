import os
from flask import Flask, render_template_string, request, Response, redirect, url_for, flash
import requests
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = "untref_innovar_full_2026"
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
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(220, 53, 69)
    pdf.cell(0, 10, f"CODIGO UNICO: {datos.get('uuid')}", ln=True)
    return pdf.output()

# --- TEMARIOS ROCKET ---
TEMAS_ROCKET = {
    "Excel Avanzado (Fórmulas y Macros)": "gestión de datos complejos, BUSCARV, SI anidados y automatización con Macros.",
    "Word Académico (Normas y Estructura)": "producción de documentos extensos, saltos de sección, normas APA e índices automáticos.",
    "Python e Innovación (Ciencia de Datos)": "pensamiento computacional, librerías Pandas y lógica de programación.",
    "IA y Vibe Coding (Prompt Engineering)": "integración de modelos generativos y desarrollo asistido por IA."
}

# --- HTML MAESTRO ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <title>Innovar UNTREF</title>
    <style>
        .rocket-box { background: #1a1a1a; color: #00ff41; padding: 20px; border-radius: 10px; font-family: monospace; border: 1px solid #00ff41; }
        .ai-button { margin: 5px; }
        .box { border-radius: 12px; }
    </style>
</head>
<body class="has-background-light">
    <nav class="navbar is-black">
        <div class="container">
            <div class="navbar-brand">
                <a class="navbar-item" href="/"><b>INSCRIPCIÓN</b></a>
                <a class="navbar-item" href="/estado"><b>MI ESTADO</b></a>
                <a class="navbar-item" href="/rocket"><b>ROCKET HUB</b></a>
            </div>
        </div>
    </nav>
    <section class="section">
        <div class="container" style="max-width: 700px;">
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}{% for category, message in messages %}
                <div class="notification {{ category }} is-light">{{ message | safe }}</div>
              {% endfor %}{% endif %}
            {% endwith %}
            {{ contenido_principal | safe }}
        </div>
    </section>

    <script>
        function typeWriter(elementId, speed) {
            const element = document.getElementById(elementId);
            if (!element) return;
            const text = element.innerHTML;
            element.innerHTML = "";
            element.style.display = "block";
            let i = 0;
            function type() {
                if (i < text.length) {
                    if (text.charAt(i) === "<") {
                        let endTag = text.indexOf(">", i);
                        element.innerHTML += text.substring(i, endTag + 1);
                        i = endTag + 1;
                    } else {
                        element.innerHTML += text.charAt(i);
                        i++;
                    }
                    setTimeout(type, speed);
                }
            }
            type();
        }
        window.onload = () => { if(document.getElementById('ai-text')) typeWriter('ai-text', 10); };
    </script>
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
                flash("✅ <b>Registro Exitoso</b>", "is-success")
            else:
                flash(f"🚫 {r.get('data', 'Error')}", "is-danger")
        except:
            flash("❌ Error de conexión", "is-danger")
        return redirect(url_for('registro'))
    
    form_html = '''
    <h1 class="title">Inscripción Académica</h1>
    <div class="box">
        <form method="POST">
            <div class="field"><label class="label">Nombre</label><input class="input" name="nombre" required></div>
            <div class="field"><label class="label">DNI</label><input class="input" name="dni" type="number" required></div>
            <div class="field"><label class="label">Materia</label>
                <div class="select is-fullwidth"><select name="materia">
                    <option>Informática I</option><option selected>Informática II</option><option>Informática III</option>
                </select></div>
            </div>
            <div class="field"><label class="label">Fecha</label><input class="input" name="fecha" type="date" required></div>
            <button class="button is-link is-fullwidth">Inscribirse</button>
        </form>
    </div>'''
    return render_template_string(HTML_TEMPLATE, contenido_principal=form_html)

@app.route('/estado', methods=['GET', 'POST'])
def estado():
    if request.method == 'POST':
        payload = {"accion": "consultar", "dni": request.form.get('dni')}
        try:
            r = requests.post(URL_API, json=payload).json()
            if r['status'] == 'exists':
                d = r['data']
                prog = ""
                if "II" in d['materia']:
                    prog = '<div class="mt-3 is-size-7"><b>Programa:</b> Excel Avanzado, Word Académico y Python.</div>'
                
                msg = f'''
                <div id="ai-text" style="display:none;">
                    Verificado Estudiante <b>{d['nombre']}</b> para <b>{d['materia']}</b>.<br><br>
                    <a href="/descargar_pdf?nombre={d['nombre']}&dni={d['dni']}&materia={d['materia']}&uuid={d['uuid']}" 
                       class="button is-black is-fullwidth">Descargar PDF</a>
                    {prog}
                </div>'''
                flash(msg, "is-info")
            else:
                flash("No se encontró el DNI.", "is-danger")
        except:
            flash("Error de conexión.", "is-danger")
        return redirect(url_for('estado'))

    form_html = '''
    <h1 class="title">Consulta de Estado</h1>
    <div class="box">
        <form method="POST">
            <label class="label">DNI</label>
            <div class="field has-addons">
                <div class="control is-expanded"><input class="input" name="dni" required></div>
                <div class="control"><button class="button is-primary">Buscar</button></div>
            </div>
        </form>
    </div>'''
    return render_template_string(HTML_TEMPLATE, contenido_principal=form_html)

@app.route('/rocket', methods=['GET', 'POST'])
def rocket():
    hub_ia = ""
    if request.method == 'POST':
        tema = request.form.get('tema')
        detalles = TEMAS_ROCKET.get(tema)
        prompt = f"[ROLE]: Tutor Innovar UNTREF. [OBJECTIVE]: Tutorial sobre {tema}. [ANTI-HALLUCINATION]: Usa https://innovaruntref.com.ar"
        
        hub_ia = f'''
        <div class="mt-5">
            <div class="rocket-box"><p id="pText">{prompt}</p></div>
            <button class="button is-success is-fullwidth mt-3" onclick="navigator.clipboard.writeText(document.getElementById('pText').innerText); alert('Copiado');">Copiar Prompt</button>
            <div class="buttons is-centered mt-4">
                <a href="https://chatgpt.com" target="_blank" class="button is-dark">ChatGPT</a>
                <a href="https://gemini.google.com" target="_blank" class="button is-info">Gemini</a>
                <a href="https://innovaruntref.com.ar" target="_blank" class="button is-danger is-outlined">Portal Innovar</a>
            </div>
        </div>'''

    opciones = "".join([f'<option value="{t}">{t}</option>' for t in TEMAS_ROCKET.keys()])
    contenido = f'''<h1 class="title">ROCKET HUB</h1><div class="box"><form method="POST"><div class="field"><label class="label">Tema</label><div class="select is-fullwidth"><select name="tema">{opciones}</select></div></div><button class="button is-link is-fullwidth">Generar</button></form></div>{hub_ia}'''
    return render_template_string(HTML_TEMPLATE, contenido_principal=contenido)

@app.route('/descargar_pdf')
def descargar_pdf():
    pdf_bytes = generar_comprobante(request.args)
    return Response(pdf_bytes, mimetype="application/pdf", headers={"Content-disposition": "attachment; filename=comprobante.pdf"})

application = app
