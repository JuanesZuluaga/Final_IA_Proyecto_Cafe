"""Dashboard histórico y chat agroclimático."""
from datetime import date, timedelta
import os

import pandas as pd
import streamlit as st

from agente import consultar
from clima import FUENTE, cargar, ventana
from ia_clasica import agendar, riesgo
from rag import buscar

st.set_page_config(page_title="Asistente agroclimático para café", page_icon="☕", layout="wide")
st.title("Asistente agroclimático para café")
st.caption("Antioquia · Histórico diario de 2024 · SI3003")

datos = st.cache_data(cargar)()
municipio = st.sidebar.selectbox("Municipio de referencia", list(datos))
serie = datos[municipio]
fecha = st.sidebar.selectbox("Fecha del escenario", sorted(serie), index=min(119, len(serie) - 1), key=f"fecha_{municipio}")
dias = st.sidebar.slider("Días de planificación", 2, 7, 5)
personas = st.sidebar.slider("Personas disponibles por día", 1, 6, 2)
contexto = dict(municipio=municipio, fecha=fecha, serie=serie, dias=dias, personas=personas)
dia = serie[fecha]
evaluacion = riesgo(dia)
plan = ventana(serie, fecha, dias)
agenda = agendar(plan, personas)
clima_tab, agenda_tab, chat_tab = st.tabs(["Clima y alerta", "Calendario de labores", "Asistente"])

with clima_tab:
    a, b, c, d = st.columns(4)
    a.metric("Temperatura media", f"{dia['temperatura']:.1f} °C")
    b.metric("Humedad relativa", f"{dia['humedad']:.1f} %")
    c.metric("Precipitación", f"{dia['precipitacion']:.1f} mm")
    d.metric("Favorabilidad para roya", evaluacion["nivel"].capitalize())
    st.caption(evaluacion["interpretacion"])
    inicio = (date.fromisoformat(fecha) - timedelta(days=29)).isoformat()
    historial = [r for f, r in sorted(serie.items()) if inicio <= f <= fecha]
    marco = pd.DataFrame([{**r, "favorabilidad": riesgo(r)["indice"]} for r in historial])
    marco["fecha"] = pd.to_datetime(marco["fecha"])
    marco = marco.set_index("fecha")
    a, b = st.columns(2)
    a.subheader("Precipitación diaria · mm")
    a.bar_chart(marco["precipitacion"])
    b.subheader("Índice de favorabilidad · 0 a 1")
    b.line_chart(marco["favorabilidad"])
    st.caption(f"Últimos 30 días hasta {fecha}. [NASA POWER]({FUENTE}) aporta datos de rejilla para puntos de referencia.")

with agenda_tab:
    st.caption("Simulación retrospectiva con lluvia observada. Las restricciones de trabajo son didácticas.")
    st.metric("Puntos de prioridad asignados", f"{agenda['prioridad_total']} de 13")
    calendario = []
    for r in plan:
        labores = [l for l in agenda["labores"] if l["fecha"] == r["fecha"]]
        calendario.append({"Fecha": r["fecha"], "Lluvia (mm)": r["precipitacion"],
                           "Labores": ", ".join(l["labor"] for l in labores) or "—",
                           "Personas asignadas": sum(l["personas"] for l in labores)})
    st.dataframe(calendario, hide_index=True)
    aplazadas = [l["labor"] for l in agenda["labores"] if l["fecha"] is None]
    if aplazadas:
        st.info("Aplazadas: " + ", ".join(aplazadas))
    if any(r["precipitacion"] is None for r in plan):
        st.warning("Los días sin datos quedan fuera de la planificación.")

with chat_tab:
    modo = st.radio("Modo", ["Consulta local", "Agente LLM"], horizontal=True)
    clave = ""
    if modo == "Agente LLM":
        clave = st.text_input("Clave de OpenAI", type="password") or os.getenv("OPENAI_API_KEY", "")
        st.caption("El agente envía la pregunta, el historial reciente y los resultados de herramientas a OpenAI.")
    else:
        st.caption("Busca referencias en el corpus local sin enviar la consulta a un proveedor.")
    escenario = (municipio, fecha, dias, personas, modo)
    if st.session_state.get("escenario") != escenario:
        st.session_state.update(escenario=escenario, conversacion=[])
    conversacion = st.session_state.conversacion

    def mostrar(respuesta):
        st.markdown(respuesta["texto"])
        for doc in respuesta["fuentes"]:
            st.markdown(f"[{doc['id']} · {doc['titulo']}]({doc['url']})")
        if respuesta["trazas"]:
            with st.expander("Llamadas a herramientas"):
                st.json(respuesta["trazas"])

    for pregunta, respuesta in conversacion:
        with st.chat_message("user"):
            st.write(pregunta)
        with st.chat_message("assistant"):
            mostrar(respuesta)
    pregunta = st.chat_input("Pregunta por el clima, la agenda o el manejo de roya",
                             max_chars=800, disabled=modo == "Agente LLM" and not clave)
    if pregunta:
        with st.chat_message("user"):
            st.write(pregunta)
        with st.chat_message("assistant"):
            if modo == "Consulta local":
                docs = buscar(pregunta)
                texto = "\n\n".join(f"[{d['id']}] {d['texto']}" for d in docs)
                respuesta = dict(texto=texto or "No encontré referencias para esta consulta.", fuentes=docs, trazas=[])
            else:
                historial_chat = []
                for anterior, salida in conversacion[-3:]:
                    if not salida.get("error"):
                        historial_chat.extend([{"role": "user", "content": anterior},
                                               {"role": "assistant", "content": salida["texto"]}])
                with st.spinner("Consultando al agente…"):
                    respuesta = consultar(pregunta, contexto, api_key=clave, historial=historial_chat)
            mostrar(respuesta)
        conversacion.append((pregunta, respuesta))
