from typing import Union
from sqlalchemy.orm import Session

from .dbmodel import Pokemons, PokemonsAbilities, PokemonsStats, PokemonsTypes
from ..scrapers.spider import PokeAPISpider


def query_pokemons(name: str, session: Session) -> list:
    """Simple func."""
    return Pokemons().get_by_name(session, name)


def create_pokemon(spider: PokeAPISpider, results: list) -> None:
    """Handles the process of insert.

    :param spider: instance of PokeAPISpider, [PokeAPISpider]
    :param results: results that are going to be processed, [list]
    """
    new_entity_guid = spider.delete_and_update(
        Pokemons,
        [elements["pokemons"] for elements in results],
        None,
        "guid",
        return_pokemon_guid=True,
    )
    spider.delete_and_update(
        PokemonsAbilities,
        [elements["abilities"] for elements in results],
        new_entity_guid,
        "pokemons_guid",
    )
    spider.delete_and_update(
        PokemonsStats,
        [elements["stats"] for elements in results],
        new_entity_guid,
        "pokemons_guid",
    )
    spider.delete_and_update(
        PokemonsTypes,
        [elements["types"] for elements in results],
        new_entity_guid,
        "pokemons_guid",
    )


def update_pokemon(spider: PokeAPISpider, pokemon_guid: str, results: list) -> None:
    """Handles the process of update.

    :param spider: instance of PokeAPISpider, [PokeAPISpider]
    :param results: results that are going to be processed, [list]
    """
    spider.delete_and_update(
        PokemonsAbilities,
        [elements["abilities"] for elements in results],
        pokemon_guid,
        "pokemons_guid",
    )
    spider.delete_and_update(
        PokemonsStats,
        [elements["stats"] for elements in results],
        pokemon_guid,
        "pokemons_guid",
    )
    spider.delete_and_update(
        PokemonsTypes,
        [elements["types"] for elements in results],
        pokemon_guid,
        "pokemons_guid",
    )
