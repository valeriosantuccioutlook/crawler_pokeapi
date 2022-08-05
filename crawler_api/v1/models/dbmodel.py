import uuid

from uuid import UUID
from typing import Union

from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

from ..database.orm import model


class Super:

    baseurl = "https://pokeapi.co/api/v2/pokemon"

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def __call__(self, guid: UUID = None, generate_guid: bool = False) -> object:
        if guid:
            self.__dict__.update({"guid": str(guid), **self.__dict__})
        if not guid and generate_guid:
            guid = uuid.uuid4()
            self.__dict__.update({"guid": str(guid), **self.__dict__})
        return self


class Pokemons(Super):
    """Pokemons class reflecting the `pokemons` table."""

    model_ = model("pokemons")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def __call__(self, guid: UUID = None, generate_guid: bool = False) -> None:
        return super().__call__(guid, generate_guid)

    @classmethod
    def erase(cls, session: Session) -> None:
        session.query(cls.model_).delete()
        session.flush()

    def get_by_name(self, session: Session, name: str = None) -> list():
        """Retrieves exisiting Pokémons in DB. If does not exists raise exception.

        :param: name: the name of the Pokémon to get
        """
        # search the pokemon by given name
        pokemon_q = session.query(self.model_).filter(self.model_.name == name)
        pokemon = session.execute(pokemon_q).fetchone()
        if not pokemon:
            raise HTTPException(status_code=409)

        # get trelated abilities
        abilities_q = session.query(PokemonsAbilities.model_).filter(
            PokemonsAbilities.model_.pokemons_guid == pokemon[0].guid
        )
        abilities = session.execute(abilities_q).fetchall()

        # get related types
        types_q = session.query(PokemonsTypes.model_).filter(
            PokemonsTypes.model_.pokemons_guid == pokemon[0].guid
        )
        types = session.execute(types_q).fetchall()

        # get related stats
        stats_q = session.query(PokemonsStats.model_).filter(
            PokemonsStats.model_.pokemons_guid == pokemon[0].guid
        )
        stats = session.execute(stats_q).fetchall()

        # build and return response
        return {
            "pokemon": pokemon[0].__dict__,
            "attributes": [
                {"types": list(t["pokemons_types"].__dict__ for t in types)},
                {"stats": list(s["pokemons_stats"].__dict__ for s in stats)},
                {
                    "abilities": list(
                        a["pokemons_abilities"].__dict__ for a in abilities
                    )
                },
            ],
        }

    def exists(self, session: Session) -> Union[str, None]:
        q = session.query(self.model_).filter(self.model_.name == self.name)
        if q.count() > 0:
            rv = session.execute(q).fetchone()
            return rv[0].guid
        return None


class PokemonsAbilities(Super):
    """Pokemons class reflecting the `pokemons_abilities` table."""

    model_ = model("pokemons_abilities")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def __call__(self, guid: UUID = None, generate_guid: bool = False) -> None:
        return super().__call__(guid, generate_guid)

    @classmethod
    def erase(cls, session: Session) -> None:
        session.query(cls.model_).delete()
        session.flush()


class PokemonsStats(Super):
    """Pokemons class reflecting the `pokemons_stats` table."""

    model_ = model("pokemons_stats")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def __call__(self, guid: UUID = None, generate_guid: bool = False) -> None:
        return super().__call__(guid, generate_guid)

    @classmethod
    def erase(cls, session: Session) -> None:
        session.query(cls.model_).delete()
        session.flush()


class PokemonsTypes(Super):
    """Pokemons class reflecting the `pokemons_types` table."""

    model_ = model("pokemons_types")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def __call__(self, guid: UUID = None, generate_guid: bool = False) -> None:
        return super().__call__(guid, generate_guid)

    @classmethod
    def erase(cls, session: Session) -> None:
        session.query(cls.model_).delete()
        session.flush()
