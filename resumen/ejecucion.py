"""Coordina fuentes independientes y conserva los fallos parciales."""
import logging
from datetime import datetime

from .camisetas import ErrorCamisetas, generar_resultado
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
    return result
