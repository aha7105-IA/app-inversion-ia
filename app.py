import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import google.generativeai as genai

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Departamento de Inversión IA", layout="wide", initial_sidebar_state="expanded")

# --- CONEXIÓN CON EL CEREBRO DE LA IA (GEMINI) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # AQUI ESTÁ EL CAMBIO: Usamos el modelo universal
    modelo = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"⚠️ Error al conectar la API: {e}")

# --- ESTILO VISUAL OSCURO ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (LOS AGENTES) ---
st.sidebar.title("🤖 Estado del Equipo")
agentes = {
    "El Sabueso": "Macro",
    "El Contable": "Micro",
    "El Psicólogo": "Sentimiento",
    "El Abogado del Diablo": "Riesgo"
}
for nombre, rol in agentes.items():
    st.sidebar.write(f"**{nombre}** ({rol}): 🟢 Operativo")

# --- CABECERA ---
st.title("🏛️ Terminal de Inversión IA - Chief Executive")
st.write(f"Fecha de conexión: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# --- PRECIOS EN TIEMPO REAL (CONVERTIDOS A EUROS) ---
st.header("📈 Monitor de Mercado (en Euros €)")

# Añadimos EURUSD=X para obtener el tipo de cambio en tiempo real y hacer la conversión
tickers = ['URA', 'ASML', 'BTC-USD', 'EURUSD=X']
data = yf.download(tickers, period="5d")['Close'].ffill().iloc[-1]

tipo_cambio = data['EURUSD=X']
precios_eur = {
    'URA': data['URA'] / tipo_cambio,
    'ASML': data['ASML'] / tipo_cambio,
    'Bitcoin': data['BTC-USD'] / tipo_cambio
}

cols = st.columns(len(precios_eur))
for i, (nombre, precio) in enumerate(precios_eur.items()):
    cols[i].metric(nombre, f"{precio:.2f} €")

st.divider()

# --- EL MOTOR DE INTELIGENCIA ARTIFICIAL ---
st.header("📋 Informe Diario de los Agentes")

if st.button("Generar Informe del Día"):
    with st.spinner("Los agentes están redactando el informe en tiempo real..."):
        prompt = """
        Actúa como un equipo de expertos financieros para un Chief Executive. Dame un informe rápido del mercado de hoy en 3 puntos. IMPORTANTE: Si hablas de dinero o precios, usa SIEMPRE Euros (€).
        1. 'El Sabueso' (Macro): Qué está pasando en la economía global hoy.
        2. 'El Contable' (Micro): Una empresa que deberíamos vigilar hoy y por qué.
        3. 'El Abogado del Diablo' (Riesgo): Un peligro inminente en el mercado actual.
        Sé directo, profesional y usa un tono ejecutivo.
        """
        try:
            respuesta = modelo.generate_content(prompt)
            st.write(respuesta.text)
        except Exception as e:
            st.error(f"Error exacto de Google: {e}")
else:
    st.info("👆 Haz clic en el botón de arriba para que la IA analice el mercado de hoy.")
