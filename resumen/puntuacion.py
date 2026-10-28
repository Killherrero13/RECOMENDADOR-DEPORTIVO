"""Escala personal estable /10; acceso y horario afectan al encaje, no a la nota."""
import re

from .categorias import categoria_tenis
from .perfiles import identidad_basket, REFERENTES_EUROLIGA, REFERENTES_TENIS, perfil_tenis
from .canales import plataforma_destacada
from .contexto import valorar_contexto

UMBRAL_PLAN = 6.5
UMBRAL_ALTERNATIVAS = 4.5
FAVORITOS_FUTBOL = {'atletico madrid', 'aston villa'}
REFERENTES_FUTBOL = {
    'real madrid','fc barcelona','atletico madrid','aston villa','bayern munich',
    'inter milan','ac milan','napoli','juventus','roma','arsenal','manchester united',
    'manchester city','liverpool','chelsea','tottenham','borussia dortmund',
    'psg','lyon','olympique marsella','benfica','porto','sporting lisboa','ajax',
}
REFERENTES_NBA = {'lakers','warriors','celtics','nuggets','suns','clippers'}
REFERENTES_ACB = {'barcelona','real madrid','valencia','joventut','gran canaria','baskonia'}


def coincide(alias, nombre):
    return re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', nombre) is not None

def contar_referentes(local, visitante, referentes):
    return sum(any(coincide(t, nombre) for t in referentes) for nombre in (local, visitante))

def base_futbol(comp):
    # Especificidad antes de términos amplios: segunda división no equivale a primera.
    for tokens, valor, motivo in [
        (['hypermotion','2. bundesliga'],4.3,'Segunda división de interés'),
        (['serie a brasil','primera division argentina'],3.3,'Primera división sudamericana'),
        (['copa del mundo','world cup','fifa copa mundial'],6.2,'Competición mundial'),
        (['eurocopa','copa america'],5.8,'Torneo continental de selecciones'),
        (['champions league','europa league'],5.6,'Competición europea principal'),
        (['conference league'],4.8,'Competición europea'),
        (['copa libertadores','conmebol libertadores'],5.6,'Copa continental sudamericana'),
        (['nations league','copa africana de naciones'],5.0,'Competición de selecciones'),
        (['supercopa'],5.0,'Supercopa'),
        (['laliga','ea sports','premier','bundesliga','serie a','ligue 1'],5.0,'Primera división europea principal'),
        (['liga portuguesa','eredivisie'],4.3,'Primera división europea'),
        (['jupiler','scottish premiership'],4.0,'Primera división europea'),
        (['copa del rey','fa cup','emirates','coppa','coupe de france','copa de francia',
          'copa de alemania','dfb-pokal','dfb pokal','carabao cup','efl cup'],4.5,'Copa nacional'),
    ]:
        if any(token in comp for token in tokens):
            return valor, motivo
    return 3.5, 'Competición admitida: valoración neutral'

def nivel_nota(nota):
    if nota >= 8:return 'Cita destacada'
    if nota >= 6:return 'Buena opción'
    if nota >= 4:return 'De fondo'
    return 'Prescindible'

