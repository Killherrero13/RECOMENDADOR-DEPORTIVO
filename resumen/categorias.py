"""Categorías verificadas y valores neutrales cuando faltan metadatos."""
import json
import re
import unicodedata
from datetime import datetime
from functools import lru_cache

from .config import ROOT, MADRID_TZ

def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto.casefold())
                   if unicodedata.category(c) != 'Mn')

@lru_cache(maxsize=1)
def catalogo_tenis():
    return json.loads((ROOT/'data/torneos_tenis.json').read_text(encoding='utf-8'))

def categoria_tenis(evento):
    comp = normalizar(evento['competicion'])
    if re.search(r'\b(?:wta|challenger|itf|junior|qualifying|qualy)\b', comp):
        return None, 'Sin categoría ATP principal reconocida'
    for patron, categoria in [(r'\bgrand slam\b', 'Grand Slam'),
                               (r'\b(?:atp\s+)?masters\s+1000\b', 'Masters 1000'),
                               (r'\batp\s*500\b', 'ATP 500'),
                               (r'\batp\s*250\b', 'ATP 250')]:
        if re.search(patron, comp):
            return categoria, 'Categoría publicada por la fuente'
    catalogo = catalogo_tenis()
    temporada = int(evento['fecha'][:4]) if evento.get('fecha') else datetime.now(MADRID_TZ).year
    if temporada == catalogo['temporada']:
        for torneo in catalogo['torneos']:
            if any(re.search(r'(?<!\w)' + re.escape(normalizar(alias)) + r'(?!\w)', comp)
                   for alias in torneo['alias']):
                return torneo['categoria'], f"Categoría verificada en calendario ATP {temporada}"
    return None, 'Categoría no identificada: sin penalización por datos ausentes'

def bonus_categoria_tenis(evento):
    categoria, _ = categoria_tenis(evento)
    return {'Grand Slam':4, 'Masters 1000':3, 'ATP 500':2, 'ATP 250':1}.get(categoria, 0)
