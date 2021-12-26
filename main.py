import asyncpg

from blueprints.user import user
from configparser import ConfigParser
from models.app import Quart
from quart_schema import QuartSchema

config = ConfigParser()
config.read('config.ini')

app = Quart(__name__)
QuartSchema(app)
app.config.update(
    {
        'psql': config['PSQL'],
        'diaita': config['DIAITA'],
    }
)

app.register_blueprint(user)

@app.before_serving
async def start() -> None:

    pool =  await asyncpg.create_pool(
        database = app.config['psql']['db'],
        user = app.config['psql']['user'],
        password = app.config['psql']['pass'],
    )

    if not pool:
        raise RuntimeError('Connection pool not acquired. Terminating connection...')
    app.db = pool

    async with app.db.acquire() as con:
        con: asyncpg.Connection

        async with await app.open_resource('database/setup.sql', 'r') as f:
            queries: str = await f.read() # type: ignore
            for query in queries.split(';'):
                if query:   
                    await con.execute(query)


@app.route('/')
async def index() -> str:
    return 'Diaita API' # temp
