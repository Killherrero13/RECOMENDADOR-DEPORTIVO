"""Contenido compartido para HTML de correo y texto, sin plantillas externas."""
from html import escape
from pathlib import Path

def linea_evento(event):
    title = event['competicion'] if event['deporte'] == 'Automovilismo' else f"{event['local']} vs {event['visitante']} · {event['competicion']}"
    return f"{event['hora']} · {title} · {event.get('channel') or 'Sin canal preferido'} · {event['score']:.1f} puntos"

def contenido(resultado):
    sections = []
    if resultado.get('demostracion'):
        sections.append(('Demostración', ['DATOS FICTICIOS: este ejemplo no es la agenda real de hoy.']))
    if resultado['errores']:
        sections.append(('Avisos de ejecución', [f'{name.capitalize()}: {message}' for name, message in resultado['errores'].items()]))
    shirt = resultado['camiseta']
    if shirt is not None:
        item = shirt['camiseta']
        description = item['Equipo']
        if item['Modelo']:
            description += f" · {item['Modelo']}"
        if item['Jugador']:
            description += f" · {item['Jugador']}"
        sections.append(('👕 Camiseta recomendada', [description,
                         'Partido asociado: sin asociación; la selección actual es aleatoria.']))
        # Con agenda disponible, no repetimos la lista de football-data.
        if resultado['eventos'] is None:
            lines = [f"{p['hora']:%H:%M} · {p['home']} vs {p['away']} · {p['competition']}" for p in shirt['partidos']]
            sections.append(('⚽ Partidos del día', lines or ['No hay partidos que cumplan el filtro horario en los datos disponibles.']))
    events = resultado['eventos']
    if events is not None:
        plan = events['plan']
        imprescindible = plan.get('imprescindible')
        sections.append(('📺 Imprescindible', [linea_evento(imprescindible)] if imprescindible else ['Ningún evento alcanza el umbral del plan.']))
        agenda = [f'{franja.capitalize()}: {linea_evento(e)}' for franja, e in plan.items() if franja != 'imprescindible']
        sections.append(('Plan principal del día', agenda or ['Sin otros eventos en el plan.']))
        sections.append(('Alternativas', [linea_evento(e) for e in events['alternativas']] or ['Sin alternativas que alcancen el umbral.']))
        sections.append(('Información', ['Alternativas en el orden original por hora. Horarios de Europe/Madrid.', 'Fuente de la agenda: futbolenlatv.es.']))
    return sections

def generar_informe(resultado):
    year, month, day = resultado['fecha'].split('-')
    subject = f'Resumen diario — {day}/{month}/{year}'
    if resultado.get('demostracion'):
        subject = '[DEMO] ' + subject
    if resultado['errores']:
        subject = '[CON ERRORES] ' + subject
    sections = contenido(resultado)
    plain = subject + '\n\n' + '\n\n'.join(title + '\n' + '\n'.join('- ' + line for line in lines) for title, lines in sections) + '\n'
    cards = []
    for title, lines in sections:
        color = '#fff5e6' if title == 'Avisos de ejecución' else '#ffffff'
        items = ''.join(f'<p style="margin:10px 0;line-height:1.65;overflow-wrap:anywhere;">{escape(line)}</p>' for line in lines)
        cards.append(f'<div style="background:{color};border:1px solid #dfe5ed;border-radius:12px;padding:18px;margin:0 0 16px;">'
                     f'<h2 style="font-size:18px;margin:0 0 12px;color:#152b46;">{escape(title)}</h2>{items}</div>')
    html = ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{escape(subject)}</title></head>'
            '<body style="margin:0;background:#f3f6fa;color:#243247;font:16px Arial,sans-serif;">'
            '<div style="max-width:620px;margin:auto;padding:24px 14px;">'
            '<p style="font-size:12px;letter-spacing:2px;color:#53657e;">TU DÍA DE DEPORTE</p>'
            f'<h1 style="font-size:26px;line-height:1.3;margin:8px 0 24px;">{escape(subject)}</h1>'
            + ''.join(cards) + '<p style="font-size:12px;color:#53657e;">Resumen deportivo personal</p></div></body></html>')
    return {'asunto': subject, 'texto': plain, 'html': html}

def guardar_informe(informe, carpeta):
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    for nombre, value in [('resumen.html', informe['html']), ('resumen.txt', informe['texto'])]:
        (carpeta / nombre).write_text(value, encoding='utf-8')
