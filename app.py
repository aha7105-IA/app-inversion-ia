{\rtf1\ansi\ansicpg1252\cocoartf2868
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import yfinance as yf\
import pandas as pd\
from datetime import datetime\
\
# CONFIGURACI\'d3N DE LA P\'c1GINA\
st.set_page_config(page_title="Departamento de Inversi\'f3n IA", layout="wide", initial_sidebar_state="expanded")\
\
# ESTILO DARK MODE PROFESIONAL\
st.markdown("""\
    <style>\
    .main \{ background-color: #0e1117; color: #ffffff; \}\
    .stMetric \{ background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #30363d; \}\
    </style>\
    """, unsafe_allow_html=True)\
\
# --- SIDEBAR: ESTADO DE LOS 9 AGENTES ---\
st.sidebar.title("\uc0\u55358 \u56598  Estado del Equipo")\
agentes = \{\
    "El Sabueso": "\uc0\u55357 \u56589  Escaneando Macro",\
    "El Contable": "\uc0\u55357 \u56522  Analizando Balances",\
    "El Psic\'f3logo": "\uc0\u55358 \u56800  Midiendo Sentimiento",\
    "El Abogado del Diablo": "\uc0\u55357 \u57001  Vigilando Riesgos",\
    "El Estratega": "\uc0\u55356 \u57263  Coordinando CIO",\
    "El Arquitecto Visual": "\uc0\u55356 \u57256  Optimizando UI",\
    "Carla": "\uc0\u55357 \u56481  Innovando I+D",\
    "El Or\'e1culo": "\uc0\u55357 \u56545  Se\'f1ales Invisibles",\
    "El Sombra": "\uc0\u55357 \u56693 \u65039  Vigilando Insiders"\
\}\
for nombre, estado in agentes.items():\
    st.sidebar.write(f"**\{nombre\}:** \{estado\}")\
\
# --- T\'cdTULO PRINCIPAL ---\
st.title("\uc0\u55356 \u57307 \u65039  Terminal de Inversi\'f3n IA - Chief Executive")\
st.write(f"Fecha actual: \{datetime.now().strftime('%d/%m/%Y %H:%M')\}")\
\
# --- BLOQUE 1: CARTERA VIRTUAL ---\
col1, col2, col3, col4 = st.columns(4)\
with col1:\
    st.metric("Balance Total", "100.000,00 \'80", "+0.42%")\
with col2:\
    st.metric("Inversi\'f3n en Uranio (URA)", "15.000,00 \'80", "En espera")\
with col3:\
    st.metric("Efectivo Disponible", "85.000,00 \'80")\
with col4:\
    st.metric("Nivel de Riesgo", "Medio-Bajo", "Estable")\
\
# --- BLOQUE 2: DATOS DE MERCADO EN TIEMPO REAL ---\
st.header("\uc0\u55357 \u56520  Monitor de Activos Bajo Vigilancia")\
tickers = ['URA', 'ASML', 'PANW', 'BTC-USD', 'GC=F'] # Uranio, Chips, Ciberseguridad, Bitcoin, Oro\
data = yf.download(tickers, period="1d")['Close'].iloc[-1]\
\
cols_m = st.columns(len(tickers))\
for i, ticker in enumerate(tickers):\
    cols_m[i].metric(ticker, f"\{data[ticker]:.2f\}")\
\
# --- BLOQUE 3: EL INFORME MAESTRO DE LOS AGENTES ---\
st.divider()\
st.header("\uc0\u55357 \u56523  Informe de los Agentes (08:00 AM)")\
\
tab1, tab2, tab3 = st.tabs(["\uc0\u55356 \u57263  Selecci\'f3n del D\'eda", "\u55357 \u56693 \u65039  Power Feed (Insiders)", "\u55357 \u57001  Riesgos"])\
\
with tab1:\
    st.subheader("Uranio (ETF: URA)")\
    st.write("**Tesis:** Movimiento coordinado de legisladores en EE.UU. y d\'e9ficit de suministro global.")\
    st.info("Recomendaci\'f3n: Mantener posici\'f3n de 15.000\'80. Precio objetivo: +12%")\
\
with tab2:\
    st.subheader("Actividad de Insiders detectada por 'El Sombra'")\
    st.warning("Detecci\'f3n de compras en el sector de Ciberseguridad por parte de directivos de Palo Alto Networks.")\
\
with tab3:\
    st.subheader("An\'e1lisis del Abogado del Diablo")\
    st.error("Alerta: Volatilidad esperada en el mercado asi\'e1tico por fluctuaci\'f3n del Yen. No abrir nuevas posiciones en Jap\'f3n.")\
\
# --- FOOTER: TICKER DE NOTICIAS ---\
st.markdown("---")\
st.write("\uc0\u55356 \u57283  **Ticker de \'daltima Hora:** [EL SABUESO] Rusia limita exportaciones de gas... [EL OR\'c1CULO] Sat\'e9lites detectan atasco en Canal de Suez... [CARLA] Nueva actualizaci\'f3n de IA cu\'e1ntica disponible...")}