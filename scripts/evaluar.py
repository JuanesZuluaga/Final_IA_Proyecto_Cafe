"""Evaluación reproducible de planificación y protocolo de herramientas."""
from collections import Counter
import argparse
from datetime import date, timedelta
import json
import os
from types import SimpleNamespace as NS

from agente import consultar, PROVEEDORES
from clima import cargar, ventana
from ia_clasica import agendar, LABORES

CASOS = [
    ("¿Cuál es la favorabilidad para roya de esta fecha?", ["risk"], ""),
    ("¿Cuánta lluvia hubo?", ["risk"], ""),
    ("¿Cuál era la humedad relativa?", ["risk"], ""),
    ("¿Cuándo se puede programar la cosecha?", ["schedule"], ""),
    ("¿Qué labores se aplazan con esta cuadrilla?", ["schedule"], ""),
    ("¿Qué día quedó la fertilización en la agenda?", ["schedule"], ""),
    ("¿Qué variedades resistentes recomienda Cenicafé?", ["search_docs"], "variedades resistentes semilla certificada"),
    ("¿Cómo se relaciona balance hídrico con fertilización?", ["search_docs"], "balance hídrico fertilización"),
    ("¿Qué referencias hablan del manejo integrado de roya?", ["search_docs"], "manejo integrado roya susceptibles"),
    ("¿Qué indica el clima y cómo orienta el monitoreo según Cenicafé?", ["risk", "search_docs"], "monitoreo enfermedad roya"),
    ("Dame la agenda y el índice de favorabilidad del escenario.", ["schedule", "risk"], ""),
    ("¿Cuándo quedó la fertilización y qué dice Cenicafé sobre humedad del suelo?", ["schedule", "search_docs"], "humedad suelo fertilización"),
]


class ClienteSimulado:
    def __init__(self, nombres, busqueda):
        self.nombres = nombres
        self.busqueda = busqueda
        self.chat = NS(completions=NS(create=self.responder))

    def responder(self, *, messages, **kwargs):
        if messages[-1]["role"] == "user":
            llamadas = [NS(id=f"llamada_{i}", function=NS(name=n, arguments=json.dumps(
                {"consulta": self.busqueda} if n == "search_docs" else {})))
                for i, n in enumerate(self.nombres)]
            mensaje = NS(content=None, tool_calls=llamadas)
        else:
            docs = [d for m in messages if m["role"] == "tool"
                    for d in json.loads(m["content"]).get("documentos", [])]
            mensaje = NS(content="Simulación de protocolo. " + " ".join(f"[{d['id']}]" for d in docs), tool_calls=[])
        return NS(choices=[NS(message=mensaje)])


def evaluar_csp(datos):
    totales = Counter()
    for serie in datos.values():
        for fecha in sorted(serie):
            fin = (date.fromisoformat(fecha) + timedelta(days=4)).isoformat()
            if fin > max(serie):
                continue
            dias = ventana(serie, fecha, 5)
            for cuadrilla in (1, 2, 3):
                csp, base = (agendar(dias, cuadrilla, base=b) for b in (False, True))
                p, q = csp["prioridad_total"], base["prioridad_total"]
                assert (p, -csp["demora_total"]) >= (q, -base["demora_total"])
                for resultado in (csp, base):
                    por_fecha = Counter()
                    lluvia = {d["fecha"]: d["precipitacion"] for d in dias}
                    for labor, asignacion in zip(LABORES, resultado["labores"]):
                        dia = asignacion["fecha"]
                        if dia is not None:
                            por_fecha[dia] += labor.personas
                            assert lluvia[dia] is not None
                            assert labor.lluvia_max is None or lluvia[dia] <= labor.lluvia_max
                    assert all(n <= cuadrilla for n in por_fecha.values())
                totales.update(escenarios=1, csp=p, base=q, mejora_prioridad=int(p > q),
                               mejora_demora_mismo_puntaje=int(p == q and csp["demora_total"] < base["demora_total"]))
    print(json.dumps(dict(totales), ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", action="store_true", help="Evaluar en vivo con un proveedor LLM.")
    parser.add_argument("--proveedor", default="OpenAI", choices=list(PROVEEDORES),
                        help="Endpoint compatible con OpenAI: OpenAI, Groq o NVIDIA.")
    args = parser.parse_args()
    env_var = PROVEEDORES[args.proveedor][2]
    if args.llm and not os.getenv(env_var):
        parser.error(f"Configura {env_var} para ejecutar las 12 consultas en vivo con {args.proveedor}.")
    datos = cargar()
    evaluar_csp(datos)
    contexto = dict(municipio="Andes", fecha="2024-04-29", serie=datos["Andes"], dias=5, personas=2)
    print(f"Proveedor real: {args.proveedor}" if args.llm
          else "Proveedor simulado: prueba el ciclo, no la selección del LLM.")
    aciertos = 0
    for i, (pregunta, esperadas, busqueda) in enumerate(CASOS, 1):
        respuesta = consultar(pregunta, contexto, api_key=os.getenv(env_var, ""), proveedor=args.proveedor,
                              cliente=None if args.llm else ClienteSimulado(esperadas, busqueda))
        llamadas = {t["herramienta"] for t in respuesta["trazas"] if t["ok"]}
        cita = bool(respuesta["fuentes"])
        ok = not respuesta["error"] and llamadas == set(esperadas) and cita == bool(busqueda)
        aciertos += ok
        print(json.dumps(dict(caso=i, pregunta=pregunta, esperadas=esperadas,
                              llamadas=sorted(llamadas), cita_esperada=bool(busqueda),
                              fuentes=[d["id"] for d in respuesta["fuentes"]], cumple=ok,
                              texto=respuesta["texto"]), ensure_ascii=False))
    print(f"{aciertos}/{len(CASOS)}")
    return 0 if aciertos == len(CASOS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
