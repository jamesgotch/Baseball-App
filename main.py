from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from sqlmodel import select, Session
from models import engine, Batting, People, Teams, populate_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    populate_db()
    yield


app = FastAPI(lifespan=lifespan)

@app.get("/years")
async def get_years():
    with Session(engine) as session:
        years = session.exec(select(Teams.yearID).distinct()).all()
        return sorted(years)


app.mount("/", StaticFiles(directory="static", html=True), name="static")