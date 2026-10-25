"""Envío Gmail por SMTP_SSL, con texto y HTML en un único mensaje."""
import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

from .config import obtener_config_correo

logger = logging.getLogger(__name__)

class ErrorCorreo(Exception):
    pass

def crear_mensaje(informe, config):
    mensaje = EmailMessage()
    mensaje['Subject'] = informe['asunto']
    mensaje['From'] = config.remitente
    mensaje['To'] = config.destinatario
    mensaje['Date'] = formatdate(localtime=False)
    mensaje['Message-ID'] = make_msgid()
    mensaje.set_content(informe['texto'], charset='utf-8')
    mensaje.add_alternative(informe['html'], subtype='html', charset='utf-8')
    return mensaje

def enviar_informe(informe):
    config = obtener_config_correo()
    mensaje = crear_mensaje(informe, config)
    aceptado = False
    try:
        # Sin reintentos: si la conexión cae tras entregar DATA, repetir podría duplicar el correo.
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30,
                              context=ssl.create_default_context()) as smtp:
            smtp.login(config.usuario, config.password)
            rechazados = smtp.send_message(mensaje, from_addr=config.remitente,
                                            to_addrs=[config.destinatario])
            if rechazados:
                raise ErrorCorreo('Gmail rechazó el destinatario del correo.')
            # QUIT puede fallar después de que Gmail haya aceptado el mensaje.
            aceptado = True
    except smtplib.SMTPAuthenticationError:
        raise ErrorCorreo('Gmail rechazó la autenticación. Revisa el usuario y la contraseña de aplicación.') from None
    except smtplib.SMTPRecipientsRefused:
        raise ErrorCorreo('Gmail rechazó el destinatario del correo.') from None
    except smtplib.SMTPException:
        if not aceptado:
            raise ErrorCorreo('Fallo SMTP. No se reintentó el envío para evitar duplicados; comprueba la bandeja de entrada antes de repetir.') from None
    except OSError:
        if not aceptado:
            raise ErrorCorreo('Fallo de conexión segura con Gmail. No se reintentó el envío; comprueba la bandeja de entrada antes de repetir.') from None
    logger.info('Gmail ha aceptado el correo para su entrega.')
