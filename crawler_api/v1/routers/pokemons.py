from fastapi import APIRouter, Depends, Path, Query
from fastapi.exceptions import HTTPException
from pydantic import StrictStr
from sqlalchemy.orm import Session

from ..database.orm import get_db
from ..models import utils


router = APIRouter()


@router.get(
    "/pokemons/{name}",
    description="Get Pokémons",
)
def get_pokemons(
    name: StrictStr = Path(..., description="Name of the Pokémon"),
    session: Session = Depends(get_db),
):
    """
    Retrieves Pokémons inside the DB.

    :param name: optional [str] -> if given, results are filtered by the given name
    """
    try:
        return utils.query_pokemons(name, session)
    except (Exception, KeyError, ValueError):
        raise HTTPException(status_code=404)
