import os
from dataclasses import dataclass, field
from email.headerregistry import Address
from email.errors import HeaderParseError
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
MADRID_TZ = ZoneInfo('Europe/Madrid')
COLECCION = ROOT / 'data/camisetas.json'
API_URL = 'https://api.football-data.org/v4/matches'

class ErrorConfiguracion(Exception):
    pass

def obtener_api_key():
    value = os.environ.get('FOOTBALL_API_KEY', '').strip()
    if not value:
        raise ErrorConfiguracion('Falta la variable de entorno FOOTBALL_API_KEY.')
    return value

@dataclass(frozen=True)
class ConfigCorreo:
    usuario: str
    password: str = field(repr=False)
    remitente: str
    destinatario: str

def obtener_config_correo():
    def obligatorio(nombre):
        value = os.environ.get(nombre, '').strip()
        if not value:
            raise ErrorConfiguracion(f'Falta la variable de entorno {nombre}.')
        return value

    usuario = obligatorio('SMTP_USERNAME')
    password = obligatorio('SMTP_PASSWORD').replace(' ', '')
    remitente = os.environ.get('EMAIL_FROM', '').strip() or usuario
    destinatario = obligatorio('EMAIL_TO')
    for nombre, valor in [('SMTP_USERNAME', usuario), ('EMAIL_FROM', remitente), ('EMAIL_TO', destinatario)]:
        try:
            address = Address(addr_spec=valor)
            if not address.username or not address.domain or any(c in valor for c in '\r\n'):
                raise ValueError
            valor.encode('ascii')
        except (ValueError, IndexError, UnicodeError, HeaderParseError):
            raise ErrorConfiguracion(f'{nombre} debe contener una única dirección de email válida.') from None
    # Evita suplantaciones y rechazos por alias no configurados en Gmail.
    if remitente.casefold() != usuario.casefold():
        raise ErrorConfiguracion('Para Gmail, EMAIL_FROM debe coincidir con SMTP_USERNAME.')
    if not password or any(c in password for c in '\r\n'):
        raise ErrorConfiguracion('SMTP_PASSWORD no es válida.')
    return ConfigCorreo(usuario, password, remitente, destinatario)
