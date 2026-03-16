import pandas as pd
import sqlite3

# Create database connection
db_path = 'baseball.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Read CSV files
people_df = pd.read_csv('people.csv')
teams_df = pd.read_csv('teams.csv')
batting_df = pd.read_csv('Batting.csv')

# Drop the ID column from people as it's redundant with playerID
people_df = people_df.drop('ID', axis=1)

# Create people table
cursor.execute('''
    CREATE TABLE people (
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

# Create teams table with composite primary key
cursor.execute('''
    CREATE TABLE teams (
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

# Create batting table with composite primary key and foreign keys
cursor.execute('''
    CREATE TABLE batting (
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

# Insert data into people table
for _, row in people_df.iterrows():
    cursor.execute('''
        INSERT INTO people VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', tuple(row))

# Insert data into teams table
for _, row in teams_df.iterrows():
    cursor.execute('''
        INSERT INTO teams VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', tuple(row))

# Insert data into batting table
for _, row in batting_df.iterrows():
    cursor.execute('''
        INSERT INTO batting VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', tuple(row))

# Commit changes and close connection
conn.commit()
conn.close()

print(f"Database '{db_path}' created successfully!")
print("Tables created: people, teams, batting")
print("Primary keys and foreign keys configured as specified.")
