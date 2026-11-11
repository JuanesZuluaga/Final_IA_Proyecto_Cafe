
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from ia_clasica import calcular_riesgo_roya, agendar_labores

def consultar_agente(pregunta, api_key, contexto_clima):
    if not api_key:
        return "⚠️ Error: Por favor ingresa tu API Key de OpenAI (o Groq/NIM) en la barra lateral para usar el agente."
        
    try:
        # Configuración básica del LLM (puedes cambiar a ChatGroq si prefieres)
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_key=api_key)
        
        # Simulamos el Tool Calling integrando los datos de la IA Clásica en el contexto del sistema
        temp_actual = contexto_clima['temperatura']
        hum_actual = contexto_clima['humedad']
        riesgo, prob = calcular_riesgo_roya(temp_actual, hum_actual)
        
        system_prompt = f"""Eres un Asistente Agroclimático experto en café en Colombia.
        Tienes acceso a los siguientes datos actuales de la finca gracias a los modelos clásicos (Red Bayesiana/CSP):
        - Temperatura: {temp_actual:.1f} °C
        - Humedad: {hum_actual:.1f} %
        - Riesgo de Roya actual: {riesgo} (Probabilidad: {prob:.0%})
        
        Responde a las consultas del agricultor de forma concisa, recomendando acciones basadas en la literatura de Cenicafé.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=pregunta)
        ]
        
        respuesta = llm(messages)
        return respuesta.content
    except Exception as e:
        return f"Error al comunicar con el LLM: {str(e)}"
