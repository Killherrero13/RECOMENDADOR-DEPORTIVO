"""Plataformas destacadas según el acceso declarado por el usuario."""
import re

def plataforma_destacada(canal):
    nombre = ' '.join(canal.casefold().split())
    if re.match(r'^dazn\b', nombre):
        return 'DAZN'
    # Solo el canal general. M+ LALIGA, Deportes, Vamos, etc. no equivalen a él.
    if re.match(r'^movistar\s*(?:plus\s*\+?|\+)(?=\s*(?:$|\(|:))', nombre):
        return 'Movistar Plus+'
    return None

def canal_texto(canal):
    return ('✓ ' if plataforma_destacada(canal) else '') + canal
