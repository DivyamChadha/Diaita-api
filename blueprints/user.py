from models.user import UserPayload, UserAuthenticatedPayload
from typing import TYPE_CHECKING
from quart import Blueprint, current_app
from quart_schema import validate_request, validate_response

user = Blueprint('user', __name__, url_prefix='/diaita/api/user')

if TYPE_CHECKING:
    from asyncpg import Connection

    from ..models.app import Quart
    current_app: Quart

@user.route('/register/', methods=['POST'])
@validate_request(UserPayload)
async def register_user(data: UserPayload):
    async with current_app.db.acquire() as con:
        con: Connection 

        hashed_email = current_app.hash_email(data.email)
        if await con.fetchval('SELECT NOT EXISTS(SELECT FROM users WHERE email = $1)', hashed_email):
            snowflake = current_app.generate_snowflake()
            user_id = int(snowflake)
            hashed_pass, salt = current_app.hash_password(data.password, int(current_app.config['diaita']['iterations']))
            await con.execute('INSERT INTO users(user_id, email, pass, salt) VALUES ($1, $2, $3, $4)', user_id, hashed_email, hashed_pass, salt)
            return 'Ok.', 201
        
        else:
            # email has already been used
            return 'Email is already in use.', 409


@user.route('/authenticate/', methods=['POST'])
@validate_request(UserPayload)
@validate_response(UserAuthenticatedPayload, 201)
async def authenticate_user(data: UserPayload):
    async with current_app.db.acquire() as con:
        con: Connection

        hashed_email = current_app.hash_email(data.email)
        row = await con.fetchrow('SELECT pass, salt FROM users where email = $1', hashed_email)

        if row is None:
            return 'User not found.', 404
        
        hashed_pass, _ = current_app.hash_password(data.password, int(current_app.config['diaita']['iterations']), row[1])
        if hashed_pass == row[0]:
            # TODO store the access token for later requests
            return UserAuthenticatedPayload(token=current_app.generate_session_token()), 201
        else:
            return 'Invalid Auth.', 401
