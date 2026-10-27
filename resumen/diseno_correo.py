"""HTML de correo con tablas de presentación, estilos inline y sin recursos remotos."""
from html import escape
from .colores import tema_evento
from .explicaciones import frases_explicacion
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

def nota_texto(evento):
    return f"{evento['score']:.1f}/10" if evento.get('escala') else f"{evento['score']:.1f} pts"

def desglose_html(evento):
    d = evento.get('desglose')
    if not d:return ''
    return (f'<div style="font-size:12px;line-height:1.6;margin-top:8px;">'
            f'Interés deportivo {d["deportivo"]:.1f} · Afinidad {d["afinidad"]:+.1f}</div>')

def explicacion_html(evento):
    frases = frases_explicacion(evento)
    if not frases:
        return ''
    return ('<div style="margin-top:12px;font-size:12px;line-height:1.65;">'
            '<strong>Por qué te lo proponemos</strong><br>'
            + '<br>'.join('• ' + texto(f) for f in frases) + '</div>')


def distintivo_nba(recomendacion):
    estilos = {
        'Ver completo': ('▶', '#14613b', '#ffffff'),
        'Resumen': ('▷', '#ffd268', '#352600'),
        'Puedes saltártelo': ('—', '#e4e8ee', '#414d5e'),
    }
    icono, fondo, tinta = estilos.get(recomendacion, ('•', '#e4e8ee', '#414d5e'))
    return (f'<div class="decision-nba" style="padding:12px 14px;border-radius:8px;'
            f'background:{fondo};color:{tinta};font-size:16px;line-height:1.4;font-weight:bold;">'
            f'{icono} {texto(recomendacion.upper())}</div>')


def tarjeta_evento(evento, destacado=False, franja=''):
    fondo, acento, identidad = tema_evento(evento)
    if destacado:
        fondo = '#132d46'
    tinta = '#ffffff' if destacado else '#172b43'
    secundaria = '#cbd9e8' if destacado else '#43536b'
    borde = '3px solid #c89b36' if destacado else f'1px solid {acento}'
    icono = ICONOS.get(evento['deporte'], '📺')
    titulo = (evento.get('descripcion') or evento['competicion']) if not evento.get('local') else f"{evento['local']} — {evento['visitante']}"
    fecha = evento['inicio'].strftime('%d/%m') if 'inicio' in evento else evento.get('fecha', '')[5:].replace('-', '/')
    badge = etiqueta(nota_texto(evento), '#dfae50' if destacado else '#e6f3ec', '#172b43' if destacado else '#1b6948')
    if evento.get('nivel'):badge += etiqueta(evento['nivel'])
    estado = []
    if evento.get('en_curso'):
        estado.append('EN CURSO')
    if evento.get('madrugada'):
        estado.append('MADRUGADA')
    if evento.get('vision_parcial'):
        estado.append(f"Ver hasta {evento['fin_vision']:%H:%M} · parcial")
    fin = f"Fin estimado {evento['fin_estimado']:%d/%m %H:%M}" if 'fin_estimado' in evento else ''
    label = ('TU IMPRESCINDIBLE' if evento['score'] >= 8 else 'LO MEJOR DEL DÍA') if destacado else franja.upper()
    return (f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="table-layout:fixed;background:{fondo};border:{borde};border-radius:14px;margin-bottom:12px;">'
            f'<tr><td style="padding:20px;">'
            + (f'<p style="margin:0 0 14px;color:{secundaria};font-size:11px;font-weight:bold;letter-spacing:1.8px;">{texto(label)}</p>' if label else '')
            + '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="table-layout:fixed;"><tr>'
            f'<td width="74" valign="top" style="padding:0 12px;text-align:center;color:{tinta};">'
            f'<div style="font-size:27px;font-weight:bold;line-height:1.2;white-space:nowrap;">{texto(evento["hora"])}</div>'
            f'<div style="margin-top:5px;font-size:12px;color:{secundaria};">{texto(fecha)}</div></td>'
            f'<td valign="top" style="color:{tinta};overflow-wrap:anywhere;">'
            f'<div style="font-size:12px;color:{secundaria};margin-bottom:7px;">{icono} {texto(evento["deporte"])} · {texto(identidad)}</div>'
            f'<div style="font-size:20px;font-weight:bold;line-height:1.35;">{texto(titulo)}</div>'
            f'<div style="font-size:13px;line-height:1.5;color:{secundaria};margin-top:7px;">{texto(evento["competicion"])}</div>'
            f'<div style="margin-top:10px;">{categoria_html(evento)} {badge}</div>{desglose_html(evento)}{explicacion_html(evento)}</td></tr></table>'
            f'<p style="color:{tinta};font-size:13px;line-height:1.6;margin:16px 0 0;padding-top:12px;border-top:1px solid {"#3c536b" if destacado else "#edf1f5"};">'
            f'<strong>TV</strong><br>{canales_html(evento)}</p>'
            + (f'<p style="font-size:12px;line-height:1.6;color:{secundaria};margin:8px 0 0;">{texto(" · ".join([s for s in [fin, *estado] if s]))}</p>' if fin or estado else '')
            + '</td></tr></table>')

