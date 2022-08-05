#!/bin/bash
set -e
export PGPASSWORD=$POSTGRES_PASSWORD;
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE USER $APP_DB_USER WITH PASSWORD '$APP_DB_PASS';
  CREATE DATABASE $APP_DB_NAME;
  GRANT ALL PRIVILEGES ON DATABASE $APP_DB_NAME TO $APP_DB_USER;
  \connect $APP_DB_NAME $APP_DB_USER
  BEGIN;
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    ALTER EXTENSION "uuid-ossp" SET SCHEMA "public";

    DROP TABLE IF EXISTS public.pokemons;
    DROP TABLE IF EXISTS public.pokemons_abilities;
    DROP TABLE IF EXISTS public.pokemons_types;
    DROP TABLE IF EXISTS public.pokemons_stats;

    CREATE TABLE public.pokemons (
        guid uuid NOT NULL,
        name VARCHAR(255) NOT NULL,
        description VARCHAR(255) NULL,
        CONSTRAINT pokemons_pkey PRIMARY KEY (guid)
        );

    CREATE TABLE public.pokemons_abilities (
        guid uuid NOT NULL,
        pokemons_guid uuid NOT NULL,
        name VARCHAR(253) NOT NULL,
        url VARCHAR(253) NOT NULL,
        is_hidden bool NOT NULL,
        slot INTEGER NOT NULL,
        CONSTRAINT pokemon_abilities_pkey PRIMARY KEY (guid),
        CONSTRAINT pokemons_abilities_guid_fkey FOREIGN KEY (pokemons_guid) REFERENCES pokemons(guid)
        );

    CREATE TABLE public.pokemons_types (
        guid uuid NOT NULL,
        name VARCHAR(255) NOT NULL,
        url VARCHAR(255) NOT NULL,
        slot INTEGER NOT NULL,
        pokemons_guid uuid NOT NULL,
        CONSTRAINT pokemon_types_pkey PRIMARY KEY (guid),
        CONSTRAINT pokemons_types_guid_fkey FOREIGN KEY (pokemons_guid) REFERENCES pokemons(guid)
        );

    CREATE TABLE public.pokemons_stats (
        guid uuid NOT NULL,
        name VARCHAR(255) NOT NULL,
        url VARCHAR(255) NOT NULL,
        base_stat INTEGER NOT NULL,
        effort INTEGER NOT NULL,
        pokemons_guid uuid NOT NULL,
        CONSTRAINT pokemon_stats_pkey PRIMARY KEY (guid),
        CONSTRAINT pokemons_stats_guid_fkey FOREIGN KEY (pokemons_guid) REFERENCES pokemons(guid)
        );

  COMMIT;
EOSQL