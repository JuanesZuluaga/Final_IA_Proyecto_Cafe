# Asistente agroclimático para café · SI3003

MVP para explorar condiciones históricas asociadas a la roya y ensayar una agenda de labores en dos municipios cafeteros de Antioquia.

## Ejecutar

Desde la raíz del repositorio, con Python 3.14:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

En Windows se activa con `.venv\Scripts\Activate.ps1`. La consulta local, las gráficas y el calendario funcionan con los archivos incluidos. Para conversar con el LLM, selecciona **Agente LLM** e ingresa una clave de OpenAI en el campo de contraseña, o configura `OPENAI_API_KEY` fuera del repositorio. `CAFE_MODEL` permite elegir un modelo compatible con llamadas de herramientas. El valor predeterminado es `gpt-4.1-mini`.

### Recorrido de demostración

1. Abre **Clima y alerta** y alterna entre Andes y Urrao. Revisa los cambios en precipitación y en el índice de favorabilidad.
2. Abre **Calendario de labores** y baja la cuadrilla a una persona. Comprueba qué labores quedan aplazadas.
3. En **Asistente**, prueba «¿Qué variedades resistentes recomienda Cenicafé?» en modo local. Con el LLM activo, prueba «¿Qué indica el clima y cómo orienta el monitoreo según Cenicafé?». Abre el detalle de herramientas y comprueba las referencias.

## Datos y reproducción

El CSV incluye 732 registros diarios de 2024 para Andes (5.66, −75.88) y Urrao (6.32, −76.13). La fuente es [NASA POWER Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/), comunidad AG, variables `T2M` (°C), `RH2M` (%) y `PRECTOTCORR` (mm/día). Son estimaciones en rejilla para coordenadas de Colombia. Cada punto aproxima el entorno municipal. El CSV local permite repetir la demostración sin conexión a la fuente.

```bash
python -m scripts.descargar_clima
python -m scripts.evaluar
python -m scripts.evaluar --llm
```

La descarga usa HTTPS. En macOS, si la instalación de Python no encuentra la raíz de confianza, configura sus certificados o usa `SSL_CERT_FILE=/etc/ssl/cert.pem` si ese archivo existe. La tercera orden requiere una clave válida de OpenAI en el entorno y hace 12 consultas con posibles costos.

El [informe breve](INFORME.md) explica el método y la evaluación. Las trazas de la prueba local están en [evaluacion_local.jsonl](evaluacion_local.jsonl). El uso de IA se describe en [USO_IA.md](USO_IA.md).
