"""Colección y selección original, con consulta HTTP independiente de Colab."""
import json
import logging
import random
import time
from datetime import datetime, time as hora_del_dia, timedelta, timezone

import requests

from .config import API_URL, COLECCION, MADRID_TZ

logger = logging.getLogger(__name__)

class ErrorCamisetas(Exception):
    pass

def cargar_coleccion(path=COLECCION):
    try:
        collection = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise ErrorCamisetas('No se pudo leer la colección de camisetas.') from None
    if not isinstance(collection, list) or not collection:
        raise ErrorCamisetas('La colección debe ser una lista no vacía.')
    for shirt in collection:
        if (not isinstance(shirt, dict)
            or not isinstance(shirt.get('Equipo'), str) or not shirt['Equipo'].strip()
            or type(shirt.get('Modelo')) not in (str, int)
            or not isinstance(shirt.get('Jugador'), str)):
            raise ErrorCamisetas('Una entrada de la colección tiene campos inválidos.')
    return collection

def parametros_fecha(fecha):
    # Los filtros son fechas UTC y dateTo es exclusivo. Cubrimos todo el día local.
    inicio = datetime.combine(fecha, hora_del_dia.min, MADRID_TZ).astimezone(timezone.utc)
    fin = datetime.combine(fecha + timedelta(days=1), hora_del_dia.min, MADRID_TZ).astimezone(timezone.utc)
    return {'dateFrom': inicio.date().isoformat(),
            'dateTo': (fin.date() + timedelta(days=1)).isoformat()}

def interpretar_partidos(payload, fecha):
    if not isinstance(payload, dict) or not isinstance(payload.get('matches'), list):
        raise ErrorCamisetas('La API no devolvió una lista de partidos válida.')
    result = []
    for match in payload['matches']:
        try:
            instante = datetime.fromisoformat(match['utcDate'].replace('Z', '+00:00'))
            if instante.tzinfo is None:
                raise ValueError
            local = instante.astimezone(MADRID_TZ)
            if local.date() != fecha:
                continue
            home, away, competition = (match['homeTeam']['name'], match['awayTeam']['name'],
                                        match['competition']['name'])
            if not all(isinstance(v, str) and v.strip() for v in (home, away, competition)):
                raise ValueError
            result.append({'home': home, 'away': away, 'hora': local, 'competition': competition,
                           'status': match.get('status')})
        except (KeyError, TypeError, ValueError, AttributeError):
            raise ErrorCamisetas('La API devolvió un partido con datos incompletos o inválidos.') from None
    return result

def obtener_partidos_hoy(api_key, ahora=None):
    ahora = ahora or datetime.now(MADRID_TZ)
    if ahora.tzinfo is None:
        raise ErrorCamisetas('La fecha de consulta debe incluir zona horaria.')
    fecha = ahora.astimezone(MADRID_TZ).date()
    for intento in range(3):
        try:
            response = requests.get(API_URL, headers={'X-Auth-Token': api_key},
                                    params=parametros_fecha(fecha), timeout=(5, 20),
                                    allow_redirects=False)
        except (requests.Timeout, requests.ConnectionError):
            if intento < 2:
                logger.warning('Consulta de partidos interrumpida; reintento %s/2.', intento + 1)
                time.sleep(2 ** intento)
                continue
            raise ErrorCamisetas('No se pudo conectar con la API tras tres intentos.') from None
        except requests.RequestException:
            raise ErrorCamisetas('Fallo al realizar la consulta de partidos.') from None
        if 500 <= response.status_code <= 599 and intento < 2:
            logger.warning('API de partidos HTTP %s; reintento %s/2.', response.status_code, intento + 1)
            time.sleep(2 ** intento)
            continue
        if response.status_code != 200:
            detail = {401: 'Credencial rechazada.', 403: 'Acceso denegado: revisa la clave y el plan.',
                      429: 'Límite de consultas alcanzado; inténtalo más tarde.'}.get(response.status_code, '')
            raise ErrorCamisetas(f'API de partidos HTTP {response.status_code}. {detail}'.strip())
        try:
            payload = response.json()
        except ValueError:
            raise ErrorCamisetas('La API no devolvió JSON válido.') from None
        matches = interpretar_partidos(payload, fecha)
        logger.info('Consulta correcta: %s partidos para %s en Madrid.', len(matches), fecha)
        return matches

def seleccionar_camiseta(coleccion, partidos, rng=None):
    # Sin pesos, favoritos ni asociación con los partidos: comportamiento original.
    return (rng or random).choices(coleccion, k=1)[0], partidos

def partidos_visibles(partidos, ahora):
    # Conserva el corte original: hasta dos horas desde el inicio, incluidos los futuros.
    return [p for p in partidos if (ahora - p['hora']).total_seconds() / 3600 <= 2]

def generar_resultado(api_key, ahora=None):
    ahora = ahora or datetime.now(MADRID_TZ)
    collection = cargar_coleccion()
    matches = obtener_partidos_hoy(api_key, ahora)
    shirt, matches = seleccionar_camiseta(collection, matches)
    return {'fecha': ahora.astimezone(MADRID_TZ).date().isoformat(), 'camiseta': shirt,
            'partidos': partidos_visibles(matches, ahora)}
