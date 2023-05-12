import datetime
import aiohttp
import asyncio
from more_itertools import chunked

from models import Base, SwapiPeople, Session, engine

MAX_REQUESTS = 5
FILMS = {}
SPECIES = {}
STARSHIPS = {}
VEHICLES = {}


def list_to_string(json_data, var, global_var):
    result = []
    for el in json_data[var]:
        result.append(global_var[el])
    return ', '.join(result)


async def get_people(client, people_id):
    async with client.get(f'https://swapi.dev/api/people/{people_id}') as response:
        json_data = await response.json()
        if 'detail' not in json_data:
            json_data['id'] = people_id

            json_data['films'] = list_to_string(json_data, 'films', FILMS)
            json_data['species'] = list_to_string(json_data, 'species', SPECIES)
            json_data['starships'] = list_to_string(json_data, 'starships', STARSHIPS)
            json_data['vehicles'] = list_to_string(json_data, 'vehicles', VEHICLES)

            del[json_data['created']]
            del[json_data['edited']]

        return json_data


async def set_dict(client, link, var, field):
    while link is not None:
        async with client.get(link) as response:
            elements = await response.json()
            for el in elements['results']:
                var[el['url']] = el[field]
            link = elements['next']


async def paste_to_db(people_jsons):
    async with Session() as session:
        orm_objects = [SwapiPeople(**item) for item in people_jsons if 'detail' not in item]

        session.add_all(orm_objects)
        await session.commit()


async def main():
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)

    async with aiohttp.ClientSession() as client:

        await asyncio.gather(set_dict(client, 'https://swapi.dev/api/films/', FILMS, 'title'), set_dict(client, 'https://swapi.dev/api/species/', SPECIES, 'name'), set_dict(client, 'https://swapi.dev/api/starships/', STARSHIPS, 'name'), set_dict(client, 'https://swapi.dev/api/vehicles/', VEHICLES, 'name'))

        for people_id_chunk in chunked(range(1, 83), MAX_REQUESTS):
            person_coros = [get_people(client, people_id) for people_id in people_id_chunk]
            result = await asyncio.gather(*person_coros)
            paste_to_db_coro = paste_to_db(result)
            paste_to_db_task = asyncio.create_task(paste_to_db_coro)

    tasks = asyncio.all_tasks() - {asyncio.current_task(), }
    for task in tasks:
        await task


if __name__ == '__main__':
    start = datetime.datetime.now()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
    print(datetime.datetime.now() - start)
