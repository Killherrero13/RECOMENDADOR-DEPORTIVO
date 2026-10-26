"""HTML de correo con tablas de presentación, estilos inline y sin recursos remotos."""
from html import escape
from .canales import plataforma_destacada

FUENTE = 'https://www.futbolenlatv.es/deporte'
ICONOS = {'Fútbol':'⚽', 'Baloncesto':'🏀', 'Tenis':'🎾', 'Automovilismo':'🏁', 'Balonmano':'🤾'}

def texto(valor):
    return escape(str(valor), quote=True)

def etiqueta(valor, color='#eaf0f6', tinta='#3e526b'):
    return f'<span style="display:inline-block;padding:4px 8px;margin:2px 4px 2px 0;border-radius:6px;background:{color};color:{tinta};font-size:12px;line-height:1.4;">{texto(valor)}</span>'

def canales_html(evento):
    badges = []
    for canal in evento.get('canales') or [evento.get('channel') or 'Canal no indicado']:
        plataforma = plataforma_destacada(canal)
        if plataforma == 'DAZN':
            badges.append(etiqueta('✓ ' + canal, '#f3ff27', '#172b43'))
        elif plataforma == 'Movistar Plus+':
            badges.append(etiqueta('✓ ' + canal, '#0072c6', '#ffffff'))
        else:
            badges.append(etiqueta(canal))
    return ' '.join(badges)

def categoria_html(evento):
    if evento.get('categoria_reconocida'):
        return etiqueta(evento['categoria_reconocida'])
    if evento.get('deporte') == 'Tenis' and 'origen_categoria' in evento:
        return etiqueta('Categoría por confirmar', '#fff1db', '#744915')
    return ''

def tarjeta_evento(evento, destacado=False, franja=''):
    tinta = '#ffffff' if destacado else '#172b43'
    secundaria = '#cbd9e8' if destacado else '#60728b'
    fondo = '#132d46' if destacado else '#ffffff'
    icono = ICONOS.get(evento['deporte'], '📺')
    titulo = (evento.get('descripcion') or evento['competicion']) if not evento.get('local') else f"{evento['local']} — {evento['visitante']}"
    fecha = evento['inicio'].strftime('%d/%m') if 'inicio' in evento else evento.get('fecha', '')[5:].replace('-', '/')
    badge = etiqueta(f"{evento['score']:.1f} pts", '#dfae50' if destacado else '#e6f3ec', '#172b43' if destacado else '#1b6948')
    estado = []
    if evento.get('en_curso'):
        estado.append('EN CURSO')
    if evento.get('madrugada'):
        estado.append('MADRUGADA')
    if evento.get('vision_parcial'):
        estado.append(f"Ver hasta {evento['fin_vision']:%H:%M} · parcial")
    fin = f"Fin estimado {evento['fin_estimado']:%d/%m %H:%M}" if 'fin_estimado' in evento else ''
    label = 'TU IMPRESCINDIBLE' if destacado else franja.upper()
    return (f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="table-layout:fixed;background:{fondo};border:1px solid #dce5ef;border-radius:14px;margin-bottom:12px;">'
            f'<tr><td style="padding:20px;">'
            + (f'<p style="margin:0 0 14px;color:{secundaria};font-size:11px;font-weight:bold;letter-spacing:1.8px;">{texto(label)}</p>' if label else '')
            + '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="table-layout:fixed;"><tr>'
            f'<td width="74" valign="top" style="padding-right:14px;color:{tinta};">'
            f'<div style="font-size:27px;font-weight:bold;line-height:1.2;white-space:nowrap;">{texto(evento["hora"])}</div>'
            f'<div style="margin-top:5px;font-size:12px;color:{secundaria};">{texto(fecha)}</div></td>'
            f'<td valign="top" style="color:{tinta};overflow-wrap:anywhere;">'
            f'<div style="font-size:12px;color:{secundaria};margin-bottom:7px;">{icono} {texto(evento["deporte"])}</div>'
            f'<div style="font-size:20px;font-weight:bold;line-height:1.35;">{texto(titulo)}</div>'
            f'<div style="font-size:13px;line-height:1.5;color:{secundaria};margin-top:7px;">{texto(evento["competicion"])}</div>'
            f'<div style="margin-top:10px;">{categoria_html(evento)} {badge}</div></td></tr></table>'
            f'<p style="color:{tinta};font-size:13px;line-height:1.6;margin:16px 0 0;padding-top:12px;border-top:1px solid {"#3c536b" if destacado else "#edf1f5"};">'
            f'<strong>TV</strong><br>{canales_html(evento)}</p>'
            + (f'<p style="font-size:12px;line-height:1.6;color:{secundaria};margin:8px 0 0;">{texto(" · ".join([s for s in [fin, *estado] if s]))}</p>' if fin or estado else '')
            + '</td></tr></table>')

