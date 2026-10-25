"""Camiseta por evento y alternativa aleatoria, sin historial ni servicios nuevos."""
import json
import random
import re
from datetime import datetime

from .config import ROOT, MADRID_TZ
from .eventos import calculate_score, normalize_team_name
from .camisetas import ErrorCamisetas

def cargar_alias():
    try:
        aliases = json.loads((ROOT/'data/alias_camisetas.json').read_text(encoding='utf-8'))
        if not isinstance(aliases, dict) or not all(isinstance(k,str) and isinstance(v,str) for k,v in aliases.items()):
            raise ValueError
    except (OSError, ValueError):
        raise ErrorCamisetas('No se pudo leer el mapa de nombres de camisetas.') from None
    return {normalize_team_name(k):normalize_team_name(v) for k,v in aliases.items()}

def recomendar_camisetas(coleccion, partidos, eventos, ahora, rng=None):
    rng = rng or random
    aliases = cargar_alias()
    def identidad(nombre):
        normal = normalize_team_name(nombre)
        if normal in aliases:
            return aliases[normal]
        normal = re.sub(r'^(?:fc|cf|afc|sc|ac)\s+|\s+(?:fc|cf|afc|sc|ac)$', '', normal)
        normal = normalize_team_name(normal)
        return aliases.get(normal, normal)
    favoritos = {identidad('Atlético de Madrid'), identidad('Aston Villa')}
    candidates = []
    for fuente, items in [('agenda', eventos), ('football-data', partidos)]:
        for e in items:
            if e.get('status') in {'CANCELLED', 'POSTPONED', 'SUSPENDED'}:
                continue
            if fuente == 'agenda':
                if e.get('deporte') != 'Fútbol':
                    continue
                try:
                    inicio = e.get('inicio') or datetime.fromisoformat(f"{e.get('fecha', ahora.date().isoformat())}T{e['hora']}").replace(tzinfo=MADRID_TZ)
                except (ValueError, TypeError):
                    continue
                home, away, comp = e['local'], e['visitante'], e['competicion']
                score = e.get('score')
                if score is None:
                    score = calculate_score(e)
            else:
                inicio = e['hora']
                home, away, comp = e['home'], e['away'], e['competition']
                score = calculate_score({'hora':inicio.strftime('%H:%M'), 'deporte':'Fútbol',
                                         'competicion':comp, 'local':home, 'visitante':away, 'canales':[]})
            # La camiseta es para hoy: excluye mañana y partidos empezados hace más de dos horas.
            if inicio.astimezone(MADRID_TZ).date() != ahora.date() or ahora.timestamp() - inicio.timestamp() > 7200:
                continue
            for equipo in {identidad(home), identidad(away)}:
                prendas = [shirt for shirt in coleccion if identidad(shirt['Equipo']) == equipo]
                if prendas:
                    asociado = {'home':home, 'away':away, 'hora':inicio, 'competition':comp, 'fuente':fuente}
                    candidates.append(((equipo not in favoritos, -score, inicio.timestamp(), equipo), prendas, asociado))
    recomendada = asociado = None
    motivo = 'No hay coincidencias con los partidos disponibles de hoy; elección al azar.'
    if candidates:
        _, opciones, asociado = min(candidates, key=lambda c:c[0])
        recomendada = rng.choice(opciones)
        motivo = ('Juega uno de tus equipos favoritos.' if identidad(recomendada['Equipo']) in favoritos
                  else 'Tu colección incluye una camiseta de este partido.')
        distintas = [shirt for shirt in coleccion if identidad(shirt['Equipo']) != identidad(recomendada['Equipo'])]
        opciones_azar = distintas or [shirt for shirt in coleccion if shirt != recomendada]
    else:
        opciones_azar = coleccion
    aleatoria = rng.choice(opciones_azar) if opciones_azar else None
    return {'camiseta': recomendada or aleatoria, 'recomendada':recomendada,
            'aleatoria':aleatoria, 'partido_asociado':asociado, 'motivo':motivo}
