"""Recuperación local con similitud coseno TF-IDF, sin servicios de embeddings."""
from collections import Counter
import json
from math import log, sqrt
from pathlib import Path
import re
import unicodedata

CORPUS = json.loads((Path(__file__).parent / "data/corpus.json").read_text(encoding="utf-8"))
STOP = set("que cual como para con por del las los una unos que esto esta del hay debo puedo segun sobre mas me mi el la al es en de y o un se a".split())


def tokens(texto):
    plano = unicodedata.normalize("NFKD", texto.lower())
    plano = "".join(c for c in plano if not unicodedata.combining(c))
    return [w for w in re.findall("[a-z0-9]+", plano) if len(w) > 2 and w not in STOP]


BOLSAS = [Counter(tokens(d["titulo"] + " " + d["texto"])) for d in CORPUS]
IDF = {w: 1 + log((1 + len(CORPUS)) / (1 + sum(w in b for b in BOLSAS)))
       for w in set().union(*BOLSAS)}


def vector(bolsa):
    return {w: n * IDF[w] for w, n in bolsa.items() if w in IDF}


def norma(v):
    return sqrt(sum(x * x for x in v.values()))


VECTORES = [vector(b) for b in BOLSAS]


def buscar(consulta):
    q = vector(Counter(tokens(consulta)))
    if not q:
        return []
    scores = [sum(q.get(w, 0) * v[w] for w in v) / (norma(q) * norma(v))
              for v in VECTORES]
    return [CORPUS[i] for i in sorted(range(len(scores)), key=scores.__getitem__, reverse=True)[:2]
            if scores[i] >= .08]
