"""Identidad visual: equipos por delante de competición, sin inferir resultados."""
import unicodedata
import re


def normalizar(texto):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFD', texto.casefold())
                           if not unicodedata.combining(c)).split())


def tema_evento(e):
    equipos = {normalizar(e.get(k, '')) for k in ('local', 'visitante')}
    deporte = normalizar(e.get('deporte', ''))
    comp = normalizar(e.get('competicion', ''))
    if deporte == 'baloncesto' and equipos & {'celtics', 'boston celtics'}:
        return '#e2f3e8', '#007a33', 'Boston Celtics'
    if deporte == 'futbol':
        if equipos & {'atletico de madrid', 'atletico madrid', 'at. madrid', 'at madrid', 'espana', 'seleccion espanola'}:
            return '#ffe5e5', '#b51c2b', 'Atleti / España'
        if 'aston villa' in equipos:
            return '#f4e3ea', '#760d35', 'Aston Villa'
        if 'conference' in comp:
            return '#e7f4df', '#39751c', 'Conference League'
        if 'europa league' in comp or 'liga europa' in comp:
            return '#ffecd9', '#aa4b08', 'Europa League'
        if 'champions' in comp or 'liga de campeones' in comp:
            return '#e4ebff', '#183d96', 'Champions League'
        if re.search(r'\b(copa|cup|pokal|coupe|coppa|taca)\b', comp):
            return '#f9e4f2', '#91316e', 'Copa'
        return '#e2f1f0', '#286c69', 'Liga / fútbol'
    if deporte == 'tenis':
        return '#f1f7b5', '#566400', 'Tenis'
    if deporte == 'baloncesto':
        if 'nba' in comp:
            return '#ffdfc1', '#b45309', 'NBA'
        if 'euroliga' in comp or 'euroleague' in comp:
            return '#ede4fa', '#683d99', 'Euroliga'
        if re.search(r'\b(copa|cup)\b', comp):
            return '#f9e4f2', '#91316e', 'Copa de baloncesto'
        if any(s in comp for s in ('acb', 'endesa')):
            return '#dff0ff', '#176a91', 'ACB'
        return '#fff0df', '#955717', 'Baloncesto'
    return '#edf2f7', '#52647a', e.get('deporte', 'Deporte')
