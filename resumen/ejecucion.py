"""Coordina fuentes independientes y conserva los fallos parciales."""
import logging
from datetime import datetime

from .camisetas import ErrorCamisetas, generar_resultado, cargar_coleccion
from .seleccion_camisetas import recomendar_camisetas
from .config import ErrorConfiguracion, MADRID_TZ, obtener_api_key
from .fuente_eventos import ErrorEventos, generar_resultado_eventos

logger = logging.getLogger(__name__)

def ejecutar(modo='ambos', ahora=None):
    if modo not in ('ambos', 'camiseta', 'eventos'):
        raise ValueError('Modo desconocido.')
    ahora = ahora or datetime.now(MADRID_TZ)
    if ahora.tzinfo is None:
        raise ValueError('La fecha debe incluir zona horaria.')
    result = {'fecha': ahora.astimezone(MADRID_TZ).date().isoformat(), 'modo': modo,
              'camiseta': None, 'eventos': None, 'errores': {}, 'demostracion': False}
    for nombre in ('camiseta', 'eventos'):
        if modo not in ('ambos', nombre):
            continue
        try:
            result[nombre] = (generar_resultado(obtener_api_key(), ahora) if nombre == 'camiseta'
                              else generar_resultado_eventos(ahora))
        except (ErrorConfiguracion, ErrorCamisetas, ErrorEventos) as error:
            result['errores'][nombre] = str(error)
            logger.error('%s: %s', nombre, error)
        except Exception as error:
            mensaje = f'Error inesperado en {nombre}; revisa el proceso y sus datos.'
            result['errores'][nombre] = mensaje
            # No se muestra el detalle: podría contener credenciales.
            logger.error('%s (%s).', mensaje, type(error).__name__)
    if modo in ('ambos', 'camiseta'):
        try:
            base = result['camiseta'] or {'fecha':result['fecha'], 'partidos':[]}
            agenda = result['eventos'] or {}
            eventos = agenda.get('eventos_disponibles', agenda.get('filtrados', []))
            seleccion = recomendar_camisetas(cargar_coleccion(), base['partidos'], eventos,
                                             ahora.astimezone(MADRID_TZ))
            result['camiseta'] = {**base, **seleccion}
            if 'camiseta' in result['errores']:
                result['camiseta']['motivo'] += ' La consulta de partidos falló; la cobertura puede ser incompleta.'
        except ErrorCamisetas as error:
            result['camiseta'] = None
            result['errores']['camiseta'] = str(error)
            logger.error('camiseta: %s', error)
    return result
