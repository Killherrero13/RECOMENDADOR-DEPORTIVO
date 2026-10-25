"""Preferencias originales: valores conservados sin cambios."""

EVENT_DURATION = 120      # minutos

MAX_OVERLAP = 30          # minutos

DAY_START = 7 * 60      # 07:00

DAY_END = 23 * 60 + 30 # 23:30

TOP_ATP = {"djokovic", "alcaraz", "medvedev", "sinner", "zverev"}

TOP_ATP_20 = TOP_ATP | {"rublev", "hurkacz", "fritz", "tsitsipas", "rune"}

TOP_NCAA = {"kansas", "duke", "kentucky", "north carolina", "michigan", "purdue", "wisconsin", "ucla"}

TOP_ACB = {"barça", "barcelona", "real madrid", "valencia", "joventut", "gran canaria", "baskonia"}

BIG_FOOTBALL_TEAMS = {
    "real madrid", "fc barcelona", "barça", "bayern",
    "inter", "napoli", "arsenal", "manchester", "ajax", "milan",
    "atletico de madrid", "psg"
}

NBA_TOP_TEAMS = {"lakers", "warriors", "celtics", "nuggets", "suns", "clippers"}

POSITIVE_CHANNELS = {"dazn", "movistar", "teledeporte", "rtve play", "youtube"}

FREE_CHANNELS = {"youtube", "teledeporte", "rtve play"}

NBA_TEAM_AFFINITY = {
    "celtics": 0.85,
    "warriors": 0.75,
    "nuggets": 0.70,
    "timberwolves": 0.70,
    "spurs": 0.60,
    "rockets": 0.60,
    "pacers": 0.55,
    "raptors": 0.50,
    "hornets": 0.45,
    "pelicans": 0.35,
    "clippers": 0.30,
    "kings": 0.30,
    "bucks": 0.20,
    "hawks": 0.15,
    "nets": 0.15,
    "bulls": 0.10,
    "magic": 0.05,
    "wizards": 0.00,
    "pistons": 0.00,
    "jazz": 0.00,
    "trail blazers": 0.00,
    "thunder": -0.45,
    "knicks": -0.40,
    "heat": -0.40,
    "76ers": -0.35
}

FOOTBALL_TEAM_AFFINITY = {
    "real madrid": 0.70,
    "fc barcelona": 0.81,
    "atletico madrid": 0.99,
    "sevilla fc": 0.65,
    "real sociedad": 0.51,
    "villarreal": 0.47,
    "getafe": 0.35,
    "rayo vallecano": 0.33,
    "osasuna": 0.28,
    "celta": 0.42,
    "valencia": 0.50,
    "betis": 0.55,
    "mallorca": 0.25,
    "girona": 0.30,
    "athletic": 0.51,
    "elche": 0.18,
    "espanyol": 0.22,
    "alaves": 0.24,
    "levante": 0.11,
    "oviedo": 0.15,

    "arsenal": 0.70,
    "manchester city": 0.77,
    "liverpool": 0.97,
    "manchester united": 0.68,
    "chelsea": 0.70,
    "tottenham": 0.68,
    "aston villa": 0.88,
    "newcastle united": 0.60,
    "west ham": 0.50,
    "everton": 0.45,
    "crystal palace": 0.38,
    "wolves": 0.35,
    "bournemouth": 0.33,
    "nottingham forest": 0.30,
    "brighton": 0.55,
    "fulham": 0.42,
    "brentford": 0.40,
    "leeds united": 0.36,
    "burnley": 0.28,
    "sunderland": 0.20,

    "inter milan": 0.8,
    "ac milan": 0.65,
    "juventus": 0.60,
    "napoli": 0.90,
    "roma": 0.88,
    "atalanta": 0.77,
    "lazio": 0.58,
    "fiorentina": 0.40,
    "torino": 0.45,
    "udinese": 0.40,
    "sassuolo": 0.35,
    "monza": 0.30,
    "lecce": 0.28,
    "empoli": 0.25,
    "bologna": 0.32,
    "verona": 0.20,
    "salernitana": 0.18,
    "frosinone": 0.16,
    "cagliari": 0.45,
    "parma": 0.12,
    "genoa": 0.2,
    "us cremonese": 0.3,

    "bayern munich": 0.79,
    "borussia dortmund": 1,
    "bayer leverkusen": 0.71,
    "rb leipzig": 0.68,
    "schalke04": 0.55,
    "wolfsburg": 0.60,
    "eintracht frankfurt": 0.64,
    "hoffenheim": 0.58,
    "mainz": 0.50,
    "koln": 0.50,
    "freiburg": 0.48,
    "union berlin": 0.57,
    "bochum": 0.30,
    "stuttgart": 0.60,
    "augsburg": 0.28,
    "borussia moenchengladbach": 0.35,
    "werder bremen": 0.42,
    "hannover": 0.18,
    "karlsruhe": 0.20,
    "hertha berlin": 0.25,
    "hamburg sv": 0.2,

    "psg": 0.77,
    "lens": 0.88,
    "olympique marsella": 0.86,
    "lille": 0.75,
    "rennes": 0.70,
    "lyon": 0.68,
    "monaco": 0.73,
    "strasbourg": 0.55,
    "montpellier": 0.50,
    "nice": 0.48,
    "toulouse": 0.44,
    "brest": 0.38,
    "reims": 0.35,
    "clermont foot": 0.30,
    "auxerre": 0.28,
    "angers": 0.22,
    "troyes": 0.20,
    "lorient": 0.32,
    "metz": 0.18,
    "caen": 0.10
}

