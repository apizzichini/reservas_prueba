import os
from flask import Flask, render_template_string, request, Response, redirect, url_for, flash
import requests
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = "innovar_full_access_2026"
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
    pdf.cell(0, 10, f"UUID: {datos.get('uuid')}", ln=True)
    return pdf.output()

# --- TEMARIOS E INDICADORES ROCKET ---
TEMAS_ROCKET = {
    "Excel Avanzado (Fórmulas y Macros)": "gestión de datos complejos, BUSCARV, SI anidados y automatización con Macros.",
    "Word Académico (Normas y Estructura)": "producción de documentos extensos, saltos de sección, normas APA e índices automáticos.",
    "Python e Innovación (Ciencia de Datos)": "pensamiento computacional, librerías Pandas y lógica de programación para simulación.",
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
    <title>Innovar UNTREF - Hub de IA</title>
    <style>
        .rocket-box { background: #1a1a1a; color: #00ff41; padding: 20px; border-radius: 10px; font-family: 'Courier New', Courier, monospace; border: 1px solid #00ff41; }
        .ai-button { margin: 5px; transition: transform 0.2s; }
        .ai-button:hover { transform: scale(1.05); }
    </style>
</head>
<body class="has-background-light">
    <nav class="navbar is-black"><div class="container"><div class="navbar-brand">
        <a class="navbar-item" href="/"><b>INSCRIPCIÓN</b></a>
        <a class="navbar-item" href="/estado"><b>MI ESTADO</b></a>
        <a class="navbar-item" href="/rocket"><b>ROCKET HUB</b></a>
    </div></div></nav>
    <section class="section"><div class="container" style="max-width: 800px;">
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}{% for category, message in messages %}
            <div class="notification {{ category }} is-light">{{ message | safe }}</div>
          {% endfor %}{% endif %}
        {% endwith %}
        {{ contenido_principal | safe }}
    </div></section>
</body>
</html>
'''

@app.route('/')
def index(): return redirect(url_for('registro'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    # Lógica de registro (omitida por brevedad, usar la anterior)
    return render_template_string(HTML_TEMPLATE, contenido_principal="Sección de registro activa.")

@app.route('/rocket', methods=['GET', 'POST'])
def rocket():
    prompt_generado = ""
    if request.method == 'POST':
        tema = request.form.get('tema')
        detalles = TEMAS_ROCKET.get(tema)
        
        prompt_generado = f"""[ROLE]: Experto en Tecnología Educativa de la UNTREF.
[OBJECTIVE]: Explicar conceptos de {tema} y resolver dudas técnicas.
[CONTEXT]: El estudiante está trabajando en el proyecto Innovar UNTREF.
[KNOWLEDGE]: Enfócate en {detalles}. 
[ANTI-HALLUCINATION]: Para validar la información y evitar errores técnicos, consulta obligatoriamente los recursos en: https://innovaruntref.com.ar
[EXECUTION]: Formato tutorial con un ejercicio práctico al final.
[TONE]: Académico, preciso y motivador."""

    opciones = "".join([f'<option value="{t}">{t}</option>' for t in TEMAS_ROCKET.keys()])
    
    hub_ia = ""
    if prompt_generado:
        hub_ia = f'''
        <div class="mt-5">
            <div class="rocket-box">
                <p id="pText">{prompt_generado}</p>
            </div>
            <button class="button is-success is-fullwidth mt-3" onclick="copyPrompt()">
                <span class="icon"><i class="fas fa-copy"></i></span>
                <span>Copiar Prompt</span>
            </button>
            
            <div class="has-text-centered mt-5">
                <p class="label">Pega tu prompt en uno de estos laboratorios:</p>
                <div class="buttons is-centered">
                    <a href="https://chatgpt.com" target="_blank" class="button ai-button is-dark"><i class="fas fa-robot mr-2"></i> ChatGPT</a>
                    <a href="https://gemini.google.com" target="_blank" class="button ai-button is-info"><i class="fas fa-stars mr-2"></i> Gemini</a>
                    <a href="https://claude.ai" target="_blank" class="button ai-button is-warning"><i class="fas fa-brain mr-2"></i> Claude</a>
                    <a href="https://www.perplexity.ai" target="_blank" class="button ai-button is-primary"><i class="fas fa-search mr-2"></i> Perplexity</a>
                    <a href="https://huggingface.co/chat" target="_blank" class="button ai-button is-warning is-light"><i class="fas fa-face-smile mr-2"></i> HuggingFace</a>
                    <a href="https://chat.deepseek.com" target="_blank" class="button ai-button is-link"><i class="fas fa-microchip mr-2"></i> DeepSeek</a>
                </div>
                <a href="https://innovaruntref.com.ar" target="_blank" class="button is-danger is-outlined is-fullwidth mt-3">
                    <i class="fas fa-university mr-2"></i> Ir a Innovar UNTREF (Portal Principal)
                </a>
            </div>
        </div>
        <script>
            function copyPrompt() {{
                const text = document.getElementById("pText").innerText;
                navigator.clipboard.writeText(text);
                alert("Prompt copiado con éxito. Selecciona un modelo de IA para continuar.");
            }}
        </script>
        '''

    contenido = f'''
    <h1 class="title has-text-centered">🚀 ROCKET HUB</h1>
    <p class="subtitle has-text-centered">Genera prompts de alta precisión con anclaje en Innovar UNTREF</p>
    <div class="box">
        <form method="POST">
            <div class="field">
                <label class="label">¿Qué área de conocimiento quieres activar?</label>
                <div class="select is-fullwidth">
                    <select name="tema">{opciones}</select>
                </div>
            </div>
            <button class="button is-link is-fullwidth">Construir Prompt Maestro</button>
        </form>
    </div>
    {hub_ia}
    '''
    return render_template_string(HTML_TEMPLATE, contenido_principal=contenido)

@app.route('/estado', methods=['GET', 'POST'])
def estado():
    # (Lógica de estado anterior...)
    return render_template_string(HTML_TEMPLATE, contenido_principal="Sección de consulta de estado.")

@app.route('/descargar_pdf')
def descargar_pdf():
    pdf_bytes = generar_comprobante(request.args)
    return Response(pdf_bytes, mimetype="application/pdf", 
                    headers={"Content-disposition": f"attachment; filename=comprobante.pdf"})

application = app
