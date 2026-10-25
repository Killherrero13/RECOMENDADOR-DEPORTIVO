"""Filtros, puntuaciones y agenda originales, sin consultas al importar."""
from copy import deepcopy
from datetime import time

from .preferencias_eventos import (
    EVENT_DURATION,
    MAX_OVERLAP,
    DAY_START,
    DAY_END,
    TOP_ATP,
    TOP_ATP_20,
    TOP_NCAA,
    TOP_ACB,
    BIG_FOOTBALL_TEAMS,
    NBA_TOP_TEAMS,
    POSITIVE_CHANNELS,
    FREE_CHANNELS,
    NBA_TEAM_AFFINITY,
    FOOTBALL_TEAM_AFFINITY,
    FOOTBALL_DERBIES,
    TENNIS_PLAYER_AFFINITY,
    ALLOWED_FOOTBALL_COMPETITIONS,
    EXCLUDED_FOOTBALL_COMPETITIONS,
    MAX_OTHER_EVENTS
)

def hour_to_min(h):
    hh, mm = map(int, h.split(":"))
    return hh * 60 + mm

def is_female(e):
    text = f"{e['local']} {e['visitante']} {e['competicion']}".lower()
    return any(x in text for x in ["women", "femenino", "femenina", "ellas", "fsf"])

def valid_time(hora):
    try:
        h, m = map(int, hora.split(":"))
        return time(9, 0) <= time(h, m) <= time(23, 30)
    except ValueError:
        # Handle cases where hora is not in 'HH:MM' format, e.g., 'PD'
        return False

def is_lower_division_football(e):
    comp = e["competicion"].lower()
    return any(x in comp for x in ["primera federación", "segunda federación", "tercera", "regional", "academy", "juvenil", "sub-19", "sub 19", "u19"])

def channel_score(canales):
    text = " ".join(canales).lower()
    score = 0
    if any(c in text for c in POSITIVE_CHANNELS):
        score += 2
    if any(c in text for c in FREE_CHANNELS):
        score += 1
    return score

def can_add_event(event, selected):
    start = hour_to_min(event["hora"])
    end = start + EVENT_DURATION

    for e in selected:
        s = hour_to_min(e["hora"])
        e_end = s + EVENT_DURATION
        overlap = min(end, e_end) - max(start, s)
        if overlap > MAX_OVERLAP:
            return False

    return True

def nba_affinity_score(local, visitante):
    score = 0
    for team, affinity in NBA_TEAM_AFFINITY.items():
        if team in local:
            score += affinity
        if team in visitante:
            score += affinity
    return score

def football_team_affinity(event):
    local = event["local"].lower()
    visitante = event["visitante"].lower()

    affinities = []

    for team, value in FOOTBALL_TEAM_AFFINITY.items():
        if team in local:
            affinities.append(value)
        if team in visitante:
            affinities.append(value)

    return max(affinities) if affinities else 0

def football_derby_bonus(event):
    local = event["local"].lower()
    visitante = event["visitante"].lower()

    for (team1, team2), bonus in FOOTBALL_DERBIES.items():
        if (team1 in local and team2 in visitante) or \
           (team2 in local and team1 in visitante):
            return bonus

    return 0

def knockout_bonus(event):
    comp = event["competicion"].lower()
    bonus = 0

    if "final" in comp:
        bonus = 2.5
    elif "semifinal" in comp:
        bonus = 2.0
    elif any(x in comp for x in ["cuartos", "quarter", "playoffs"]):
        bonus = 1.5
    elif any(x in comp for x in ["octavos", "round of 16", "1/8"]):
        bonus = 1.0
    elif any(x in comp for x in ["1/16", "round of 32"]):
        bonus = 0.8

    # Ajuste por ida / vuelta
    if "vuelta" in comp:
        bonus += 0.7
    elif "ida" in comp:
        bonus += 0.3

    return bonus

def stakes_bonus(event):
    comp = event["competicion"].lower()
    bonus = 0

    # Título claro
    if any(x in comp for x in [
        "supercopa", "playoff", "titulo", "campeón"
    ]):
        bonus += 2.0

    # Ascenso / descenso
    if any(x in comp for x in [
        "ascenso", "permanencia", "descenso", "playout"
    ]):
        bonus += 1.2

    return bonus

def tennis_affinity_bonus(event):
    local = event["local"].lower()
    visitante = event["visitante"].lower()

    for player, bonus in TENNIS_PLAYER_AFFINITY.items():
        if player in local or player in visitante:
            return bonus

    return 0

def event_key(e):
    return (
        e["hora"],
        e["deporte"],
        e.get("competicion"),
        e.get("local"),
        e.get("visitante")
    )

def football_match_quality_bonus(local, visitante):
    big_count = 0
    for team in BIG_FOOTBALL_TEAMS:
        if team in local or team in visitante:
            big_count += 1

    if big_count == 2:
        return 3.0 # Doubled from 1.5
    elif big_count == 1:
        return 1.0 # Doubled from 0.5
    return 0

