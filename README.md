# Asistente agroclimático para café

Este proyecto cumple con la idea del curso de IA: combina una técnica clásica (modelo bayesiano + programación por restricciones) con un agente LLM con RAG y un dashboard interactivo para apoyar decisiones agronómicas en café.

## ¿Para qué sirve?

La aplicación ayuda a:

- entender el clima histórico de Andes y Urrao,
- observar si las condiciones son favorables para la roya,
- planear labores del día a día con la cuadrilla disponible,
- consultar información técnica de Cenicafé y FNC en lenguaje natural.

Es una herramienta de apoyo para análisis y planificación, no un diagnóstico agronómico definitivo.

## Requisitos

- Python 3.10 o superior
- Git
- Conexión opcional para usar el agente LLM con OpenAI

## Instalación rápida

```bash
cd /ruta/al/proyecto
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

En Windows:

```powershell
cd \ruta\al\proyecto
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Cómo usar la app

1. En la barra lateral, selecciona el municipio.
2. Elige la fecha del escenario.
3. Ajusta la cantidad de días y la cantidad de personas disponibles.
4. Revisa la pestaña de clima para ver temperatura, humedad y riesgo.
5. En la pestaña de calendario, observa qué labores quedan programadas o aplazadas.
6. En la pestaña del asistente, haz preguntas naturales.

### Modos del asistente

- Consulta local: busca en el corpus sin enviar datos externos.
- Agente LLM: usa el modelo de OpenAI con herramientas `risk`, `schedule` y `search_docs`.

Si prefieres usar el agente LLM, puedes:

- ingresar la clave en la interfaz, o
- definir la variable de entorno `OPENAI_API_KEY` antes de ejecutar la app.

## Datos del proyecto

Los datos históricos provienen de NASA POWER y se guardan localmente en `data/clima_historico.csv`.

- Municipios: Andes y Urrao
- Variable principal: precipitación diaria
- Variables adicionales: temperatura media, humedad relativa
- Cobertura: 2024

## Modelo clásico implementado

Se desarrolló una lógica propia de:

- indicador bayesiano de favorabilidad climática para roya,
- planificador basado en restricciones para asignar labores,
- comparación contra una línea base para validar el desempeño.

Los resultados se evaluaron con las métricas del proyecto y la validación automática del repositorio.

## RAG y agente LLM

El agente puede:

- consultar condiciones climáticas,
- consultar la agenda de labores,
- recuperar referencias técnicas de Cenicafé y FNC,
- responder con citas a documentos relevantes.

## Evaluación incluida

Se incluye una evaluación reproducible con preguntas fijas:

```bash
python -m scripts.evaluar
python -m scripts.evaluar --llm
```

La segunda opción requiere una `OPENAI_API_KEY` válida.

## Archivos clave

- `app.py`: dashboard principal
- `ia_clasica.py`: algoritmo clásico de riesgo y planificación
- `agente.py`: ciclo del agente y llamadas a herramientas
- `rag.py`: recuperación documental local con TF-IDF
- `clima.py`: carga de datos climáticos
- `data/corpus.json`: referencias técnicas para RAG
- `INFORME.md`: resumen técnico del proyecto
- `USO_IA.md`: declaración de uso de IA generativa

## Limitaciones

La aplicación está pensada como MVP funcional y educativo. El indicador climático es un estimador didáctico y no reemplaza mediciones reales ni diagnóstico de campo.

## Créditos

Proyecto final de IA con foco en café, clima y decisión agronómica en Antioquia.
