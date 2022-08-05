import itertools
from json import JSONDecodeError
from typing import Union
import requests

from aiohttp import ClientSession
from requests.exceptions import RequestException
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

from ..models.dbmodel import Pokemons, PokemonsAbilities, PokemonsStats, PokemonsTypes


class PokeAPISpider:
    """Class that handles the procedure of find, collect and store all the pokemons
    at `https://pokeapi.co/api/v2/pokemon`.
    """

    baseurl = "https://pokeapi.co/api/v2/pokemon"

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_urls(self) -> list:
        """Finds and returns a list of all the urls to scrape.

        :return: _description_
        :rtype: list
        """
        urls = list()
        try:
            response = requests.get(self.baseurl).json()
            count = response["count"] if "count" in response else None
            if count:
                for n in range(1, count + 1):
                    urls.append(self.baseurl + f"/{n}/")
        except RequestException:
            pass
        return urls

    def get_url(self, name: str) -> str:
        """Returns a single url.

        :param: name: the name of the Pokémon to get the url of.
        """
        return self.baseurl + f"/{name}"

    @classmethod
    def prepare(cls, session: Session) -> None:
        """Performs a removal of all record inside the DB.
        This is dengerous but needed considering that the scraper could be run
        a second time very far from the first: this is more useful then add or
        modify N entities by a single call.
        """
        # the order matters
        PokemonsAbilities.erase(session)
        PokemonsStats.erase(session)
        PokemonsTypes.erase(session)
        Pokemons.erase(session)
        session.flush()
        session.commit()

    async def scrape(self, clientSession: ClientSession, url: str) -> dict:
        """Scrape the PokeAPI url. If the response is 200, then build the
        entities according to the Pokemons, PokemonsAbilities, PokemonsStats or
        PokemonsTypes model.

        Returns a dict representing the relations of the entities.

        Note that, in this case, the `guid` field is given to the Pokemon entity
        and the passed to its attributes.

        :param clientSession: ClientSession requests instance, [ClientSession]
        :param url: url to scrape, [str]
        """
        # Here's some variables need to be declare
        rv = {"pokemons": list(), "abilities": list(), "types": list(), "stats": list()}
        all_abilities = list()
        all_types = list()
        all_stats = list()
        response = None

        try:
            # Make request
            request = await clientSession.get(url, timeout=10)

            if request.status == 200:
                response = await request.json()
                await request.read()

                # if a repsonse is returned, starts entities build process
                if response:
                    # create the Pokemon
                    pokemon = Pokemons(
                        **{
                            "name": response["name"],
                            "description": response["name"].title() + " short desc",
                        },
                    )
                    pokemon(generate_guid=True)

                    # create abilities attributes
                    if "abilities" in response:
                        if len(response["abilities"]):
                            for ability in response["abilities"]:
                                pokemon_ability = PokemonsAbilities(
                                    **{
                                        "name": ability["ability"]["name"],
                                        "url": ability["ability"]["url"],
                                        "is_hidden": ability["is_hidden"],
                                        "slot": ability["slot"],
                                        "pokemons_guid": pokemon.guid,
                                    }
                                )
                                pokemon_ability(generate_guid=True)
                                all_abilities.append(pokemon_ability)

                    # create stats attributes
                    if "stats" in response:
                        if len(response["stats"]):
                            for stat in response["stats"]:
                                pokemon_stat = PokemonsStats(
                                    **{
                                        "name": stat["stat"]["name"],
                                        "url": stat["stat"]["url"],
                                        "base_stat": stat["base_stat"],
                                        "effort": stat["effort"],
                                        "pokemons_guid": pokemon.guid,
                                    }
                                )
                                pokemon_stat(generate_guid=True)
                                all_stats.append(pokemon_stat)

                    # create types attributes
                    if "types" in response:
                        if len(response["types"]):
                            for type_ in response["types"]:
                                pokemon_type = PokemonsTypes(
                                    **{
                                        "name": type_["type"]["name"],
                                        "url": type_["type"]["url"],
                                        "slot": type_["slot"],
                                        "pokemons_guid": pokemon.guid,
                                    }
                                )
                                pokemon_type(generate_guid=True)
                                all_types.append(pokemon_type)

                    # store entiies in return value dict
                    rv["pokemons"].append(pokemon)
                    rv["abilities"].extend(all_abilities)
                    rv["types"].extend(all_types)
                    rv["stats"].extend(all_stats)
        except RequestException:
            pass
        return rv

    def bulk_insert(self, class_: object, request: list) -> None:
        """Bulk insert of records to optimize performances.

        :param class_: the class of the entity instance. Can be Pokemons, PokemonsAbilities, PokemonsTypes or PokemonsStats.
        :param request: the entities that are going to be persisted in the related table.
        """
        items = list(itertools.chain(*request))

        # if element is not an instance of the class is skipped: probably the scrape
        # found empty body from the http request
        entities = [
            class_.model_(**element.__dict__)
            for element in items
            if isinstance(element, class_)
        ]
        self.session.bulk_save_objects(entities)
        self.session.flush()

    def delete_and_update(
        self,
        class_: object,
        request: list,
        pokemon_guid: Union[str, None],
        filter_attr: str,
        return_pokemon_guid: bool = False,
    ) -> Union[str, None]:
        """Perform one-by-one delete and add of updated Pokémons.

        :param class_: the class of the entity instance. Can be Pokemons, PokemonsAbilities, PokemonsTypes or PokemonsStats.
        :param request: the entities that are going to be persisted in the related table.
        """
        items = list(itertools.chain(*request))
        entities = [
            class_.model_(**element.__dict__)
            for element in items
            if isinstance(element, class_)
        ]

        # perform delete of existing elements if pokemon_guid is not None
        if pokemon_guid and class_ != Pokemons:
            self.session.query(class_.model_).filter(
                getattr(class_.model_, filter_attr) == pokemon_guid
            ).delete(synchronize_session=False)
            self.session.flush()

            for entity in entities:
                if hasattr(entity, filter_attr):
                    setattr(entity, filter_attr, pokemon_guid)

        # add new records for entitiy
        self.session.bulk_save_objects(entities)
        self.session.flush()

        if return_pokemon_guid:
            return entities[0].guid
