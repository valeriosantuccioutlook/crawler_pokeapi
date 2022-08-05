from fastapi import FastAPI

from .routers import scraper, pokemons

app = FastAPI(
    title="Crawler",
    description="PokeAPI Crawler",
    version="1.0.0",
)

app.include_router(
    pokemons.router,
    tags=["Pokemons"],
)

app.include_router(
    scraper.router,
    tags=["Pokemons Scraper"],
)
