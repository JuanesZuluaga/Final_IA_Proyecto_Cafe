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
- Agente LLM: usa un modelo con herramientas `risk`, `schedule` y `search_docs`.

El agente funciona con cualquier endpoint compatible con OpenAI. Hay tres proveedores preconfigurados; se elige desde la barra del chat:

| Proveedor | Modelo por defecto | Variable de entorno | Dónde obtener la clave |
|-----------|--------------------|---------------------|------------------------|
| OpenAI    | `gpt-4.1-mini`            | `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| Groq      | `openai/gpt-oss-20b` | `GROQ_API_KEY`   | https://console.groq.com/keys |
| NVIDIA    | `meta/llama-3.3-70b-instruct` | `NVIDIA_API_KEY` | https://build.nvidia.com (NIM) |

Groq y NVIDIA NIM ofrecen capa gratuita, recomendada para controlar costos.

Para usar el agente puedes:

- elegir el proveedor e ingresar la clave directamente en la interfaz, o
- definir la variable de entorno correspondiente antes de ejecutar la app, por ejemplo:

```bash
export GROQ_API_KEY="tu_clave"      # o OPENAI_API_KEY / NVIDIA_API_KEY
python -m streamlit run app.py
```

### Comprobar que la clave se está usando

En la pestaña del asistente, con el modo **Agente LLM**, usa el botón **"Probar conexión"**:
hace una llamada mínima real al proveedor y muestra si la clave es válida y con qué
modelo respondió, o el error exacto si falla. La leyenda "🔑 Clave: ..." indica además
si la clave que se usará viene de la interfaz o de la variable de entorno.

También puedes verificarlo desde la terminal, sin levantar la app:

```bash
export GROQ_API_KEY="tu_clave"
python -m scripts.evaluar --check --proveedor Groq
```

Opcionalmente puedes forzar otro modelo con la variable `CAFE_MODEL`.

> **Nota:** los proveedores retiran y renombran modelos con frecuencia. Si una
> consulta falla con un error tipo `model ... does not exist` o `model_decommissioned`,
> consulta la lista vigente del proveedor (p. ej. https://console.groq.com/docs/models)
> y define el nombre actual con `CAFE_MODEL`, sin cambiar el código. El mensaje de
> error de la app muestra el detalle devuelto por el proveedor para facilitar el diagnóstico.

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
python -m scripts.evaluar                        # proveedor simulado (sin clave)
python -m scripts.evaluar --llm                  # agente real con OpenAI
python -m scripts.evaluar --llm --proveedor Groq # agente real con Groq
```

La evaluación en vivo requiere la variable de entorno del proveedor elegido
(`OPENAI_API_KEY`, `GROQ_API_KEY` o `NVIDIA_API_KEY`).

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
