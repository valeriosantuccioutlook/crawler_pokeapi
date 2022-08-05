from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import MetaData
from sqlalchemy.ext.automap import automap_base

DB_URI = "postgresql://docker:docker@pgserver:5432/docker?sslmode=disable"
DB_SCHEMA = "public"

engine = create_engine(DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData(bind=engine, schema=DB_SCHEMA)
Base = automap_base(bind=engine, metadata=metadata)
metadata.reflect(engine)
Base.prepare(engine, reflect=True)


def model(table: str) -> object:
    try:
        return Base.classes[table]
    except KeyError:
        raise KeyError("No such `%s` table" % table)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
