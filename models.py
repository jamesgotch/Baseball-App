from typing import Optional
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session, select
from pydantic import ConfigDict

# Database configuration
DATABASE_URL = "sqlite:///baseball.db"
engine = create_engine(DATABASE_URL, echo=False)


class People(SQLModel, table=True):
    playerID: str = Field(primary_key=True)
    birthYear: Optional[int] = None
    birthMonth: Optional[int] = None
    birthDay: Optional[int] = None
    birthCity: Optional[str] = None
    birthCountry: Optional[str] = None
    birthState: Optional[str] = None
    deathYear: Optional[int] = None
    deathMonth: Optional[int] = None
    deathDay: Optional[int] = None
    deathCountry: Optional[str] = None
    deathState: Optional[str] = None
    deathCity: Optional[str] = None
    nameFirst: Optional[str] = None
    nameLast: Optional[str] = None
    nameGiven: Optional[str] = None
    weight: Optional[int] = None
    height: Optional[int] = None
    bats: Optional[str] = None
    throws: Optional[str] = None
    debut: Optional[str] = None
    bbrefID: Optional[str] = None
    finalGame: Optional[str] = None
    retroID: Optional[str] = None

    # Relationship to batting records
    batting_records: list["Batting"] = Relationship(back_populates="player")


class Teams(SQLModel, table=True):
    model_config = ConfigDict(populate_by_name=True)

    yearID: int = Field(primary_key=True)
    teamID: str = Field(primary_key=True)
    lgID: Optional[str] = None
    franchID: Optional[str] = None
    divID: Optional[str] = None
    Rank: Optional[int] = None
    G: Optional[int] = None
    Ghome: Optional[int] = None
    W: Optional[int] = None
    L: Optional[int] = None
    DivWin: Optional[str] = None
    WCWin: Optional[str] = None
    LgWin: Optional[str] = None
    WSWin: Optional[str] = None
    R: Optional[int] = None
    AB: Optional[int] = None
    H: Optional[int] = None
    double_b: Optional[int] = Field(None, alias="2B", validation_alias="2B")
    triple_b: Optional[int] = Field(None, alias="3B", validation_alias="3B")
    HR: Optional[int] = None
    BB: Optional[int] = None
    SO: Optional[int] = None
    SB: Optional[int] = None
    CS: Optional[int] = None
    HBP: Optional[int] = None
    SF: Optional[int] = None
    RA: Optional[int] = None
    ER: Optional[int] = None
    ERA: Optional[float] = None
    CG: Optional[int] = None
    SHO: Optional[int] = None
    SV: Optional[int] = None
    IPouts: Optional[int] = None
    HA: Optional[int] = None
    HRA: Optional[int] = None
    BBA: Optional[int] = None
    SOA: Optional[int] = None
    E: Optional[int] = None
    DP: Optional[int] = None
    FP: Optional[float] = None
    name: Optional[str] = None
    park: Optional[str] = None
    attendance: Optional[int] = None
    BPF: Optional[int] = None
    PPF: Optional[int] = None
    teamIDBR: Optional[str] = None
    teamIDlahman45: Optional[str] = None
    teamIDretro: Optional[str] = None


class Batting(SQLModel, table=True):
    model_config = ConfigDict(populate_by_name=True)

    playerID: str = Field(primary_key=True, foreign_key="people.playerID")
    yearID: int = Field(primary_key=True, foreign_key="teams.yearID")
    stint: int = Field(primary_key=True)
    teamID: str = Field(foreign_key="teams.teamID")
    lgID: Optional[str] = None
    G: Optional[int] = None
    AB: Optional[int] = None
    R: Optional[int] = None
    H: Optional[int] = None
    double_b: Optional[int] = Field(None, alias="2B", validation_alias="2B")
    triple_b: Optional[int] = Field(None, alias="3B", validation_alias="3B")
    HR: Optional[int] = None
    RBI: Optional[int] = None
    SB: Optional[int] = None
    CS: Optional[int] = None
    BB: Optional[int] = None
    SO: Optional[int] = None
    IBB: Optional[int] = None
    HBP: Optional[int] = None
    SH: Optional[int] = None
    SF: Optional[int] = None
    GIDP: Optional[int] = None

    # Relationship to People
    player: Optional[People] = Relationship(back_populates="batting_records")


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def populate_db():
    """Populate the database from CSV files. Skips if data already exists."""
    import pandas as pd

    with Session(engine) as session:
        if session.exec(select(People)).first():
            print("Database already populated, skipping.")
            return

        people_df = pd.read_csv('people.csv').drop('ID', axis=1)
        teams_df = pd.read_csv('teams.csv')
        batting_df = pd.read_csv('Batting.csv')

        def clean(d):
            return {k: None if pd.isna(v) else v for k, v in d.items()}

        for _, row in people_df.iterrows():
            session.add(People(**clean(row.to_dict())))

        for _, row in teams_df.iterrows():
            session.add(Teams.model_validate(clean(row.to_dict())))

        for _, row in batting_df.iterrows():
            session.add(Batting.model_validate(clean(row.to_dict())))

        session.commit()
        print("Database populated successfully.")


def get_session():
    """Get a new database session."""
    return Session(engine)
