import os
from flask import Flask, render_template_string, request, Response
import requests
from fpdf import FPDF # Importamos la librería para PDF

app = Flask(__name__)
URL_API = os.getenv("APPS_SCRIPT_URL")

# --- LÓGICA PARA GENERAR EL PDF ---
def crear_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado Institucional
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "COMPROBANTE DE INSCRIPCION - UNTREF", ln=True, align="C")
    pdf.ln(10)
    
    # Contenido
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Estudiante: {datos.get('nombre')}", ln=True)
    pdf.cell(0, 10, f"DNI: {datos.get('dni')}", ln=True)
    pdf.cell(0, 10, f"Materia: {datos.get('materia')}", ln=True)
    pdf.cell(0, 10, f"Estado: {datos.get('estado')}", ln=True)
    pdf.ln(5)
    
    # Código Único (UUID)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(255, 0, 0)
    pdf.cell(0, 10, f"CODIGO DE RESERVA: {datos.get('uuid')}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Este documento sirve como comprobante oficial de reserva de vacante.", ln=True, align="C")
    
    return pdf.output()

# --- NUEVA RUTA PARA DESCARGAR EL PDF ---
@app.route('/descargar_pdf')
def descargar_pdf():
    # Recibimos los datos del alumno por parámetros de URL
    datos = {
        "nombre": request.args.get('nombre'),
        "dni": request.args.get('dni'),
        "materia": request.args.get('materia'),
        "estado": request.args.get('estado'),
        "uuid": request.args.get('uuid')
    }
    
    pdf_bytes = crear_pdf(datos)
    
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-disposition": f"attachment; filename=comprobante_{datos['dni']}.pdf"}
    )

# --- ACTUALIZACIÓN DE LA PÁGINA DE ESTADO (BOTÓN) ---
# Debes modificar el HTML de la función estado() para incluir este botón:
# (Poner dentro del bloque de 'if info')
'''
<div class="notification {{clase}} mt-4">
    {{info}}
    <hr>
    <a href="/descargar_pdf?nombre={{nombre}}&dni={{dni}}&materia={{materia}}&estado={{estado}}&uuid={{uuid}}" 
       class="button is-white is-fullwidth">
       Descargar Comprobante PDF
    </a>
</div>
'''
