import csv
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from sqlmodel import select, Session
from models import engine, Teams, populate_db

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


def to_int(value):
    if value is None or value == "":
        return 0

    try:
        return int(value)
    except ValueError:
        return 0


def load_player_name_map():
    name_map = {}

    with open("people.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    populate_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/years")
async def get_years():
    with Session(engine) as session:
        years = session.exec(select(Teams.yearID).distinct().order_by(Teams.yearID)).all()
        return sorted(years)

@app.get("/teams")
async def get_teams(year: int):
    teams = []
    year_text = str(year)

    with open("teams.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            if row.get("yearID") != year_text:
                continue

            team_name = row.get("name")
            team_id = row.get("teamID")
            lead_code = row.get("lgID")
            division_code = row.get("divID")
            wins = to_int(row.get("W"))

            if not team_name or not team_id:
                continue

            if lead_code in LEAGUE_NAMES:
                lead_name = LEAGUE_NAMES[lead_code]
            elif lead_code:
                lead_name = lead_code
            else:
                lead_name = "Unknown League"

            if division_code in DIVISION_NAMES:
                division_name = DIVISION_NAMES[division_code]
            elif division_code:
                division_name = division_code
            else:
                division_name = "No Division"

            team_record = {
                "name": team_name,
                "lead": lead_name,
                "division": division_name,
                "teamID": team_id,
                "wins": wins,
            }

            already_added = False
            for existing in teams:
                same_team = existing["teamID"] == team_record["teamID"]
                same_league = existing["lead"] == team_record["lead"]
                same_division = existing["division"] == team_record["division"]
                same_name = existing["name"] == team_record["name"]
                same_wins = existing["wins"] == team_record["wins"]

                if same_team and same_league and same_division and same_name and same_wins:
                    already_added = True
                    break

            if not already_added:
                teams.append(team_record)

    teams.sort(key=lambda team: (team["lead"], team["division"], -team["wins"], team["name"]))
    return teams


@app.get("/players")
async def get_players(year: int, teamID: str):
    player_ids = []
    year_text = str(year)

    with open("Batting.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
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
        players.append(
            {
                "playerID": player_id,
                "name": name_map.get(player_id, player_id),
            }
        )

    players.sort(key=lambda player: player["name"])
    return players


@app.get("/player-stats")
async def get_player_stats(year: int, teamID: str, playerID: str):
    stat_keys = [
        "G", "AB", "R", "H", "2B", "3B", "HR", "RBI", "SB",
        "CS", "BB", "SO", "IBB", "HBP", "SH", "SF", "GIDP"
    ]

    totals = {
        "G": 0,
        "AB": 0,
        "R": 0,
        "H": 0,
        "2B": 0,
        "3B": 0,
        "HR": 0,
        "RBI": 0,
        "SB": 0,
        "CS": 0,
        "BB": 0,
        "SO": 0,
        "IBB": 0,
        "HBP": 0,
        "SH": 0,
        "SF": 0,
        "GIDP": 0,
    }

    year_text = str(year)

    with open("Batting.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            same_year = row.get("yearID") == year_text
            same_team = row.get("teamID") == teamID
            same_player = row.get("playerID") == playerID

            if not same_year or not same_team or not same_player:
                continue

            for key in stat_keys:
                totals[key] += to_int(row.get(key))

    batting_average = 0.0
    if totals["AB"] > 0:
        batting_average = round(totals["H"] / totals["AB"], 3)

    name_map = load_player_name_map()

    return {
        "playerID": playerID,
        "name": name_map.get(playerID, playerID),
        "teamID": teamID,
        "year": year,
        "batting_average": batting_average,
        "stats": totals,
    }


app.mount("/", StaticFiles(directory="static", html=True), name="static")