def normalize_team_name(name):
    name = name.lower()
    replacements = {
        "at. madrid": "atletico madrid",
        "atlético madrid": "atletico madrid",
        "atletico de madrid": "atletico madrid",
        "fc barcelona": "fc barcelona",
        "barça": "fc barcelona",
        "psg": "psg",
    }
    for k, v in replacements.items():
        name = name.replace(k, v)
    return name

def select_preferred_channel(canales):
    """
    Devuelve UN solo canal favorito según prioridad:
    Movistar+ > DAZN > resto favoritos.
    Si no hay canal favorito, devuelve None.
    """
    if not canales:
        return None

    canales_norm = [c.lower() for c in canales]

    # 1️⃣ Movistar+
    for c in canales_norm:
        if "movistar" in c:
            return "Movistar+"

    # 2️⃣ DAZN
    for c in canales_norm:
        if "dazn" in c:
            return "DAZN"

    # 3️⃣ Resto favoritos
    for c in canales_norm:
        if any(x in c for x in ["teledeporte", "rtve", "youtube"]):
            # Normalizamos nombre bonito
            if "youtube" in c:
                return "YouTube"
            if "teledeporte" in c:
                return "Teledeporte"
            if "rtve" in c:
                return "RTVE Play"

    return None

def calculate_score(e):
    score = 0
    deporte = e["deporte"]
    comp = e["competicion"].lower()
    local = e["local"].lower()
    visitante = e["visitante"].lower()
    hora = hour_to_min(e["hora"]) // 60
    local = normalize_team_name(local)
    visitante = normalize_team_name(visitante)

    if deporte == "Fútbol":

        # Specific bonus for Nations League
        if "nations league" in comp:
            score += 3.5
        # Highest priority competitions (knockout/finals are handled by knockout_bonus/stakes_bonus)
        elif "supercopa" in comp:
            score += 4
        elif any(x in comp for x in ["champions league", "europa league", "fifa copa mundial"]):
            score += 4.5 # Increased base score for Champions League
        elif "copa africana de naciones" in comp:
            score += 4.0 # Specific bonus for Africa Cup of Nations
        elif any(x in comp for x in ["copa américa", "eurocopa"]):
            score += 4.5 # Specific bonus for Copa América and Eurocopa
        elif "copa del mundo" in comp or "world cup" in comp:
            score += 5.0 # Specific bonus for World Cup
        # Top 5 leagues, with specific checks for second divisions
        elif any(x in comp for x in ["laliga", "ea sports", "premier", "bundesliga", "serie a", "ligue 1"]):
            if "hypermotion" in comp: # LaLiga Hypermotion (Spanish second division)
                score += 1.8
            elif "2. bundesliga" in comp: # 2. Bundesliga (German second division)
                score += 1.8
            else: # Top tier of these leagues
                score += 2.5
        # Other decent leagues
        elif any(x in comp for x in ["eredevisie", "serie a brasil", "jupiler pro league", "liga portuguesa", "scottish premiership"]):
            score += 1.5
        # Cup competitions (national cups)
        elif any(x in comp.lower() for x in ["fa cup", "copa del rey", "emirates", "copa de francia", "coupe de france", "coppa"]):
            score += 2

        if "atletico madrid" in local or "atletico madrid" in visitante:
            score += 3.5

        if "aston villa" in local or "aston villa" in visitante:
            score += 2

        # Bonus for 'España' (Spain) if playing
        if "españa" in local or "españa" in visitante:
            score += 3.0

        score += football_match_quality_bonus(local, visitante)

        # Contexto fuerte
        context_total = (
            football_derby_bonus(e)
            + knockout_bonus(e)
            + stakes_bonus(e)
        )
        score += min(context_total, 4.0)

        # Afinidad personal (FACTOR DECISIVO)
        affinity = football_team_affinity(e)
        score *= (1 + affinity * 0.4)

    elif deporte == "Baloncesto":
        if "nba" in comp:
            score += 3
            if any(t in local or t in visitante for t in NBA_TOP_TEAMS):
                score += 1

            affinity = nba_affinity_score(local, visitante)
            score += affinity * 3

        if "endesa" in comp or "acb" in comp or "euroliga" in comp:
            score += 2.5
        if "estudiantes" in local or "estudiantes" in visitante:
            score += 4
        if "estudiantes" in local or "estudiantes" in visitante:
            score += 4
        if "minicopa" in comp:
            score -= 4.5

        if any(t in local for t in TOP_NCAA) or any(t in visitante for t in TOP_NCAA):
            score += 1 # Base score for NCAA games

        if any(t in local or t in visitante for t in TOP_ACB):
            score += 2

        # Bonus por eliminatorias
        score += knockout_bonus(e)
        score += stakes_bonus(e)


    elif deporte == "Tenis":
        score += 2  # base tenis

        # Finales y torneos grandes
        score += knockout_bonus(e)
        score += stakes_bonus(e)
        if "grand slam" in comp:
            score += 4
        elif "masters 1000" in comp:
            score += 3
        elif "atp 500" in comp:
            score += 2
        elif "atp 250" in comp:
            score += 1

        affinity = tennis_affinity_bonus(e)

        if affinity > 0:
            score += affinity
        else:
            # Penalización si no es un partido realmente top
            if score < 6:
                score -= 2


    elif deporte == "Automovilismo":
        score += 1.5

    if 9<= hora <= 23:
        score += 1

    return score + channel_score(e["canales"])

