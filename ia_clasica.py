
import random

# Parte 1.1: Red Bayesiana (Simulada con tabla de probabilidad condicional para no depender de pgmpy)
# Calcula el riesgo de roya basado en Temperatura y Humedad
def calcular_riesgo_roya(temperatura, humedad):
    prob_roya = 0.1 # Base
    
    if temperatura > 21 and temperatura < 25:
        prob_roya += 0.4
    elif temperatura >= 25:
        prob_roya += 0.2
        
    if humedad > 85:
        prob_roya += 0.4
    elif humedad > 75:
        prob_roya += 0.2
        
    prob_roya = min(prob_roya, 0.95)
    
    if prob_roya > 0.7:
        return "ALTO", prob_roya
    elif prob_roya > 0.4:
        return "MEDIO", prob_roya
    else:
        return "BAJO", prob_roya

# Parte 1.2: Problema de Satisfacción de Restricciones (CSP) Simple para Agendar Labores
# Restricciones: No fertilizar si llueve mucho, no cosechar si llueve mucho.
def agendar_labores(datos_clima_proximos_dias):
    agenda = {}
    for dia in datos_clima_proximos_dias:
        fecha = dia['fecha']
        lluvia = dia['precipitacion']
        
        if lluvia < 2.0:
            agenda[fecha] = "Cosecha / Poda"
        elif lluvia >= 2.0 and lluvia < 10.0:
            agenda[fecha] = "Fertilización (suelo húmedo)"
        else:
            agenda[fecha] = "Mantenimiento bajo techo (Lluvia fuerte)"
            
    return agenda
