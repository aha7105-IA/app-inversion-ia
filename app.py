import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DEL DASHBOARD ---
st.set_page_config(page_title="Terminal IA Avanzada", layout="wide", initial_sidebar_state="expanded")

# --- 2. CEREBRO IA ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    modelo = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.sidebar.error("⚠️ API Key no conectada.")

# --- 3. ESTILOS CSS PROFESIONALES ---
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #ffffff; }
    h1, h2, h3 { color: #f0f6fc; }
    .stMetric { background-color: #161b22; border-left: 5px solid #2ea043; padding: 15px; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BARRA LATERAL: SELECTOR DE ACTIVOS ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Jon_Kirsch%27s_Logo.png/120px-Jon_Kirsch%27s_Logo.png", width=50) # Logo genérico
st.sidebar.title("Centro de Mando")
st.sidebar.divider()

st.sidebar.subheader("🎯 Seleccionar Activo")
diccionario_activos = {
    "Bitcoin (Cripto)": "BTC-USD",
    "Uranio (ETF)": "URA",
    "ASML (Semiconductores)": "ASML",
    "Nvidia (IA)": "NVDA",
    "Oro (Materias Primas)": "GC=F"
}
seleccion = st.sidebar.selectbox("¿Qué mercado analizamos hoy?", list(diccionario_activos.keys()))
ticker_actual = diccionario_activos[seleccion]

st.sidebar.divider()
st.sidebar.caption("Sistemas Operativos: 🟢 9/9 Agentes Online")

# --- 5. DESCARGA DE DATOS EN TIEMPO REAL ---
@st.cache_data(ttl=300) # Guarda los datos 5 minutos para que la web vaya ultra rápida
def obtener_datos(ticker):
    datos = yf.download(ticker, period="3mo", interval="1d")
    return datos

df = obtener_datos(ticker_actual)
precio_actual = df['Close'].iloc[-1].item()
precio_anterior = df['Close'].iloc[-2].item()
variacion = ((precio_actual - precio_anterior) / precio_anterior) * 100

# --- 6. CABECERA PRINCIPAL ---
st.title("🏛️ Terminal Analítica de Inversión")
st.markdown(f"**Análisis de {seleccion}** | Última actualización: {datetime.now().strftime('%H:%M:%S')}")

# Métricas rápidas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Precio Actual", f"{precio_actual:.2f} $", f"{variacion:.2f}%")
col2.metric("Máximo (3 meses)", f"{df['High'].max().item():.2f} $")
col3.metric("Mínimo (3 meses)", f"{df['Low'].min().item():.2f} $")
col4.metric("Volumen de hoy", f"{int(df['Volume'].iloc[-1].item()):,}")

st.divider()

# --- 7. PESTAÑAS DE NAVEGACIÓN ---
tab1, tab2, tab3 = st.tabs(["📊 Gráfico Interactivo (El Analista)", "🧠 Reporte de la IA (El Equipo)", "📰 Datos Raw"])

with tab1:
    st.subheader(f"Acción del Precio: {seleccion}")
    # Gráfico de Velas Japonesas profesional con Plotly
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                    open=df['Open'].squeeze(),
                    high=df['High'].squeeze(),
                    low=df['Low'].squeeze(),
                    close=df['Close'].squeeze(),
                    increasing_line_color='#2ea043', decreasing_line_color='#f85149')])
    
    fig.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=30, b=0), height=500,
                      xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Análisis Estratégico Generado por IA")
    if st.button("🚀 Iniciar Análisis de los Agentes", use_container_width=True):
        with st.spinner("Conectando con la matriz de agentes..."):
            prompt = f"""
            Eres el equipo de analistas de un fondo de inversión. 
            Actualmente estamos viendo el activo: {seleccion} (Ticker: {ticker_actual}).
            El precio actual es {precio_actual:.2f} y ha variado un {variacion:.2f}% hoy.
            
            Redacta un informe ejecutivo urgente estructurado así:
            1. 'El Sabueso' (Macro): Contexto actual del sector de este activo.
            2. 'El Analista Técnico': Breve comentario sobre qué significa esa variación del {variacion:.2f}%.
            3. 'El Abogado del Diablo' (Riesgo): ¿Cuál es el peor escenario posible si compramos ahora?
            
            Sé crudo, directo y usa un tono muy profesional y técnico.
            """
            try:
                respuesta = modelo.generate_content(prompt)
                st.markdown(respuesta.text)
            except Exception as e:
                st.error(f"Fallo de conexión con el satélite Gemini: {e}")
    else:
        st.info("El equipo está a la espera de sus órdenes para procesar este activo.")

with tab3:
    st.subheader("Histórico de Precios (Últimos 10 días)")
    st.dataframe(df.tail(10).sort_index(ascending=False), use_container_width=True)
