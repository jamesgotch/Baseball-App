import csv
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

TEAMS_FILE = "teams.csv"
PEOPLE_FILE = "people.csv"
BATTING_FILE = "Batting.csv"

LEAGUE_NAMES = {
    "AL": "American League",
    "NL": "National League",
    "AA": "American Association",
    "NA": "National Association",
    "UA": "Union Association",
    "PL": "Players League",
    "FL": "Federal League",
}

DIVISION_NAMES = {
    "E": "East",
    "W": "West",
    "C": "Central",
}

STAT_KEYS = [
    "G", "AB", "R", "H", "2B", "3B", "HR", "RBI", "SB",
    "CS", "BB", "SO", "IBB", "HBP", "SH", "SF", "GIDP"
]


def to_int(value):
    if value is None or value == "":
        return 0

    try:
        return int(value)
    except ValueError:
        return 0


def read_csv_rows(filename):
    with open(filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


def get_league_name(league_code):
    if league_code in LEAGUE_NAMES:
        return LEAGUE_NAMES[league_code]

    if league_code:
        return league_code

    return "Unknown League"


def get_division_name(division_code):
    if division_code in DIVISION_NAMES:
        return DIVISION_NAMES[division_code]

    if division_code:
        return division_code

    return "No Division"


def make_empty_stats():
    totals = {}

    for key in STAT_KEYS:
        totals[key] = 0

    return totals


def build_team_record(row):
    team_name = row.get("name")
    team_id = row.get("teamID")

    if not team_name or not team_id:
        return None

    league_name = get_league_name(row.get("lgID"))
    division_name = get_division_name(row.get("divID"))

    return {
        "name": team_name,
        "league": league_name,
        "lead": league_name,
        "division": division_name,
        "teamID": team_id,
        "wins": to_int(row.get("W")),
    }


def build_player_record(player_id, name_map):
    return {
        "playerID": player_id,
        "name": name_map.get(player_id, player_id),
    }


def calculate_batting_average(stats):
    at_bats = stats["AB"]

    if at_bats == 0:
        return 0.0

    return round(stats["H"] / at_bats, 3)


def load_player_name_map():
    name_map = {}

    for row in read_csv_rows(PEOPLE_FILE):
        player_id = row.get("playerID")

        if not player_id:
            continue

        first_name = row.get("nameFirst") or ""
        last_name = row.get("nameLast") or ""
        full_name = f"{first_name} {last_name}".strip()

        if full_name:
            name_map[player_id] = full_name
        else:
            name_map[player_id] = player_id

    return name_map


app = FastAPI()

@app.get("/years")
async def get_years():
    years = set()

    for row in read_csv_rows(TEAMS_FILE):
        year_value = row.get("yearID")

        if not year_value:
            continue

        try:
            years.add(int(year_value))
        except ValueError:
            continue

    return sorted(years)


@app.get("/teams")
async def get_teams(year: int):
    teams = []
    seen_teams = set()
    year_text = str(year)

    for row in read_csv_rows(TEAMS_FILE):
        if row.get("yearID") != year_text:
            continue

        team_record = build_team_record(row)

        if team_record is None:
            continue

        team_key = (
            team_record["teamID"],
            team_record["league"],
            team_record["division"],
            team_record["name"],
            team_record["wins"],
        )

        if team_key in seen_teams:
            continue

        seen_teams.add(team_key)
        teams.append(team_record)

    teams.sort(key=lambda team: (team["league"], team["division"], -team["wins"], team["name"]))
    return teams


@app.get("/players")
async def get_players(year: int, teamID: str):
    player_ids = []
    year_text = str(year)

    for row in read_csv_rows(BATTING_FILE):
        same_year = row.get("yearID") == year_text
        same_team = row.get("teamID") == teamID

        if not same_year or not same_team:
            continue

        player_id = row.get("playerID")

        if player_id and player_id not in player_ids:
            player_ids.append(player_id)

    name_map = load_player_name_map()
    players = []

    for player_id in player_ids:
        players.append(build_player_record(player_id, name_map))

    players.sort(key=lambda player: player["name"])
    return players


@app.get("/player-stats")
async def get_player_stats(year: int, teamID: str, playerID: str):
    totals = make_empty_stats()

    year_text = str(year)

    for row in read_csv_rows(BATTING_FILE):
        same_year = row.get("yearID") == year_text
        same_team = row.get("teamID") == teamID
        same_player = row.get("playerID") == playerID

        if not same_year or not same_team or not same_player:
            continue

        for key in STAT_KEYS:
            totals[key] += to_int(row.get(key))

    name_map = load_player_name_map()

    return {
        "playerID": playerID,
        "name": name_map.get(playerID, playerID),
        "teamID": teamID,
        "year": year,
        "batting_average": calculate_batting_average(totals),
        "stats": totals,
    }


app.mount("/", StaticFiles(directory="static", html=True), name="static")