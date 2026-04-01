import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DEL DASHBOARD ---
st.set_page_config(page_title="Terminal IA | Chief Executive", layout="wide", initial_sidebar_state="expanded")

# --- 2. CEREBRO IA ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    modelo = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.sidebar.error("⚠️ API Key no conectada.")

# --- 3. ESTILOS CSS PREMIUM (Modo Terminal) ---
st.markdown("""
    <style>
    /* Fondo oscuro profundo */
    .main { background-color: #050505; color: #e0e0e0; }
    h1, h2, h3 { color: #ffffff; font-family: 'Courier New', Courier, monospace; }
    
    /* Estilo de las tarjetas de métricas */
    div[data-testid="metric-container"] {
        background-color: #111111;
        border: 1px solid #333333;
        border-left: 4px solid #00ff88;
        padding: 15px;
        border-radius: 4px;
        box-shadow: 0 4px 10px rgba(0,255,136,0.05);
    }
    
    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; border-radius: 4px 4px 0px 0px; padding-top: 10px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { background-color: #00ff88; color: #000000; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BARRA LATERAL: SELECTOR DE ACTIVOS ---
st.sidebar.title("⚡ COMANDOS")
st.sidebar.divider()

st.sidebar.subheader("🎯 Seleccionar Activo")
diccionario_activos = {
    "Bitcoin (Cripto)": "BTC-USD",
    "Uranio (ETF)": "URA",
    "ASML (Semiconductores)": "ASML",
    "Nvidia (IA)": "NVDA",
    "Oro (Materias Primas)": "GC=F"
}
seleccion = st.sidebar.selectbox("Fijar objetivo:", list(diccionario_activos.keys()))
ticker_actual = diccionario_activos[seleccion]

st.sidebar.divider()
st.sidebar.caption("Sistemas Operativos: 🟢 9/9 Agentes Online")
st.sidebar.caption("Divisa Base: 🇪🇺 EUR (€)")

# --- 5. EXTRACCIÓN Y CONVERSIÓN DE DATOS (A EUROS) ---
@st.cache_data(ttl=300) # Se actualiza cada 5 minutos para no saturar
def obtener_datos_convertidos(ticker):
    # Descargar activo y divisa
    df_activo = yf.download(ticker, period="3mo", interval="1d")
    df_eurusd = yf.download("EURUSD=X", period="5d")
    
    # Extraer precios de forma segura
    close_activo = df_activo['Close'].squeeze()
    open_activo = df_activo['Open'].squeeze()
    high_activo = df_activo['High'].squeeze()
    low_activo = df_activo['Low'].squeeze()
    volume_activo = df_activo['Volume'].squeeze()
    
    tipo_cambio = float(df_eurusd['Close'].ffill().iloc[-1].squeeze())
    
    # Crear un nuevo dataframe en EUROS
    df_eur = pd.DataFrame({
        'Open': open_activo / tipo_cambio,
        'High': high_activo / tipo_cambio,
        'Low': low_activo / tipo_cambio,
        'Close': close_activo / tipo_cambio,
        'Volume': volume_activo
    })
    
    # Añadir Media Móvil Simple de 20 días
    df_eur['SMA_20'] = df_eur['Close'].rolling(window=20).mean()
    
    return df_eur.dropna() # Limpiar datos nulos

df = obtener_datos_convertidos(ticker_actual)

precio_actual = float(df['Close'].iloc[-1])
precio_anterior = float(df['Close'].iloc[-2])
variacion = ((precio_actual - precio_anterior) / precio_anterior) * 100
maximo_3m = float(df['High'].max())
minimo_3m = float(df['Low'].min())
volumen_hoy = int(df['Volume'].iloc[-1])

# --- 6. CABECERA PRINCIPAL ---
st.title("🏛️ Terminal Analítica de Inversión")
st.markdown(f"**Vigilando: {seleccion}** | Última actualización: {datetime.now().strftime('%H:%M:%S')}")

# Métricas rápidas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Precio Actual (€)", f"{precio_actual:.2f} €", f"{variacion:.2f}%")
col2.metric("Máximo (3m)", f"{maximo_3m:.2f} €")
col3.metric("Mínimo (3m)", f"{minimo_3m:.2f} €")
col4.metric("Volumen Diario", f"{volumen_hoy:,}")

st.divider()

# --- 7. PESTAÑAS DE NAVEGACIÓN ---
tab1, tab2, tab3 = st.tabs(["📊 Gráfico Pro", "🧠 Reporte IA", "📰 Datos Históricos"])

with tab1:
    # Gráfico de Velas Japonesas profesional con Plotly
    fig = go.Figure()
    
    # Velas
    fig.add_trace(go.Candlestick(x=df.index,
                    open=df['Open'], high=df['High'],
                    low=df['Low'], close=df['Close'],
                    name='Precio (€)',
                    increasing_line_color='#00ff88', decreasing_line_color='#ff3333'))
    
    # Media Móvil (SMA 20)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], 
                             line=dict(color='#00d4ff', width=1.5), 
                             name='SMA 20 Días'))
    
    # Diseño del gráfico
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#050505',
        plot_bgcolor='#050505',
        margin=dict(l=10, r=10, t=10, b=10),
        height=550,
        xaxis_rangeslider_visible=False,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Análisis Estratégico Generado por IA")
    if st.button("🚀 Iniciar Análisis de los Agentes", use_container_width=True):
        with st.spinner("Conectando con la matriz de agentes..."):
            prompt = f"""
            Eres el equipo de analistas de un fondo de inversión. 
            Actualmente estamos viendo el activo: {seleccion} (Ticker: {ticker_actual}).
            El precio actual es {precio_actual:.2f} EUROS (€) y ha variado un {variacion:.2f}% hoy.
            
            Redacta un informe ejecutivo urgente estructurado así:
            1. 'El Sabueso' (Macro): Contexto actual del sector de este activo.
            2. 'El Analista Técnico': Qué significa esa variación del {variacion:.2f}% (teniendo en cuenta que estamos usando una media móvil de 20 días).
            3. 'El Abogado del Diablo' (Riesgo): ¿Cuál es el peor escenario posible si compramos ahora?
            
            Usa un formato muy limpio. IMPORTANTE: Expresa todos los valores monetarios en EUROS (€).
            """
            try:
                respuesta = modelo.generate_content(prompt)
                st.markdown(respuesta.text)
            except Exception as e:
                st.error(f"Fallo de conexión con el satélite Gemini: {e}")
    else:
        st.info("El equipo está a la espera de sus órdenes para procesar este activo. Haga clic en el botón superior.")

with tab3:
    st.subheader("Datos en Crudo (EUR €)")
    # Formateamos el dataframe para que se vea limpio
    df_mostrar = df.tail(10).sort_index(ascending=False).copy()
    for col in ['Open', 'High', 'Low', 'Close', 'SMA_20']:
        df_mostrar[col] = df_mostrar[col].apply(lambda x: f"{x:.2f} €")
    st.dataframe(df_mostrar, use_container_width=True)