def listado_completo(eventos):
    filas = []
    for e in eventos:
        fecha = e['inicio'].strftime('%d/%m') if 'inicio' in e else e.get('fecha', '')
        nombre = (e.get('descripcion') or e['competicion']) if not e.get('local') else f"{e['local']} — {e['visitante']}"
        fondo, acento, _ = tema_evento(e)
        filas.append(f'<tr class="evento-filtrado" style="background:{fondo};">'
                     f'<td width="68" valign="top" style="padding:13px 12px;text-align:center;border-bottom:1px solid #e4eaf1;white-space:nowrap;"><strong>{texto(e["hora"])}</strong><br><span style="font-size:11px;color:#64748b;">{texto(fecha)}</span></td>'
                     f'<td valign="top" style="padding:13px 8px;border-left:4px solid {acento};border-bottom:1px solid #e4eaf1;overflow-wrap:anywhere;">'
                     f'<strong style="font-size:14px;">{texto(nombre)}</strong><br>'
                     f'<span style="font-size:12px;color:#52647a;">{texto(e["deporte"])} · {texto(e["competicion"])}</span><br>'
                     f'<span style="font-size:12px;line-height:1.6;">{canales_html(e)}</span><br>'
                     f'<span style="font-size:11px;color:#1b6948;">{texto(nota_texto(e))} · {texto(e.get("nivel", ""))}</span> {categoria_html(e)}'
                     + (f'<br><span style="font-size:11px;color:#8a5217;">Visionado parcial hasta {e["fin_vision"]:%H:%M}</span>' if e.get('vision_parcial') else '')
                     + ('<br><span style="font-size:11px;color:#8a5217;">En curso</span>' if e.get('en_curso') else '')
                     + explicacion_html(e) + '</td></tr>')
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

def bloque_camisetas(secciones, camiseta):
    partes = [
        '<div id="bloque-camisetas" style="margin:0 0 24px;border:2px solid #7660a7;border-radius:16px;overflow:hidden;background:#f5f0fb;">',
        '<div style="background:#33234f;color:#ffffff;padding:22px;border-bottom:5px solid #d8bc72;">'
        '<p style="margin:0 0 8px;font-size:11px;letter-spacing:2px;color:#e9d8ff;">DE TU COLECCIÓN</p>'
        '<h2 style="font-size:23px;line-height:1.3;margin:0;">👕 Tu camiseta de hoy</h2>'
        '<p style="font-size:12px;line-height:1.6;margin:10px 0 0;">Una elección para acompañar tu día de deporte.</p></div>'
        '<div style="padding:16px;">'
    ]
    for titulo, lineas in secciones:
        if not titulo.startswith('👕'):
            continue
        asociada = titulo == '👕 Camiseta recomendada' and bool(camiseta.get('partido_asociado'))
        label = '★ RECOMENDADA POR PARTIDO' if asociada else '🎲 ELECCIÓN AL AZAR'
        color = '#fff6df' if asociada else '#eee6f8'
        borde = '#b58b32' if asociada else '#9477bb'
        partes.append(f'<div class="tarjeta-camiseta" style="background:{color};color:#33234f;padding:18px;margin-bottom:12px;border:1px solid {borde};border-left:5px solid {borde};border-radius:10px;">'
                      f'{etiqueta(label, "#33234f", "#ffffff")}')
        for indice, linea in enumerate(lineas):
            partes.append(f'<p style="font-size:{20 if indice == 0 else 13}px;line-height:1.6;margin:10px 0 0;'
                          f'{"font-weight:bold;" if indice == 0 else ""}">{texto(linea)}</p>')
        partes.append('</div>')
    partes.append('</div></div>')
    return ''.join(partes)