def listado_completo(eventos):
    filas = []
    for e in eventos:
        fecha = e['inicio'].strftime('%d/%m') if 'inicio' in e else e.get('fecha', '')
        nombre = (e.get('descripcion') or e['competicion']) if not e.get('local') else f"{e['local']} — {e['visitante']}"
        filas.append('<tr class="evento-filtrado">'
                     f'<td width="68" valign="top" style="padding:13px 8px 13px 0;border-bottom:1px solid #e4eaf1;white-space:nowrap;"><strong>{texto(e["hora"])}</strong><br><span style="font-size:11px;color:#64748b;">{texto(fecha)}</span></td>'
                     '<td valign="top" style="padding:13px 0;border-bottom:1px solid #e4eaf1;overflow-wrap:anywhere;">'
                     f'<strong style="font-size:14px;">{texto(nombre)}</strong><br>'
                     f'<span style="font-size:12px;color:#52647a;">{texto(e["deporte"])} · {texto(e["competicion"])}</span><br>'
                     f'<span style="font-size:12px;line-height:1.6;">{canales_html(e)}</span><br>'
                     f'<span style="font-size:11px;color:#1b6948;">{e["score"]:.1f} puntos</span> {categoria_html(e)}'
                     + (f'<br><span style="font-size:11px;color:#8a5217;">Visionado parcial hasta {e["fin_vision"]:%H:%M}</span>' if e.get('vision_parcial') else '')
                     + ('<br><span style="font-size:11px;color:#8a5217;">En curso</span>' if e.get('en_curso') else '')
                     + '</td></tr>')
    return ('<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="color:#172b43;">'
            + ''.join(filas) + '</table>' if filas else '<p>No hay eventos que superen los filtros y la disponibilidad.</p>')

def pagina(asunto, cuerpo):
    return ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{texto(asunto)}</title></head>'
            '<body style="margin:0;padding:0;background:#edf2f7;font-family:Arial,Helvetica,sans-serif;color:#172b43;overflow-wrap:anywhere;word-break:break-word;">'
            '<div style="max-width:640px;margin:0 auto;padding:20px 12px;overflow-wrap:anywhere;word-break:break-word;">'
            '<p style="margin:8px 0;color:#52647a;font-size:11px;font-weight:bold;letter-spacing:2px;">TU DÍA DE DEPORTE</p>'
            f'<h1 style="font-size:27px;line-height:1.3;margin:10px 0 22px;">{texto(asunto)}</h1>'
            + cuerpo + f'<p style="font-size:12px;line-height:1.7;color:#61718a;margin:24px 0;">Horarios de Madrid · '
            f'<a href="{FUENTE}" style="color:#1b6948;">Consultar la agenda de origen</a><br>'
            '✓ Plataformas destacadas según tu acceso: DAZN y canal Movistar Plus+.<br>'
            'Otros canales M+ pueden requerir un paquete diferente.</p>'
            '</div></body></html>')

def crear_html(asunto, secciones, resultado, todos):
    events = resultado['eventos']
    bloques = []
    if events is not None:
        bloques.append(f'<p style="margin:0 0 22px;">{etiqueta(str(len(events.get("seleccionados", []))) + " en tu plan")}{etiqueta(str(len(todos)) + " eventos filtrados")}{etiqueta("EUROPE / MADRID")}</p>')
    for titulo, lineas in secciones:
        if titulo == '📺 Imprescindible' and events['plan'].get('imprescindible'):
            bloques.append(tarjeta_evento(events['plan']['imprescindible'], True))
        elif titulo == 'Plan principal del día' and events['plan']:
            bloques.append('<h2 style="font-size:19px;margin:26px 0 14px;">Tu plan del día</h2>')
            for franja, e in events['plan'].items():
                if franja != 'imprescindible':bloques.append(tarjeta_evento(e,franja=franja))
            if len(events['plan']) == 1:bloques.append('<p style="color:#64748b;">Sin otros eventos compatibles en el plan.</p>')
        elif titulo == 'Alternativas' and events['alternativas']:
            bloques.append('<h2 style="font-size:19px;margin:26px 0 14px;">Otras buenas opciones</h2>')
            bloques.extend(tarjeta_evento(e) for e in events['alternativas'])
        elif titulo.startswith('Todos los eventos filtrados'):
            bloques.append(f'<div style="margin:26px 0;padding:20px;border-radius:14px;background:#e0eee7;"><h2 style="font-size:19px;margin:0 0 10px;">¿Quieres más opciones?</h2>'
                           f'<a href="#todos-eventos" style="display:inline-block;background:#1b6948;color:#ffffff;text-decoration:none;padding:13px 16px;border-radius:8px;font-size:14px;font-weight:bold;">Ver los {len(todos)} eventos filtrados ↓</a>'
                           '<p style="font-size:12px;line-height:1.6;margin:12px 0 0;">Listado completo a continuación, también adjunto como todos_eventos.html.</p></div>'
                           f'<div id="todos-eventos" style="padding:20px;background:#ffffff;border:1px solid #dce5ef;border-radius:14px;"><h2 style="font-size:19px;margin:0 0 8px;">{texto(titulo)}</h2>'
                           '<p style="font-size:12px;color:#61718a;line-height:1.6;">Orden cronológico. Incluye todos los que pasan tus filtros y disponibilidad, aunque su puntuación no alcance el plan.</p>'
                           + listado_completo(todos) + '</div>')
        else:
            jersey = titulo.startswith('👕')
            aviso = titulo in ('Avisos de ejecución','Cobertura de la agenda','Demostración')
            fondo = '#fff5e6' if aviso else '#ffffff'
            cuerpo = ''.join(f'<p style="margin:8px 0;line-height:1.65;font-size:{"20" if jersey and i == 0 else "13"}px;{"font-weight:bold;" if jersey and i == 0 else "color:#52647a;"}">{texto(l)}</p>' for i,l in enumerate(lineas))
            bloques.append(f'<div style="background:{fondo};padding:20px;margin-bottom:14px;border:1px solid #dce5ef;border-radius:14px;'
                           + ('border-left:5px solid #dfae50;' if jersey else '') + f'"><h2 style="font-size:15px;margin:0 0 12px;">{texto(titulo)}</h2>{cuerpo}</div>')
    return pagina(asunto,''.join(bloques))
