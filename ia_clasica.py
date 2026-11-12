"""Red de juicio experto y CSP implementados con Python estándar."""
from dataclasses import dataclass

# P(ambiente húmedo | HR alta, lluvia), en ese orden.
HUMECTACION = {(False, False): .10, (False, True): .65,
               (True, False): .60, (True, True): .95}
# P(ambiente favorable | temperatura compatible, ambiente húmedo).
FAVORABLE = {(False, False): .05, (False, True): .25,
             (True, False): .15, (True, True): .85}


def riesgo(dia):
    compatible = 18 <= dia["temperatura"] <= 25
    humeda = HUMECTACION[dia["humedad"] >= 85, dia["precipitacion"] >= 2]
    indice = (1 - humeda) * FAVORABLE[compatible, False] + humeda * FAVORABLE[compatible, True]
    return {"nivel": "alto" if indice >= .65 else "medio" if indice >= .35 else "bajo",
            "indice": round(indice, 3), "clima": dia,
            "interpretacion": "Favorabilidad climática de un modelo didáctico sin calibrar. No estima incidencia ni diagnostica roya."}


@dataclass(frozen=True)
class Labor:
    nombre: str
    personas: int
    lluvia_max: float | None
    prioridad: int


LABORES = (
    Labor("Cosecha", 2, 4, 5),
    Labor("Monitoreo de roya", 1, 8, 4),
    Labor("Fertilización", 2, 6, 3),
    Labor("Mantenimiento bajo techo", 1, None, 1),
)


def agendar(dias, cuadrilla, *, base=False):
    """Una fecha o aplazamiento por labor; capacidad se reinicia cada día."""
    capacidad = [cuadrilla] * len(dias)
    dominios = [
        [i for i, d in enumerate(dias) if d["precipitacion"] is not None
         and cuadrilla >= labor.personas
         and (labor.lluvia_max is None or d["precipitacion"] <= labor.lluvia_max)]
        for labor in LABORES
    ]
    mejor, solucion = (-1, 0), ()

    def buscar(asignacion, puntos, demora):
        nonlocal mejor, solucion
        i = len(asignacion)
        if i == len(LABORES):
            objetivo = (puntos, -demora)
            if objetivo > mejor:
                mejor, solucion = objetivo, asignacion
            return
        if puntos + sum(l.prioridad for l in LABORES[i:]) < mejor[0]:
            return
        labor = LABORES[i]
        for j in dominios[i]:
            if capacidad[j] >= labor.personas:
                capacidad[j] -= labor.personas
                buscar(asignacion + (j,), puntos + labor.prioridad, demora + j)
                capacidad[j] += labor.personas
                if base:
                    return
        buscar(asignacion + (None,), puntos, demora)

    buscar((), 0, 0)
    return {"prioridad_total": mejor[0], "demora_total": -mejor[1],
            "labores": [{"labor": l.nombre, "fecha": dias[j]["fecha"] if j is not None else None,
                         "personas": l.personas, "limite_mm_demo": l.lluvia_max}
                        for l, j in zip(LABORES, solucion)]}