def crear_html(asunto, secciones, resultado, todos):
    events = resultado['eventos']
    bloques = []
    if events is not None:
        bloques.append(f'<p style="margin:0 0 22px;">{etiqueta(str(len(events.get("seleccionados", []))) + " en tu plan")}{etiqueta(str(len(todos)) + " eventos filtrados")}{etiqueta("EUROPE / MADRID")}</p>')
    camisetas_mostradas = False
    for titulo, lineas in secciones:
        if titulo.startswith('👕'):
            if not camisetas_mostradas:
                bloques.append(bloque_camisetas(secciones, resultado['camiseta']))
                camisetas_mostradas = True
        elif titulo in ('📺 Imprescindible','📺 Lo mejor del día') and events['plan'].get('imprescindible'):
            bloques.append(tarjeta_evento(events['plan']['imprescindible'], True))
        elif titulo == '🏀 NBA en diferido · sin spoilers':
            nba = resultado['nba']
            bloques.append('<div id="bloque-nba" style="margin:26px 0;border:2px solid #c45a12;border-radius:16px;overflow:hidden;background:#fff2e5;">'
                           '<div style="background:#142840;padding:22px;color:#ffffff;border-bottom:5px solid #ed7b24;">'
                           '<p style="margin:0 0 8px;font-size:11px;letter-spacing:2px;color:#ffb77e;">TU SESIÓN DE BALONCESTO</p>'
                           '<h2 style="font-size:23px;margin:0;color:#ffffff;">🏀 NBA en diferido</h2>'
                           '<p style="font-size:12px;line-height:1.6;margin:10px 0 0;">Sin marcadores ni notas · Orden alfabético</p></div><div style="padding:16px;">')
            for p in nba['partidos']:
                fondo_nba, acento_nba, _ = tema_evento({**p, 'deporte':'Baloncesto', 'competicion':'NBA'})
                bloques.append(f'<div class="tarjeta-nba" style="background:{fondo_nba};color:#142840;padding:18px;margin-bottom:12px;border:1px solid {acento_nba};border-left:5px solid {acento_nba};border-radius:10px;">'
                               f'{distintivo_nba(p["recomendacion"])}<p style="font-size:17px;line-height:1.5;font-weight:bold;margin:12px 0 0;">{texto(p["local"])} — {texto(p["visitante"])}</p></div>')
            if not nba['partidos']:
                bloques.append('<p>No hay partidos finalizados y validados en esta consulta.</p>')
            cobertura = [f"Ventana de inicio de partidos: {nba['ventana']}",
                         f"Consultado: {nba['consultado']} · Fuente: {nba['fuente']}", *nba['avisos']]
            bloques.append('<div style="border-top:1px solid #d88a4c;padding-top:12px;color:#513822;font-size:12px;line-height:1.7;">'
                           + '<br>'.join(texto(l) for l in cobertura) + '</div></div></div>')
        elif titulo == 'Cobertura NBA':
            continue  # La cobertura ya figura dentro del bloque NBA.
        elif titulo == 'Tu planning flexible':
            bloques.append('<div id="bloque-planning" style="margin:26px 0;border:2px solid #287b79;border-radius:16px;overflow:hidden;background:#f0f8f7;">'
                           '<div style="padding:22px;background:#153e43;color:#ffffff;border-bottom:5px solid #7bd3bc;">'
                           '<p style="font-size:11px;letter-spacing:2px;margin:0 0 8px;color:#b5e8dc;">TU TIEMPO, A TU RITMO</p>'
                           '<h2 style="font-size:23px;margin:0;">Tu planning diario</h2>'
                           '<p style="font-size:12px;line-height:1.6;margin:10px 0 0;">Citas principales y opciones voluntarias, en orden de visionado.</p></div>'
                           '<div style="padding:16px;">')
            for b in events.get('planning', []):
                principal = b['tipo'] == 'Cita principal'
                origen = next((e for e in events.get('filtrados', []) if (f"{e['local']} — {e['visitante']}" if e.get('local') else e.get('descripcion') or e['competicion']) == b['evento']), {})
                color, acento, _ = tema_evento(origen)
                bloques.append('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed;margin-bottom:12px;">'
                               f'<tr><td width="68" valign="top" style="padding:16px 12px;text-align:center;color:#153e43;font-size:14px;"><strong>{texto(b["desde"])}</strong>'
                               f'<br><span style="font-size:11px;">hasta<br>{texto(b["hasta"])}</span></td>'
                               f'<td valign="top" style="padding:16px;background:{color};border-left:4px solid {acento};border-radius:0 10px 10px 0;overflow-wrap:anywhere;">'
                               f'{etiqueta(b["tipo"], "#153e43" if principal else "#bde3d7", "#ffffff" if principal else "#153e43")}'
                               f'<p style="font-size:16px;line-height:1.5;margin:10px 0 0;color:#153e43;"><strong>{texto(b["evento"])}</strong></p>'
                               f'<p style="font-size:12px;line-height:1.65;margin:8px 0 0;color:#375a5d;">{texto(b["detalle"])}</p></td></tr></table>')
            if not events.get('planning'):
                bloques.append('<p style="color:#153e43;">Sin citas que reservar: deja el día libre.</p>')
            bloques.append('<p style="font-size:12px;color:#375a5d;line-height:1.6;">Los huecos quedan libres. Opciones voluntarias y finales estimados.</p>')
            alternativas = events.get('alternativas', [])
            if alternativas:
                bloques.append('<div style="border-top:1px solid #a3c8c0;margin-top:18px;padding-top:14px;"><h3 style="font-size:15px;color:#153e43;margin:0 0 12px;">Alternativas para cambiar tu plan</h3>'
                               '<p style="font-size:12px;color:#375a5d;">No se añaden a la línea temporal. Puedes elegirlas en lugar de otra cita.</p>')
                bloques.extend(tarjeta_evento(e) for e in alternativas)
                bloques.append('</div>')
            for aviso in events.get('avisos', []):
                bloques.append(f'<p style="font-size:12px;color:#375a5d;line-height:1.6;">{texto(aviso)}</p>')
            bloques.append('</div></div>')
        elif titulo in ('Plan principal del día', 'Alternativas', 'Información', 'Cobertura de la agenda'):
            continue  # Contenido agrupado en planning o listado completo.
        elif titulo.startswith('Todos los eventos filtrados'):
            bloques.append(f'<div style="margin:26px 0;padding:20px;border-radius:14px;background:#e0eee7;"><h2 style="font-size:19px;margin:0 0 10px;">¿Quieres más opciones?</h2>'
                           f'<a href="#todos-eventos" style="display:inline-block;background:#1b6948;color:#ffffff;text-decoration:none;padding:13px 16px;border-radius:8px;font-size:14px;font-weight:bold;">Ver los {len(todos)} eventos filtrados ↓</a>'
                           '<p style="font-size:12px;line-height:1.6;margin:12px 0 0;">Listado completo a continuación, también adjunto como todos_eventos.html.</p></div>'
                           f'<div id="todos-eventos" style="padding:20px;background:#ffffff;border:1px solid #dce5ef;border-radius:14px;"><h2 style="font-size:19px;margin:0 0 8px;">{texto(titulo)}</h2>'
                           '<p style="font-size:12px;color:#61718a;line-height:1.6;">Orden cronológico. Incluye todos los que pasan tus filtros y disponibilidad, aunque su puntuación no alcance el plan.</p>'
                           + ''.join(f'<p style="font-size:12px;color:#61718a;line-height:1.6;">{texto(l)}</p>' for t, ls in secciones if t == 'Información' for l in ls)
                           + listado_completo(todos) + '</div>')
        else:
            jersey = titulo.startswith('👕')
            aviso = titulo in ('Avisos de ejecución','Cobertura de la agenda','Demostración')
            fondo = '#fff5e6' if aviso else '#ffffff'
            cuerpo = ''.join(f'<p style="margin:8px 0;line-height:1.65;font-size:{"20" if jersey and i == 0 else "13"}px;{"font-weight:bold;" if jersey and i == 0 else "color:#52647a;"}">{texto(l)}</p>' for i,l in enumerate(lineas))
            bloques.append(f'<div style="background:{fondo};padding:20px;margin-bottom:14px;border:1px solid #dce5ef;border-radius:14px;'
                           + ('border-left:5px solid #dfae50;' if jersey else '') + f'"><h2 style="font-size:15px;margin:0 0 12px;">{texto(titulo)}</h2>{cuerpo}</div>')
    return pagina(asunto,''.join(bloques))
