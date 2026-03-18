import pandas as pd
import sqlite3


def seed_database(db_path='baseball.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    people_df = pd.read_csv('people.csv').drop('ID', axis=1)
    teams_df = pd.read_csv('teams.csv')
    batting_df = pd.read_csv('Batting.csv')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people (
            playerID TEXT PRIMARY KEY,
            birthYear INTEGER,
            birthMonth INTEGER,
            birthDay INTEGER,
            birthCity TEXT,
            birthCountry TEXT,
            birthState TEXT,
            deathYear INTEGER,
            deathMonth INTEGER,
            deathDay INTEGER,
            deathCountry TEXT,
            deathState TEXT,
            deathCity TEXT,
            nameFirst TEXT,
            nameLast TEXT,
            nameGiven TEXT,
            weight INTEGER,
            height INTEGER,
            bats TEXT,
            throws TEXT,
            debut TEXT,
            bbrefID TEXT,
            finalGame TEXT,
            retroID TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            yearID INTEGER,
            teamID TEXT,
            lgID TEXT,
            franchID TEXT,
            divID TEXT,
            Rank INTEGER,
            G INTEGER,
            Ghome INTEGER,
            W INTEGER,
            L INTEGER,
            DivWin TEXT,
            WCWin TEXT,
            LgWin TEXT,
            WSWin TEXT,
            R INTEGER,
            AB INTEGER,
            H INTEGER,
            "2B" INTEGER,
            "3B" INTEGER,
            HR INTEGER,
            BB INTEGER,
            SO INTEGER,
            SB INTEGER,
            CS INTEGER,
            HBP INTEGER,
            SF INTEGER,
            RA INTEGER,
            ER INTEGER,
            ERA REAL,
            CG INTEGER,
            SHO INTEGER,
            SV INTEGER,
            IPouts INTEGER,
            HA INTEGER,
            HRA INTEGER,
            BBA INTEGER,
            SOA INTEGER,
            E INTEGER,
            DP INTEGER,
            FP REAL,
            name TEXT,
            park TEXT,
            attendance INTEGER,
            BPF INTEGER,
            PPF INTEGER,
            teamIDBR TEXT,
            teamIDlahman45 TEXT,
            teamIDretro TEXT,
            PRIMARY KEY (yearID, teamID)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS batting (
            playerID TEXT,
            yearID INTEGER,
            stint INTEGER,
            teamID TEXT,
            lgID TEXT,
            G INTEGER,
            AB INTEGER,
            R INTEGER,
            H INTEGER,
            "2B" INTEGER,
            "3B" INTEGER,
            HR INTEGER,
            RBI INTEGER,
            SB INTEGER,
            CS INTEGER,
            BB INTEGER,
            SO INTEGER,
            IBB INTEGER,
            HBP INTEGER,
            SH INTEGER,
            SF INTEGER,
            GIDP INTEGER,
            PRIMARY KEY (playerID, yearID, stint),
            FOREIGN KEY (playerID) REFERENCES people(playerID),
            FOREIGN KEY (yearID, teamID) REFERENCES teams(yearID, teamID)
        )
    ''')

    for _, row in people_df.iterrows():
        cursor.execute('''
            INSERT OR IGNORE INTO people VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(row))

    for _, row in teams_df.iterrows():
        cursor.execute('''
            INSERT OR IGNORE INTO teams VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(row))

    for _, row in batting_df.iterrows():
        cursor.execute('''
            INSERT OR IGNORE INTO batting VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(row))

    conn.commit()
    conn.close()
    print(f"Database '{db_path}' seeded successfully.")


if __name__ == '__main__':
    seed_database()
    print("Tables created: people, teams, batting")
    print("Primary keys and foreign keys configured as specified.")

