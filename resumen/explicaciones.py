"""Motivos verificables del interés y del lugar de cada evento en el plan."""
from .horarios import intervalo
from .canales import plataforma_destacada
from .puntuacion import UMBRAL_PLAN
from .preferencias_eventos import MAX_OVERLAP


def explicar_agenda(eventos, plan, clave):
    seleccion = {clave(e) for e in plan.values()}
    for e in eventos:
        # Destacar primero las señales personales y las eliminatorias.
        motivos = list(dict.fromkeys(e.get('motivos', [])))
        motivos.sort(key=lambda m: 0 if any(s in m.casefold() for s in ('contexto:', 'favorito', 'celtics', 'final', 'eliminatoria')) else 1)
        razones = motivos[:3]
        plataformas = list(dict.fromkeys(p for c in e.get('canales', []) if (p := plataforma_destacada(c))))
        if plataformas:
            razones.append('En tu acceso declarado: ' + ' y '.join(plataformas) + '.')
        if e.get('vision_parcial'):
            razones.append(f"Solo puedes verlo hasta las {e['fin_vision']:%H:%M}; el final es estimado.")
        if e.get('madrugada'):
            razones.append('Horario de madrugada: encaja peor con tu descanso.')
        if clave(e) in seleccion:
            papel = 'Elegido para tu plan por su interés y encaje.'
        elif e['score'] < UMBRAL_PLAN:
            papel = 'Opción secundaria: no alcanza el umbral del plan (6,5/10).'
        else:
            inicio, fin = intervalo(e)
            conflictos = []
            for otro in plan.values():
                a, b = intervalo(otro)
                if min(fin, b) - max(inicio, a) > MAX_OVERLAP:
                    nombre = (f"{otro['local']} — {otro['visitante']}" if otro.get('local')
                              else otro.get('descripcion') or otro['competicion'])
                    conflictos.append(nombre)
            papel = ('Coincide con tu plan: ' + '; '.join(dict.fromkeys(conflictos)) + '. Duraciones estimadas.'
                     if conflictos else 'Fuera del plan: otras opciones tienen mejor prioridad y el plan tiene plazas limitadas.')
        e['explicacion'] = {'motivos': razones, 'papel': papel}


def frases_explicacion(evento):
    explicacion = evento.get('explicacion', {})
    return [*explicacion.get('motivos', []), *([explicacion['papel']] if explicacion.get('papel') else [])]
