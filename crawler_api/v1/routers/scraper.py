import asyncio

from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from aiohttp import ClientSession
from pydantic import StrictStr

from crawler_api.v1.models.dbmodel import (
    Pokemons,
    PokemonsAbilities,
    PokemonsTypes,
    PokemonsStats,
)

from ..database.orm import get_db
from ..scrapers.spider import PokeAPISpider
from ..enums.enums import Status
from ..models import utils


router = APIRouter()


async def parallel_request(
    clientSession: ClientSession, urls_list: list, scrape_func: Any
) -> list():
    results = await asyncio.gather(
        *[scrape_func(clientSession, url) for url in urls_list]
    )
    return results


@router.post(
    "/scraper",
    description="Scrape Pokémons",
)
async def scrape_pokemons_from_pokeapi(session: Session = Depends(get_db)):
    """
    Scrapes all Pokémons from `https://pokeapi.co/api/v2/pokemon`.

    """
    try:
        PokeAPISpider.prepare(session)
        spider = PokeAPISpider(session)
        urls = spider.get_urls()
        clientSession = ClientSession()
        results = await parallel_request(clientSession, urls, spider.scrape)
        spider.bulk_insert(Pokemons, [elements["pokemons"] for elements in results])
        spider.bulk_insert(
            PokemonsAbilities, [elements["abilities"] for elements in results]
        )
        spider.bulk_insert(PokemonsStats, [elements["stats"] for elements in results])
        spider.bulk_insert(PokemonsTypes, [elements["types"] for elements in results])
        session.commit()
        return Status.success.value
    except (Exception, KeyError) as e:
        session.rollback()
        raise HTTPException(status_code=409, detail=e.args)


@router.patch(
    "/scraper/{pokemon_name}",
    description="Search and update or add Pokémon",
)
async def update_pokemons_from_pokeapi(
    session: Session = Depends(get_db),
    pokemon_name: StrictStr = Query(..., description="Name of the Pokémon"),
):
    """
    Scrape Pokémon from `https://pokeapi.co/api/v2/pokemon/{pokemon_name}`.

    """
    try:
        spider = PokeAPISpider(session)
        url = [spider.get_url(pokemon_name)]
        clientSession = ClientSession()
        results = await parallel_request(clientSession, url, spider.scrape)

        # get pokemon guid if exists
        pokemon_guid = None
        if len(results):
            # don't like to select element int this way but I'm quite sure that no IndexError will be raised
            pokemon_guid = results[0]["pokemons"][0].exists(session)
            if not pokemon_guid:
                utils.create_pokemon(spider, results)
            elif pokemon_guid:
                utils.update_pokemon(spider, pokemon_guid, results)
            session.commit()
        return Status.success.value
    except (Exception, KeyError) as e:
        session.rollback()
        raise HTTPException(status_code=404, detail=e.args)
