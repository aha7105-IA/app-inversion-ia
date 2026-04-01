import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Departamento de Inversión IA", layout="wide", initial_sidebar_state="expanded")

# ESTILO DARK MODE PROFESIONAL
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: ESTADO DE LOS 9 AGENTES ---
st.sidebar.title("🤖 Estado del Equipo")
agentes = {
    "El Sabueso": "🔍 Escaneando Macro",
    "El Contable": "📊 Analizando Balances",
    "El Psicólogo": "🧠 Midiendo Sentimiento",
    "El Abogado del Diablo": "🚩 Vigilando Riesgos",
    "El Estratega": "🎯 Coordinando CIO",
    "El Arquitecto Visual": "🎨 Optimizando UI",
    "Carla": "💡 Innovando I+D",
    "El Oráculo": "📡 Señales Invisibles",
    "El Sombra": "🕵️ Vigilando Insiders"
}
for nombre, estado in agentes.items():
    st.sidebar.write(f"**{nombre}:** {estado}")

# --- TÍTULO PRINCIPAL ---
st.title("🏛️ Terminal de Inversión IA - Chief Executive")
st.write(f"Fecha actual: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# --- BLOQUE 1: CARTERA VIRTUAL ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Balance Total", "100.000,00 €", "+0.42%")
with col2:
    st.metric("Inversión en Uranio (URA)", "15.000,00 €", "En espera")
with col3:
    st.metric("Efectivo Disponible", "85.000,00 €")
with col4:
    st.metric("Nivel de Riesgo", "Medio-Bajo", "Estable")

# --- BLOQUE 2: DATOS DE MERCADO EN TIEMPO REAL ---
st.header("📈 Monitor de Activos Bajo Vigilancia")
tickers = ['URA', 'ASML', 'PANW', 'BTC-USD', 'GC=F'] # Uranio, Chips, Ciberseguridad, Bitcoin, Oro
data = yf.download(tickers, period="1d")['Close'].iloc[-1]

cols_m = st.columns(len(tickers))
for i, ticker in enumerate(tickers):
    cols_m[i].metric(ticker, f"{data[ticker]:.2f}")

# --- BLOQUE 3: EL INFORME MAESTRO DE LOS AGENTES ---
st.divider()
st.header("📋 Informe de los Agentes (08:00 AM)")

tab1, tab2, tab3 = st.tabs(["🎯 Selección del Día", "🕵️ Power Feed (Insiders)", "🚩 Riesgos"])

with tab1:
    st.subheader("Uranio (ETF: URA)")
    st.write("**Tesis:** Movimiento coordinado de legisladores en EE.UU. y déficit de suministro global.")
    st.info("Recomendación: Mantener posición de 15.000€. Precio objetivo: +12%")

with tab2:
    st.subheader("Actividad de Insiders detectada por 'El Sombra'")
    st.warning("Detección de compras en el sector de Ciberseguridad por parte de directivos de Palo Alto Networks.")

with tab3:
    st.subheader("Análisis del Abogado del Diablo")
    st.error("Alerta: Volatilidad esperada en el mercado asiático por fluctuación del Yen. No abrir nuevas posiciones en Japón.")

# --- FOOTER: TICKER DE NOTICIAS ---
st.markdown("---")
st.write("🏃 **Ticker de Última Hora:** [EL SABUESO] Rusia limita exportaciones de gas... [EL ORÁCULO] Satélites detectan atasco en Canal de Suez... [CARLA] Nueva actualización de IA cuántica disponible...")