def valorar(evento, local, visitante, competicion, afinidad_previa=0, derby=0, ronda=0):
    sport = evento['deporte']
    cartel = 0.0
    afinidad = 0.0
    motivos = []
    # El bonus de fase anterior distingue final, semifinal, cuartos y octavos.
    fase = {2.5:2.4, 2.0:1.6, 1.5:1.0, 1.0:0.6, 0.8:0.3}.get(ronda, 0)
    if sport == 'Fútbol':
        base, motivo = base_futbol(competicion)
        motivos.append(motivo)
        n = contar_referentes(local, visitante, REFERENTES_FUTBOL)
        cartel = 2.0 if n == 2 else 0.8 if n == 1 else 0
        if n == 2:motivos.append('Duelo entre equipos de referencia')
        elif n == 1:motivos.append('Participa un equipo de referencia')
        if derby:
            cartel += min(0.6, derby * 0.3)
            motivos.append('Rivalidad reconocida')
        if local in FAVORITOS_FUTBOL or visitante in FAVORITOS_FUTBOL:
            afinidad = 1.3
            motivos.append('Juega uno de tus favoritos')
        else:
            afinidad = max(0, afinidad_previa) * 0.7
        afinidad += 0.2 # Preferencia habitual por fútbol, sin veto a otros deportes.
    elif sport == 'Baloncesto':
        if 'nba' in competicion:
            base = 5.0
            n = contar_referentes(local, visitante, REFERENTES_NBA)
            afinidad = max(-0.5,min(1.5,afinidad_previa)) * 0.7
            if coincide('celtics',local) or coincide('celtics',visitante):
                afinidad = 1.3
                motivos.append('Juegan tus Celtics')
        else:
            base = (5.8 if any(x in competicion for x in ['mundial','copa del mundo','world cup','eurobasket','olimpic']) else
                    5.0 if any(x in competicion for x in ('euroliga', 'euroleague')) else
                    4.5 if any(x in competicion for x in ['endesa','acb','copa del rey']) else 3.5)
            equipos = [identidad_basket(e) for e in (local, visitante)]
            referentes = REFERENTES_EUROLIGA if any(x in competicion for x in ('euroliga', 'euroleague')) else REFERENTES_ACB
            n = sum(e in referentes for e in equipos)
            if 'estudiantes' in local or 'estudiantes' in visitante:afinidad = 0.6
        cartel = 1.5 if n == 2 else 0.8 if n == 1 else 0
        afinidad += 0.1
        motivos.append('Baloncesto de interés')
        if n:
            motivos.append('Dos clubes del catálogo de referentes de la competición' if n == 2 else 'Un club del catálogo de referentes de la competición')
        if 'minicopa' in competicion:base = 2.0
    elif sport == 'Tenis':
        categoria, _ = categoria_tenis(evento)
        base = {'Grand Slam':5.8,'Masters 1000':5.0,'ATP 500':4.4,'ATP 250':3.8}.get(categoria,3.2)
        perfiles = [perfil_tenis(p) for p in (local, visitante)]
        n = sum(p is not None for p in perfiles)
        cartel = sum(1.2 if p == 'figura' else 0.5 if p == 'referente' else 0 for p in perfiles)
        if n == 2:
            cartel += 0.5
        afinidad = max(0,afinidad_previa) * 0.28
        motivos.append(categoria or 'Categoría sin confirmar: valoración neutral')
        if 'figura' in perfiles: motivos.append('Figura del catálogo editorial de tenis')
        if n == 2: motivos.append('Ambos jugadores tienen perfil reconocido; se valora también al rival')
        elif n == 1: motivos.append('Un jugador reconocido; rival sin perfil en el catálogo')
    elif sport == 'Automovilismo':
        base = 4.7 if any(x in competicion for x in ['formula 1','f1']) else 3.5
        motivos.append('Motor: interés secundario')
    elif sport == 'Balonmano':
        base = 4.2
        if local == 'espana' or visitante == 'espana':afinidad = 0.6
        motivos.append('Balonmano de selección')
    else:
        base = 3.0
        motivos.append('Valoración neutral del deporte')
    if fase:
        motivos.append('Final' if ronda == 2.5 else 'Fase de eliminatoria')
    contexto = valorar_contexto(evento)
    motivos.extend(contexto['motivos'])
    deportivo_basico = min(8.5, base + cartel + fase)
    afinidad_basica = max(-deportivo_basico, min(10-deportivo_basico, afinidad))
    nota_basica = round(max(0, min(10, deportivo_basico + afinidad_basica)), 1)
    afinidad += contexto.get('afinidad', 0)
    deportivo = round(min(8.5,base + cartel + fase + contexto['ajuste']),2)
    afinidad = round(max(-deportivo,min(10-deportivo,afinidad)),2)
    nota = round(max(0,min(10,deportivo+afinidad)),1)
    canales = evento.get('canales',[])
    acceso = 0.2 if any(plataforma_destacada(c) or any(x in c.casefold() for x in ['teledeporte','rtve','youtube']) for c in canales) else 0
    horario = -(0.6 if evento.get('madrugada') else 0) - (0.5 if evento.get('vision_parcial') else 0)
    return {'score':nota,'prioridad':round(nota+acceso+horario,2),'nivel':nivel_nota(nota),
            'desglose':{'base':base,'cartel':cartel,'fase':fase,'deportivo':deportivo,
                        'afinidad':afinidad,'acceso':acceso,'horario':horario,'contexto':round(nota-nota_basica,1)},
            'evaluacion_contexto':contexto,
            'motivos':motivos, 'escala':'personal-10-v2'}
