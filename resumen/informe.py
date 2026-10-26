"""Contenido compartido para HTML de correo y texto, sin plantillas externas."""
from pathlib import Path
from .horarios import orden_inicio
from .diseno_correo import crear_html, listado_completo, pagina, nota_texto
from .canales import canal_texto

def linea_evento(event):
    title = ((event.get('descripcion') or event['competicion']) + ' · ' + event['competicion']) if not event.get('local') else f"{event['local']} vs {event['visitante']} · {event['competicion']}"
    hora = event['inicio'].strftime('%d/%m %H:%M') if 'inicio' in event else event['hora']
    canales = ' · '.join(canal_texto(c) for c in event.get('canales') or [event.get('channel') or 'Canal no indicado'])
    texto = f"{hora} · {title} · {canales} · {nota_texto(event)}"
    if event.get('nivel'):
        texto += f" · {event['nivel']}"
    if event.get('desglose'):
        d = event['desglose']
        texto += f" · Interés deportivo {d['deportivo']:.1f} · Afinidad {d['afinidad']:+.1f}"
    if event.get('categoria_reconocida'):
        texto += f" · Categoría: {event['categoria_reconocida']}"
    elif event.get('deporte') == 'Tenis' and 'origen_categoria' in event:
        texto += ' · Categoría por confirmar (sin penalización por datos ausentes)'
    if 'fin_estimado' in event:
        texto += f" · Fin estimado: {event['fin_estimado']:%d/%m %H:%M}"
    if event.get('en_curso'):
        texto += ' · En curso'
    if event.get('vision_parcial'):
        texto += f" · Visionado parcial: hasta {event['fin_vision']:%H:%M}"
    if event.get('madrugada'):
        texto += ' · Opción de madrugada'
    return texto

def contenido(resultado):
    sections = []
    if resultado.get('demostracion'):
        sections.append(('Demostración', ['DATOS FICTICIOS: este ejemplo no es la agenda real de hoy.']))
    if resultado['errores']:
        sections.append(('Avisos de ejecución', [f'{name.capitalize()}: {message}' for name, message in resultado['errores'].items()]))
    shirt = resultado['camiseta']
    if shirt is not None:
        item = shirt['camiseta']
        lines = [describir_camiseta(item)]
        match = shirt.get('partido_asociado')
        if match:
            lines.append(f"Partido: {match['home']} vs {match['away']} · {match['hora']:%d/%m %H:%M} · {match['competition']}")
        else:
            lines.append('Elección al azar, sin partido asociado en los datos disponibles.')
        if shirt.get('motivo'):
            lines.append(shirt['motivo'])
        sections.append(('👕 Camiseta recomendada', lines))
        if shirt.get('recomendada') is not None and shirt.get('aleatoria') is not None:
            sections.append(('👕 Alternativa al azar', [describir_camiseta(shirt['aleatoria'])]))
        # Con agenda disponible, no repetimos la lista de football-data.
        if resultado['eventos'] is None:
            lines = [f"{p['hora']:%H:%M} · {p['home']} vs {p['away']} · {p['competition']}" for p in shirt['partidos']]
            sections.append(('⚽ Partidos del día', lines or ['No hay partidos que cumplan el filtro horario en los datos disponibles.']))
    events = resultado['eventos']
    if events is not None:
        if events.get('avisos'):
            sections.append(('Cobertura de la agenda', events['avisos']))
        plan = events['plan']
        imprescindible = plan.get('imprescindible')
        titulo = ('📺 Día tranquilo' if not imprescindible else
                  '📺 Lo mejor del día' if imprescindible['score'] < 8 else '📺 Imprescindible')
        sections.append((titulo, [linea_evento(imprescindible)] if imprescindible else ['Hoy no hay citas que alcancen el umbral del plan; puedes dejar el día libre.']))
        agenda = [f'{franja.capitalize()}: {linea_evento(e)}' for franja, e in plan.items() if franja != 'imprescindible']
        sections.append(('Plan principal del día', agenda or ['Sin otros eventos en el plan.']))
        sections.append(('Alternativas', [linea_evento(e) for e in events['alternativas']] or ['Sin alternativas que alcancen el umbral.']))
        sections.append(('Información', ['Notas personales sobre diez: interés deportivo y afinidad. El acceso y el horario solo ajustan el encaje en la agenda.',
                         '8–10: cita destacada · 6–7,9: buena opción · 4–5,9: de fondo · menos de 4: prescindible.',
                         'Alternativas ordenadas por interés y encaje. Horarios de Europe/Madrid.',
                         'Los finales y solapamientos se calculan con duraciones estimadas; pueden variar.',
                         'Fuente de la agenda: futbolenlatv.es.']))
        todos = sorted(events.get('filtrados', []), key=orden_inicio)
        sections.append((f'Todos los eventos filtrados ({len(todos)})', [linea_evento(e) for e in todos]
                         or ['No hay eventos que superen los filtros y la disponibilidad.']))
    return sections

def describir_camiseta(item):
    description = item['Equipo']
    if item['Modelo']:
        description += f" · {item['Modelo']}"
    if item['Jugador']:
        description += f" · {item['Jugador']}"
    return description

def generar_informe(resultado):
    year, month, day = resultado['fecha'].split('-')
    subject = f'Resumen diario — {day}/{month}/{year}'
    if resultado.get('demostracion'):
        subject = '[DEMO] ' + subject
    if resultado['errores']:
        subject = '[CON ERRORES] ' + subject
    sections = contenido(resultado)
    plain = subject + '\n\n' + '\n\n'.join(title + '\n' + '\n'.join('- ' + line for line in lines) for title, lines in sections) + '\n'
    todos = sorted((resultado['eventos'] or {}).get('filtrados', []), key=orden_inicio)
    html = crear_html(subject, sections, resultado, todos)
    listado = pagina(f'Todos los eventos filtrados — {day}/{month}/{year}', listado_completo(todos)) if resultado['eventos'] is not None else None
    return {'asunto': subject, 'texto': plain, 'html': html, 'listado_html':listado}

def guardar_informe(informe, carpeta):
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    for nombre, value in [('resumen.html', informe['html']), ('resumen.txt', informe['texto'])]:
        (carpeta / nombre).write_text(value, encoding='utf-8')
    if informe.get('listado_html'):
        (carpeta/'todos_eventos.html').write_text(informe['listado_html'],encoding='utf-8')
