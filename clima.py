"""Histórico diario de puntos de referencia, sin acceso a red en la app."""
import csv
from datetime import date, timedelta
from pathlib import Path

PUNTOS = {"Andes": (5.66, -75.88), "Urrao": (6.32, -76.13)}
ARCHIVO = Path(__file__).parent / "data" / "clima_historico.csv"
FUENTE = "https://power.larc.nasa.gov/docs/services/api/temporal/daily/"


def cargar():
    datos = {p: {} for p in PUNTOS}
    with ARCHIVO.open(encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            punto, dia = fila.pop("municipio"), fila.pop("fecha")
            datos[punto][dia] = {"fecha": dia, **{k: float(v) for k, v in fila.items()}}
    return datos


def ventana(serie, fecha, dias):
    inicio = date.fromisoformat(fecha)
    return [
        serie.get(dia, {"fecha": dia, "precipitacion": None})
        for dia in ((inicio + timedelta(days=i)).isoformat() for i in range(dias))
    ]