FOOTBALL_DERBIES = {
    # ======================
    # ESPAÑA
    # ======================
    ("real madrid", "fc barcelona"): 2.0,
    ("atletico madrid", "real madrid"): 1.6,
    ("atletico madrid", "fc barcelona"): 1.4,
    ("fc barcelona", "valencia"): 1.4, # Added for Barcelona vs Valencia
    ("valencia", "fc barcelona"): 1.4, # Added for Valencia vs Barcelona
    ("sevilla fc", "betis"): 1.5,
    ("athletic", "real sociedad"): 1.4,
    ("valencia", "levante"): 1.2,
    ("valencia", "villarreal"): 1.3,        # Derbi de la Comunidad
    ("deportivo la coruna", "celta vigo"): 1.4,  # Derbi gallego
    ("real zaragoza", "sd huesca"): 1.1,     # Derbi aragonés
    ("cd tenerife", "ud las palmas"): 1.3,   # Derbi canario

    # ======================
    # INGLATERRA
    # ======================
    ("arsenal", "tottenham"): 1.5,
    ("manchester united", "manchester city"): 1.6,
    ("liverpool", "manchester united"): 1.7,
    ("liverpool", "everton"): 1.7,
    ("chelsea", "arsenal"): 1.3,
    ("chelsea", "tottenham"): 1.4,
    ("manchester city", "liverpool"): 1.4,  # Rivalidad moderna
    ("west ham", "millwall"): 1.6,
    ("leeds united", "manchester united"): 1.6,
    ("aston villa", "birmingham city"): 1.2,

    # ======================
    # ITALIA
    # ======================
    ("inter milan", "ac milan"): 1.8,
    ("roma", "lazio"): 1.6,
    ("juventus", "inter milan"): 1.5,
    ("juventus", "ac milan"): 1.4,
    ("napoli", "roma"): 1.3,
    ("napoli", "juventus"): 1.5,
    ("genoa", "sampdoria"): 1.3,
    ("atalanta", "brescia"): 1.1,
    ("torino", "juventus"): 1.4,

    # ======================
    # ALEMANIA
    # ======================
    ("bayern munich", "borussia dortmund"): 1.8,
    ("schalke04", "borussia dortmund"): 1.5,
    ("hamburger sv", "werder bremen"): 1.4,   # Nordderby
    ("bayern munich", "1860 munich"): 1.3,
    ("eintracht frankfurt", "mainz"): 1.2,
    ("hertha berlin", "union berlin"): 1.4,  # Derbi de Berlín

    # ======================
    # FRANCIA
    # ======================
    ("psg", "olympique marsella"): 1.7,
    ("psg", "paris fc"): 1.6,
    ("olympique lyon", "saint-etienne"): 1.6,  # Derbi del Ródano
    ("lille", "lens"): 1.5,                    # Derbi del Norte
    ("monaco", "nice"): 1.3,
}

TENNIS_PLAYER_AFFINITY = {
    "alcaraz": 2.5,
    "djokovic": 1.8,
    "sinner": 1.6,
    "medvedev": 1.4,
    "zverev": 1.2,
    "tsitsipas": 1.0,
    "rublev": 1.0
}

ALLOWED_FOOTBALL_COMPETITIONS = [
    "laliga", "ea sports", "hypermotion", "premier", "bundesliga",
    "serie a", "ligue 1", "eredivisie",
    "fa cup", "emirates",
    "copa del rey", "coppa",
    "copa de francia", "coupe de france",
    "supercopa", "scottish premiership", "copa africana de naciones",
    "cham", "europa league", "champions league", "conference league", "fifa",
    "liga portuguesa", "coppa italia", "primera division argentina", "serie a brasil",
    "jupiler pro league", "nations league", "eurocopa", "copa america",
    "copa del mundo", "world cup"
]

EXCLUDED_FOOTBALL_COMPETITIONS = [
    "bahrain",
    "northern irish",
    "northern ireland",
    "coppa italia serie c",
    "premier league 2", "ucrania",
    "championnat national","futures","liga premier islandia", "afc champions league"
]

MAX_OTHER_EVENTS = 8
