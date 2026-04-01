import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import google.generativeai as genai
import time

# --- 1. CONFIGURACIÓN DEL DASHBOARD ---
st.set_page_config(page_title="Terminal IA | Chief Executive", layout="wide", initial_sidebar_state="expanded")

# --- INICIALIZAR BANCO VIRTUAL Y MEMORIA ---
if 'cash' not in st.session_state:
    st.session_state.cash = 100000.0 # Tus 100.000€ iniciales
if 'cartera' not in st.session_state:
    st.session_state.cartera = {} # Aquí se guardan tus activos comprados
if 'ultimo_informe' not in st.session_state:
    st.session_state.ultimo_informe = "El sistema está a la espera de sus órdenes."
if 'ultima_actualizacion' not in st.session_state:
    st.session_state.ultima_actualizacion = datetime.now() - timedelta(minutes=60)

# --- 2. CEREBRO IA ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    modelo = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.sidebar.error("⚠️ API Key no conectada.")

# --- 3. ESTILOS CSS PREMIUM ---
st.markdown("""
    <style>
    .main { background-color: #050505; color: #e0e0e0; }
    h1, h2, h3 { color: #ffffff; font-family: 'Courier New', Courier, monospace; }
    div[data-testid="metric-container"] {
        background-color: #111111; border: 1px solid #333333; border-left: 4px solid #00ff88;
        padding: 15px; border-radius: 4px; box-shadow: 0 4px 10px rgba(0,255,136,0.05);
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; border-radius: 4px 4px 0px 0px; padding-top: 10px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { background-color: #00ff88; color: #000000; font-weight: bold; }
    .status-live { color: #00ff88; font-weight: bold; animation: blinker 2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BARRA LATERAL ---
st.sidebar.title("⚡ SISTEMA AUTÓNOMO")
modo_auto = st.sidebar.toggle("Activar Modo Vigilancia (Auto-Update)", value=False)
intervalo = st.sidebar.select_slider("Frecuencia del reporte IA (min):", options=[1, 5, 15, 30, 60], value=15)

st.sidebar.divider()
st.sidebar.subheader("🎯 Seleccionar Activo")
diccionario_activos = {
    "Bitcoin (Cripto)": "BTC-USD", "Uranio (ETF)": "URA", "ASML (Semiconductores)": "ASML",
    "Nvidia (IA)": "NVDA", "Oro (Materias Primas)": "GC=F"
}
seleccion = st.sidebar.selectbox("Fijar objetivo:", list(diccionario_activos.keys()))
ticker_actual = diccionario_activos[seleccion]

st.sidebar.divider()
# Mostrar resumen del banco en la barra lateral
st.sidebar.success(f"💰 Liquidez: {st.session_state.cash:,.2f} €")

# --- 5. EXTRACCIÓN DE DATOS ---
@st.cache_data(ttl=60)
def obtener_datos_convertidos(ticker):
    df_activo = yf.download(ticker, period="3mo", interval="1d")
    df_eurusd = yf.download("EURUSD=X", period="5d")
    
    close_activo = df_activo['Close'].squeeze()
    open_activo = df_activo['Open'].squeeze()
    high_activo = df_activo['High'].squeeze()
    low_activo = df_activo['Low'].squeeze()
    volume_activo = df_activo['Volume'].squeeze()
    
    tipo_cambio = float(df_eurusd['Close'].ffill().iloc[-1].squeeze())
    
    df_eur = pd.DataFrame({
        'Open': open_activo / tipo_cambio, 'High': high_activo / tipo_cambio,
        'Low': low_activo / tipo_cambio, 'Close': close_activo / tipo_cambio,
        'Volume': volume_activo
    })
    df_eur['SMA_20'] = df_eur['Close'].rolling(window=20).mean()
    return df_eur.dropna()

df = obtener_datos_convertidos(ticker_actual)

precio_actual = float(df['Close'].iloc[-1])
precio_anterior = float(df['Close'].iloc[-2])
variacion = ((precio_actual - precio_anterior) / precio_anterior) * 100

# --- 6. CABECERA PRINCIPAL ---
status_text = '<span class="status-live">● LIVE</span>' if modo_auto else '<span>○ STANDBY</span>'
st.markdown(f"<h1>🏛️ Terminal Analítica {status_text}</h1>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Precio Actual (€)", f"{precio_actual:.2f} €", f"{variacion:.2f}%")
col2.metric("Máximo (3m)", f"{float(df['High'].max()):.2f} €")
col3.metric("Mínimo (3m)", f"{float(df['Low'].min()):.2f} €")
col4.metric("Volumen Diario", f"{int(df['Volume'].iloc[-1]):,}")

st.divider()

# --- FUNCION DE IA ---
def generar_inteligencia():
    prompt = f"""
    Actúa como analista jefe. Activo: {seleccion} ({ticker_actual}). Precio: {precio_actual:.2f} €.
    Genera un informe ULTRA-ESQUEMATIZADO en viñetas. Solo usa EUROS. Formato:
    ### 🌐 1. CONTEXTO MACRO
    * **Driver:**
    ### 📊 2. ACCIÓN DEL PRECIO
    * **Técnico:**
    ### ⚠️ 3. EVALUACIÓN DE RIESGO
    * **Riesgo:**
    ### 🎯 CONCLUSIÓN
    * **Veredicto:** (COMPRA FUERTE / MANTENER / VENTA / ESPERAR)
    """
    try:
        res = modelo.generate_content(prompt)
        st.session_state.ultimo_informe = res.text
        st.session_state.ultima_actualizacion = datetime.now()
    except Exception as e:
        st.error("Fallo de IA")

# --- 7. PESTAÑAS ---
# HEMOS AÑADIDO UNA NUEVA PESTAÑA AQUÍ
tab1, tab2, tab3, tab4 = st.tabs(["📊 Gráfico Pro", "🧠 Reporte IA", "📰 Datos Históricos", "💼 Simulador de Cartera"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    name='Precio (€)', increasing_line_color='#00ff88', decreasing_line_color='#ff3333'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='#00d4ff', width=1.5), name='SMA 20 Días'))
    fig.update_layout(template='plotly_dark', paper_bgcolor='#050505', plot_bgcolor='#050505',
        margin=dict(l=10, r=10, t=10, b=10), height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Análisis Táctico Esquematizado")
    if st.button("🚀 Forzar Análisis Ahora", use_container_width=True):
        with st.spinner("Analizando variables..."):
            generar_inteligencia()
    st.markdown(st.session_state.ultimo_informe)

with tab3:
    st.subheader("Datos en Crudo (EUR €)")
    st.dataframe(df.tail(10).sort_index(ascending=False), use_container_width=True)

with tab4:
    st.subheader(f"Mesa de Operaciones: {seleccion}")
    
    # Obtener la posición actual del usuario en este activo
    posicion = st.session_state.cartera.get(ticker_actual, {'cantidad': 0.0, 'invertido': 0.0})
    valor_actual_posicion = posicion['cantidad'] * precio_actual
    beneficio_posicion = valor_actual_posicion - posicion['invertido']
    
    # Mostrar métricas del portfolio
    cp1, cp2, cp3 = st.columns(3)
    cp1.metric("Liquidez Disponible", f"{st.session_state.cash:,.2f} €")
    cp2.metric(f"Tus uds. de {ticker_actual}", f"{posicion['cantidad']:.4f}", f"{beneficio_posicion:,.2f} € (Beneficio/Pérdida)")
    cp3.metric("Valor Actual de tu Posición", f"{valor_actual_posicion:,.2f} €")
    
    st.divider()
    
    # Interfaz de Compra/Venta
    col_compra, col_venta = st.columns(2)
    
    with col_compra:
        st.markdown("<h3 style='color: #00ff88;'>🛒 COMPRAR</h3>", unsafe_allow_html=True)
        cant_compra = st.number_input(f"Cantidad a comprar", min_value=0.0, step=0.1, key="compra")
        coste = cant_compra * precio_actual
        st.write(f"Coste de la operación: **{coste:,.2f} €**")
        
        if st.button("Ejecutar COMPRA", type="primary", use_container_width=True):
            if coste > 0 and coste <= st.session_state.cash:
                st.session_state.cash -= coste
                st.session_state.cartera[ticker_actual] = {
                    'cantidad': posicion['cantidad'] + cant_compra,
                    'invertido': posicion['invertido'] + coste
                }
                st.success(f"¡Compra ejecutada con éxito!")
                st.rerun()
            elif coste > st.session_state.cash:
                st.error("Liquidez insuficiente para esta operación.")
                
    with col_venta:
        st.markdown("<h3 style='color: #ff3333;'>💸 VENDER</h3>", unsafe_allow_html=True)
        cant_venta = st.number_input(f"Cantidad a vender", min_value=0.0, max_value=float(posicion['cantidad']), step=0.1, key="venta")
        ingreso = cant_venta * precio_actual
        st.write(f"Ingreso de la operación: **{ingreso:,.2f} €**")
        
        if st.button("Ejecutar VENTA", use_container_width=True):
            if cant_venta > 0 and cant_venta <= posicion['cantidad']:
                st.session_state.cash += ingreso
                proporcion_vendida = cant_venta / posicion['cantidad']
                st.session_state.cartera[ticker_actual] = {
                    'cantidad': posicion['cantidad'] - cant_venta,
                    'invertido': posicion['invertido'] - (posicion['invertido'] * proporcion_vendida)
                }
                st.success(f"¡Venta ejecutada con éxito!")
                st.rerun()

# --- BUCLE AUTÓNOMO ---
if modo_auto:
    time.sleep(10)
    st.rerun()
