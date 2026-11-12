"""Regenera el CSV de 2024 desde NASA POWER: python -m scripts.descargar_clima."""
import csv
import io
import json
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen

from clima import ARCHIVO, PUNTOS

CAMPOS = {"T2M": "temperatura", "RH2M": "humedad", "PRECTOTCORR": "precipitacion"}


def main():
    salida = io.StringIO(newline="")
    writer = csv.writer(salida, lineterminator="\n")
    writer.writerow(["municipio", "fecha", *CAMPOS.values()])
    for punto, (lat, lon) in PUNTOS.items():
        parametros = urlencode(dict(parameters=",".join(CAMPOS), community="AG",
                                     longitude=lon, latitude=lat, start=20240101,
                                     end=20241231, format="JSON"))
        with urlopen("https://power.larc.nasa.gov/api/temporal/daily/point?" + parametros,
                     timeout=30) as respuesta:
            datos = json.load(respuesta)
        valores = datos["properties"]["parameter"]
        faltante = datos["header"]["fill_value"]
        cuenta = 0
        for clave in sorted(valores["T2M"]):
            t, h, p = [valores[k].get(clave) for k in CAMPOS]
            if None in (t, h, p) or faltante in (t, h, p):
                continue
            if not (-60 <= t <= 60 and 0 <= h <= 100 and p >= 0):
                raise ValueError(f"Valor fuera de rango: {punto}, {clave}")
            writer.writerow([punto, datetime.strptime(clave, "%Y%m%d").date(), t, h, p])
            cuenta += 1
        if not cuenta:
            raise ValueError(f"Sin días completos para {punto}")
        print(f"{punto}: {cuenta} días completos")
    ARCHIVO.write_text(salida.getvalue(), encoding="utf-8")


if __name__ == "__main__":
    main()