def build_daily_plan(events):
    # --------------------------------------------------
    # 1️⃣ Elegir IMPRESCINDIBLE (por score, no por hora)
    # --------------------------------------------------
    top_events = [
        e for e in events
        if e["score"] >= 7
        and DAY_START <= hour_to_min(e["hora"]) <= DAY_END
    ]

    if not top_events:
        return {}, []

    must_watch = max(top_events, key=lambda e: e["score"])

    # --------------------------------------------------
    # 2️⃣ Construir selección respetando solapes
    # --------------------------------------------------
    selected = [must_watch]

    for e in events:
        if e is must_watch:
            continue

        start = hour_to_min(e["hora"])

        # Respeta horario diario
        if start < DAY_START or start > DAY_END:
            continue

        # Umbral mínimo
        if e["score"] < 7:
            continue

        # Solapamiento real
        if not can_add_event(e, selected):
            continue

        selected.append(e)

        # Límite suave
        if len(selected) == 4:
            break

    # --------------------------------------------------
    # 3️⃣ Orden cronológico para presentación
    # --------------------------------------------------
    selected.sort(key=lambda e: hour_to_min(e["hora"]))

    # --------------------------------------------------
    # 4️⃣ Construir plan visual
    # --------------------------------------------------
    plan = {"imprescindible": must_watch}

    for e in selected:
        if e is must_watch:
            continue

        h = hour_to_min(e["hora"])
        if h < 12 * 60:
            plan["mañana"] = e
        elif h < 15 * 60:
            plan["mediodía"] = e
        elif h < 20 * 60:
            plan["tarde"] = e
        else:
            plan["noche"] = e

    return plan, selected

def recomendar_eventos(events):
    # La copia evita añadir score/channel a los datos de entrada del llamante.
    events = deepcopy(events)
    filtered_events = []
    for e in events:
        deporte = e["deporte"]
        comp = e["competicion"].lower()
        local = e["local"].lower()
        visitante = e["visitante"].lower()
        canales = " ".join(e["canales"]).lower()
        local = normalize_team_name(local)
        visitante = normalize_team_name(visitante)
    
    
        if is_female(e) or not valid_time(e["hora"]):
            continue
    
        if deporte in {"Fútbol Sala", "Waterpolo", "Hockey Patines", "Atletismo", "Rugby U", "Boxeo", "Ishockey", "Béisbol"}:
            continue
    
        if deporte == "Automovilismo":
            filtered_events.append(e)
            continue
    
        if deporte == "Fútbol":
            if "u23" in comp or is_lower_division_football(e):
                continue
            if not any(x in comp for x in ALLOWED_FOOTBALL_COMPETITIONS):
                continue
            if any(x in comp for x in EXCLUDED_FOOTBALL_COMPETITIONS):
                continue
            filtered_events.append(e)
            continue
    
        if deporte == "Baloncesto":
            is_relevant_baloncesto = False
            if "nba" in comp:
                is_relevant_baloncesto = True
            if "copa del rey" in comp:
                is_relevant_baloncesto = True
            if "endesa" in comp or "acb" in comp or "euroliga" in comp:
                is_relevant_baloncesto = True
            if "estudiantes" in local or "estudiantes" in visitante:
                is_relevant_baloncesto = True
            if "españa" in local or "españa" in visitante:
                is_relevant_baloncesto = True
            if any(t in local for t in TOP_NCAA) or any(t in visitante for t in TOP_NCAA):
                is_relevant_baloncesto = True
    
            if is_relevant_baloncesto:
                filtered_events.append(e)
            continue
    
        if deporte == "Balonmano":
            if local == "españa" or visitante == "españa":
                filtered_events.append(e)
            continue
    
        if deporte == "Tenis":
            if any(p in local for p in TOP_ATP_20) or any(p in visitante for p in TOP_ATP_20):
                filtered_events.append(e)
    for e in filtered_events:
        e['score'] = calculate_score(e)
        e['channel'] = select_preferred_channel(e['canales'])
    filtered_events.sort(key=lambda e: e['hora'])
    daily_plan, selected_events = build_daily_plan(filtered_events)
    visible_plan_keys = {event_key(e) for e in daily_plan.values()}
    other_top_events = [e for e in filtered_events
                        if event_key(e) not in visible_plan_keys and e['score'] >= 6.5]
    other_top_events.sort(key=lambda e: (hour_to_min(e['hora']), -e['score']))
    return {'filtrados': filtered_events, 'plan': daily_plan,
            'seleccionados': selected_events, 'alternativas': other_top_events[:MAX_OTHER_EVENTS]}
