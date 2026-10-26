"""NBA en diferido: la salida pública no contiene marcadores ni notas."""
import json
import math
import time
from datetime import datetime, timedelta, time as hora, timezone
from pathlib import Path

import requests
from .config import MADRID_TZ

URL = 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard'
AFINIDADES = json.loads((Path(__file__).resolve().parents[1] / 'data/afinidades_nba.json').read_text(encoding='utf-8'))


class ErrorNBA(Exception):
    pass


def descargar(dia):
    for intento in range(3):
        try:
            r = requests.get(URL, params={'dates': dia.strftime('%Y%m%d'), 'limit': 100}, timeout=(5, 20))
            if r.status_code == 429 or r.status_code >= 500:
                if intento < 2:
                    time.sleep(2 ** intento)
                    continue
            r.raise_for_status()
            datos = r.json()
            if not isinstance(datos, dict) or not isinstance(datos.get('events'), list):
                raise ErrorNBA('La fuente NBA ha cambiado de formato.')
            return datos['events']
        except (requests.Timeout, requests.ConnectionError):
            if intento < 2:
                time.sleep(2 ** intento)
                continue
            raise ErrorNBA('No se pudo consultar la NBA tras tres intentos.') from None
        except (requests.RequestException, ValueError):
            raise ErrorNBA('No se pudo leer la fuente NBA.') from None


def puntuacion(local, visitante, puntos_local, puntos_visitante):
    diferencia = abs(puntos_local - puntos_visitante)
    competitividad = math.exp(-diferencia / 14)
    gustos = max(0, min(1, .5 + (AFINIDADES.get(local, 0) + AFINIDADES.get(visitante, 0)) / 4))
    favorito = .04 if 'Celtics' in (local, visitante) else 0
    # Sin puntos totales ni clasificación ficticia; escala interna, nunca publicada.
    return min(1, .80 * competitividad + .20 * gustos + favorito)


def categoria_nba(nota):
    return 'Ver completo' if nota >= .74 else 'Resumen' if nota >= .50 else 'Puedes saltártelo'



def evaluar_partidos(partidos, ahora):
    if ahora.tzinfo is None:
        raise ValueError('La fecha NBA debe incluir zona horaria.')
    ahora = ahora.astimezone(MADRID_TZ)
    cierre = datetime.combine(ahora.date(), hora(6, 30), MADRID_TZ)
    inicio = datetime.combine(ahora.date() - timedelta(days=1), hora(6, 30), MADRID_TZ)
    limite = min(ahora, cierre)
    vistos = set()
    salida, pendientes, invalidos = [], 0, 0
    for e in partidos:
        try:
            fecha = datetime.fromisoformat(e['date'].replace('Z', '+00:00'))
            if fecha.tzinfo is None:
                raise ValueError()
            if not inicio <= fecha < cierre or fecha > limite:
                continue
            identificador = str(e['id'])
            if identificador in vistos:
                continue
            vistos.add(identificador)
            if not e['status']['type']['completed']:
                pendientes += 1
                continue
            equipos = e['competitions'][0]['competitors']
            local = next(t for t in equipos if t['homeAway'] == 'home')
            visitante = next(t for t in equipos if t['homeAway'] == 'away')
            puntos = [int(t['score']) for t in (local, visitante)]
            if any(p < 0 for p in puntos) or puntos[0] == puntos[1]:
                raise ValueError()
            nombres = [t['team']['displayName'] for t in (local, visitante)]
            afinidades = [t['team']['name'] for t in (local, visitante)]
            nota = puntuacion(*afinidades, *puntos)
            recomendacion = categoria_nba(nota)
            # Nunca devolver el objeto de la fuente: contiene spoilers incluso en sus enlaces.
            salida.append({'local': nombres[0], 'visitante': nombres[1],
                           'fecha': fecha.astimezone(MADRID_TZ).strftime('%d/%m %H:%M'),
                           'recomendacion': recomendacion})
        except (KeyError, IndexError, TypeError, ValueError, StopIteration, AttributeError):
            invalidos += 1
    # Orden estable por nombres, nunca por margen/nota oculta.
    salida.sort(key=lambda p: (p['local'], p['visitante']))
    avisos = []
    if pendientes:
        avisos.append(f'{pendientes} encuentros iniciados aún sin resultado final confirmado; no se evalúan.')
    if invalidos:
        avisos.append(f'{invalidos} registros no se pudieron validar; cobertura incompleta.')
    if ahora < cierre:
        avisos.append('Consulta antes de las 06:30: la jornada puede seguir en curso y el correo no se actualiza automáticamente.')
    return {'partidos': salida, 'avisos': avisos, 'fuente': 'ESPN',
            'ventana': f'{inicio:%d/%m %H:%M}–{cierre:%d/%m %H:%M} · Madrid',
            'consultado': ahora.strftime('%d/%m %H:%M')}


def generar_nba(ahora=None):
    ahora = ahora or datetime.now(MADRID_TZ)
    if ahora.tzinfo is None:
        raise ValueError('La fecha NBA debe incluir zona horaria.')
    local = ahora.astimezone(MADRID_TZ)
    inicio = datetime.combine(local.date() - timedelta(days=1), hora(6, 30), MADRID_TZ)
    cierre = min(local, datetime.combine(local.date(), hora(6, 30), MADRID_TZ))
    dia = inicio.astimezone(timezone.utc).date()
    ultimo = cierre.astimezone(timezone.utc).date()
    partidos = []
    while dia <= ultimo:
        partidos.extend(descargar(dia))
        dia += timedelta(days=1)
    return evaluar_partidos(partidos, ahora)
