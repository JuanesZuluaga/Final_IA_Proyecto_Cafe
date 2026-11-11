
import streamlit as st
import pandas as pd
from ia_clasica import calcular_riesgo_roya, agendar_labores
from agente import consultar_agente
import datetime

st.set_page_config(page_title="Asistente Agroclimático Café", layout="wide")

st.title("🌱 Asistente Agroclimático para Café")
st.markdown("Plataforma integrada de IA para la gestión del riesgo de roya y labores agrícolas.")

# --- BARRA LATERAL (Parámetros) ---
st.sidebar.header("⚙️ Configuración")
api_key = st.sidebar.text_input("OpenAI API Key (para el Agente):", type="password")
municipio = st.sidebar.selectbox("Municipio / Finca:", ["Marinilla (Finca La Esperanza)", "Andes (Finca El Mirador)"])
fecha_consulta = st.sidebar.date_input("Fecha de Análisis:", datetime.date(2026, 11, 4))

# Cargar Datos Mock
@st.cache_data
def load_data():
    return pd.read_csv("data/clima_historico.csv")

df = load_data()
df['fecha'] = pd.to_datetime(df['fecha']).dt.date

# Obtener datos del día seleccionado
datos_dia = df[df['fecha'] == fecha_consulta]

if datos_dia.empty:
    st.warning("No hay datos históricos para esta fecha. Usando datos simulados.")
    temp, hum, precip = 22.5, 82.0, 5.0
else:
    temp = datos_dia.iloc[0]['temperatura']
    hum = datos_dia.iloc[0]['humedad']
    precip = datos_dia.iloc[0]['precipitacion']

contexto_actual = {'temperatura': temp, 'humedad': hum, 'precipitacion': precip}

# --- TABS DEL DASHBOARD ---
tab1, tab2, tab3 = st.tabs(["📊 Dashboard Climático & Clásica", "🗓️ CSP Labores", "🤖 Agente Inteligente (RAG)"])

with tab1:
    st.header("Condiciones Actuales y Riesgo de Roya (Red Bayesiana)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Temperatura", f"{temp:.1f} °C")
    col2.metric("Humedad", f"{hum:.1f} %")
    col3.metric("Precipitación", f"{precip:.1f} mm")
    
    riesgo, prob = calcular_riesgo_roya(temp, hum)
    st.subheader(f"⚠️ Riesgo Estimado de Roya: {riesgo}")
    st.progress(prob)
    st.caption("Calculado mediante inferencia probabilística basada en temperatura y humedad.")
    
    st.line_chart(df.set_index('fecha')[['temperatura', 'humedad']].tail(30))

with tab2:
    st.header("Planificación de Labores (CSP)")
    st.markdown("Asignación de tareas restringida por condiciones climáticas de los próximos 5 días.")
    
    # Simular próximos 5 días
    proximos_dias = []
    for i in range(5):
        proximos_dias.append({
            'fecha': (fecha_consulta + datetime.timedelta(days=i)).strftime("%Y-%m-%d"),
            'precipitacion': df['precipitacion'].sample().iloc[0] # random sample for demo
        })
    
    agenda = agendar_labores(proximos_dias)
    for f, labor in agenda.items():
        st.info(f"**{f}**: {labor}")

with tab3:
    st.header("Chat con el Asistente Agroclimático")
    st.markdown("Consulta recomendaciones basadas en manuales de Cenicafé. El agente conoce tu riesgo actual.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if prompt := st.chat_input("Ej: ¿Qué fungicida recomiendas para riesgo alto?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Consultando manuales..."):
                respuesta = consultar_agente(prompt, api_key, contexto_actual)
                st.markdown(respuesta)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
