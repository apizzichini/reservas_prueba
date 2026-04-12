import streamlit as st
import requests

# Reemplaza con la URL que me pasaste
URL_API = "https://script.google.com/macros/s/AKfycbz1PFmrsGGCCJ-XcbPFjGGYfgYbfichKPjv0SQNNuLNOg9OcyuxgS0NZ-f_bRz5iFNYKQ/exec"

st.set_page_config(page_title="Sistema de Reservas UNTREF", layout="centered")

st.title("📋 Reserva de Laboratorios de Informática")
st.info("Materias: Informática I, II y III")

with st.form("registro_reserva"):
    nombre = st.text_input("Nombre completo del Estudiante")
    materia = st.selectbox("Materia", ["Informática I", "Informática II", "Informática III"])
    fecha_reserva = st.date_input("Fecha programada para el laboratorio")
    comentarios = st.text_area("Notas adicionales (opcional)")
    
    enviar = st.form_submit_button("Confirmar Reserva")

    if enviar:
        if not nombre:
            st.error("El nombre es obligatorio.")
        else:
            # Estructura de datos profesional (JSON)
            payload = {
                "nombre": nombre,
                "materia": materia,
                "fecha": str(fecha_reserva),
                "comentarios": comentarios
            }
            
            try:
                with st.spinner("Enviando datos al servidor de Google..."):
                    # Enviamos el POST a la URL de tu Apps Script
                    response = requests.post(URL_API, json=payload, timeout=10)
                    
                if response.status_code == 200:
                    st.success(f"✅ ¡Reserva exitosa para {nombre}!")
                    st.balloons()
                else:
                    st.error(f"Error del servidor: {response.status_code}")
            except Exception as e:
                st.error(f"No se pudo conectar con el sistema: {e}")
app = None
