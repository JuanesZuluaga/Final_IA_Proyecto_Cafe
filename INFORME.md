# Informe breve · Asistente agroclimático para café

Los cambios en lluvia, temperatura y humedad pueden afectar la planeación de labores del cafetal. El MVP muestra un escenario histórico de Andes o Urrao, estima la favorabilidad climática y calcula qué labores caben en la ventana con la cuadrilla disponible. Las publicaciones técnicas respaldan las explicaciones del asistente.

## Datos y método clásico

NASA POWER aporta 366 días de 2024 por punto. Se conservan los días completos y se verifican rangos físicos al descargar. La resolución de la rejilla y el relieve limitan la representatividad a escala de finca.

La red bayesiana didáctica usa dos dependencias. La lluvia y la humedad relativa determinan una distribución para la humectación. Esta distribución y una categoría de temperatura determinan el índice de favorabilidad. Se marginalizan los dos estados de humectación mediante la ley de probabilidad total. Las tablas y umbrales son supuestos del prototipo sin calibración con observaciones de roya.

En el CSP cada labor se asigna a una fecha o se aplaza. El dominio excluye días sin dato y días que exceden el límite de lluvia de la labor. La suma de personas asignadas en un día no puede exceder la cuadrilla. La búsqueda con retroceso maximiza la prioridad total y, en caso de empate, minimiza la suma de días transcurridos hasta las labores asignadas. La línea base recorre las mismas labores por prioridad y elige el primer día que cumple las restricciones.

## Agente y RAG

El LLM puede invocar `risk`, `schedule` y `search_docs`. Las primeras dos herramientas consultan el mismo escenario que muestra el dashboard. La tercera recupera hasta dos pasajes de un corpus de cinco resúmenes atribuidos a Cenicafé y FNC, mediante similitud coseno de vectores TF-IDF. El agente recibe el resultado de cada herramienta y puede solicitar otras hasta completar cuatro rondas. Las referencias visibles se vinculan a los pasajes recuperados en el turno.

## Resultados y límites

En 2.172 escenarios (dos municipios, 362 ventanas por municipio y tres tamaños de cuadrilla), ambos algoritmos respetaron las restricciones. El CSP obtuvo 18.937 puntos acumulados frente a 18.844 de la línea base, una diferencia de 0,49 %. Mejoró el puntaje en 31 casos y redujo la demora con igual puntaje en otros 226. Las ventanas se solapan y la evaluación mide el objetivo del planificador, sin inferir impacto en campo.

Las 12 preguntas fijas pasaron la prueba de protocolo con un proveedor simulado (12/12). El simulador prescribe las llamadas esperadas y comprueba el intercambio con las herramientas y la resolución de citas; no evalúa la selección de herramientas del modelo real. Para medir esa selección y la calidad de las respuestas se ejecuta `python -m scripts.evaluar --llm --proveedor <OpenAI|Groq|NVIDIA>` con una clave válida y se revisan los textos contra las fuentes citadas. El corpus es pequeño y la recuperación depende de la coincidencia léxica (TF-IDF), lo que limita el recall ante sinónimos.

El agente admite tres endpoints compatibles con OpenAI (OpenAI, Groq y NVIDIA NIM); los dos últimos tienen capa gratuita. Como los proveedores retiran modelos con frecuencia, el nombre del modelo es configurable con `CAFE_MODEL` y los errores del proveedor se devuelven como texto para facilitar el diagnóstico sin tumbar la app.

La planificación usa retrospectivamente lluvia observada y límites didácticos. El índice requiere datos de incidencia por lote, variedad y estado del cultivo para una validación agronómica. La aplicación presenta el índice como favorabilidad climática.

## Fuentes

- [NASA POWER Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
- [Cenicafé · Recomendaciones para el manejo de la roya](https://publicaciones.cenicafe.org/index.php/bot/article/view/1326)
- [Cenicafé · Aplicativo de balance hídrico para café](https://publicaciones.cenicafe.org/index.php/avances_tecnicos/article/view/188)
- Las cinco referencias del asistente están atribuidas en [el corpus](data/corpus.json).
