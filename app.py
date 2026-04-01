import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import google.generativeai as genai
import time

# --- 1. CONFIGURACIÓN DEL DASHBOARD ---
st.set_page_config(page_title="Terminal IA | Autonomous Mode", layout="wide", initial_sidebar_state="expanded")

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

# --- 4. BARRA LATERAL: CONTROL DE AGENTES ---
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
st.sidebar.caption("Sistemas Operativos: 🟢 9/9 Agentes Online")
st.sidebar.caption("Divisa Base: 🇪🇺 EUR (€)")

# --- 5. EXTRACCIÓN Y CONVERSIÓN DE DATOS (A EUROS) ---
@st.cache_data(ttl=60) # Refresca datos de bolsa cada 60 segundos para ser muy rápido
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
maximo_3m = float(df['High'].max())
minimo_3m = float(df['Low'].min())
volumen_hoy = int(df['Volume'].iloc[-1])

# --- 6. CABECERA PRINCIPAL ---
status_text = '<span class="status-live">● LIVE</span>' if modo_auto else '<span>○ STANDBY</span>'
st.markdown(f"<h1>🏛️ Terminal Analítica {status_text}</h1>", unsafe_allow_html=True)
st.markdown(f"**Vigilando: {seleccion}** | Última lectura de mercado: {datetime.now().strftime('%H:%M:%S')}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Precio Actual (€)", f"{precio_actual:.2f} €", f"{variacion:.2f}%")
col2.metric("Máximo (3m)", f"{maximo_3m:.2f} €")
col3.metric("Mínimo (3m)", f"{minimo_3m:.2f} €")
col4.metric("Volumen Diario", f"{volumen_hoy:,}")

st.divider()

# --- 7. INICIALIZAR MEMORIA DE LA IA ---
if 'ultimo_informe' not in st.session_state:
    st.session_state.ultimo_informe = "El sistema está a la espera de sus órdenes para generar el primer reporte."
if 'ultima_actualizacion' not in st.session_state:
    # Truco para que, si pulsas auto, no tengas que esperar la primera vez
    st.session_state.ultima_actualizacion = datetime.now() - timedelta(minutes=intervalo + 1) 

def generar_inteligencia():
    prompt = f"""
    Actúa como el analista jefe de un fondo de cobertura cuantitativo.
    Activo bajo análisis: {seleccion} ({ticker_actual}). 
    Precio: {precio_actual:.2f} € | Variación diaria: {variacion:.2f}%.
    
    Genera un informe ULTRA-ESQUEMATIZADO para el CEO. 
    REGLAS: Cero párrafos largos. Solo viñetas. Expresa dinero en EUROS (€). Mantén este formato exacto:

    ### 🌐 1. CONTEXTO MACRO (El Sabueso)
    * **Driver Principal:** (1 frase directa sobre qué mueve el sector hoy).
    * **Dato Clave:** (1 métrica relevante).

    ### 📊 2. ACCIÓN DEL PRECIO (El Analista)
    * **Diagnóstico Técnico:** (¿Qué indica el {variacion:.2f}% frente a la SMA 20?).
    * **Flujo de Dinero:** (Entrada o salida institucional).

    ### ⚠️ 3. EVALUACIÓN DE RIESGO (El Abogado del Diablo)
    * **Peligro Inminente:** (Mayor riesgo a corto plazo).
    * **Peor Escenario:** (Qué pasaría si sale mal).
    
    ### 🎯 CONCLUSIÓN
    * **Veredicto:** (COMPRA FUERTE / MANTENER / VENTA / ESPERAR)
    """
    try:
        res = modelo.generate_content(prompt)
        st.session_state.ultimo_informe = res.text
        st.session_state.ultima_actualizacion = datetime.now()
    except Exception as e:
        st.error(f"Fallo de conexión IA: {e}")

# --- 8. PESTAÑAS DE NAVEGACIÓN ---
tab1, tab2, tab3 = st.tabs(["📊 Gráfico Pro", "🧠 Reporte IA Automático", "📰 Datos Históricos"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    name='Precio (€)', increasing_line_color='#00ff88', decreasing_line_color='#ff3333'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='#00d4ff', width=1.5), name='SMA 20 Días'))
    fig.update_layout(template='plotly_dark', paper_bgcolor='#050505', plot_bgcolor='#050505',
        margin=dict(l=10, r=10, t=10, b=10), height=550, xaxis_rangeslider_visible=False,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Análisis Táctico Esquematizado")
    
    # Lógica de temporizador visual
    tiempo_pasado = (datetime.now() - st.session_state.ultima_actualizacion).total_seconds()
    
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        if st.button("🚀 Forzar Análisis Ahora", use_container_width=True):
            with st.spinner("Analizando variables..."):
                generar_inteligencia()
    
    with col_info:
        if modo_auto:
            segundos_restantes = int((intervalo * 60) - tiempo_pasado)
            if segundos_restantes > 0:
                st.info(f"Modo Automático ON. Próximo reporte de los agentes en **{segundos_restantes} segundos**.")
            else:
                st.warning("⏱️ Generando reporte autónomo...")
                generar_inteligencia()
                st.rerun() # Obliga a limpiar el mensaje de "Generando..."
    
    st.markdown(st.session_state.ultimo_informe)
    st.caption(f"Último reporte generado a las: {st.session_state.ultima_actualizacion.strftime('%H:%M:%S')}")

with tab3:
    st.subheader("Datos en Crudo (EUR €)")
    df_mostrar = df.tail(10).sort_index(ascending=False).copy()
    for col in ['Open', 'High', 'Low', 'Close', 'SMA_20']:
        df_mostrar[col] = df_mostrar[col].apply(lambda x: f"{x:.2f} €")
    st.dataframe(df_mostrar, use_container_width=True)

# --- 9. BUCLE DE REFRESCO AUTÓNOMO ---
if modo_auto:
    time.sleep(10) # Refresca el precio del activo cada 10 segundos silenciosamente
    st.rerun()
