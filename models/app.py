from __future__ import annotations

import os
import hashlib
import secrets

from datetime import datetime, timezone
from models.snowflake import Snowflake
from typing import TYPE_CHECKING, Optional
from quart import Quart as _Quart

if TYPE_CHECKING:
    from asyncpg import Pool
    from quart import Config

class Quart(_Quart):
    db: Pool
    config: Config
    last_datetime: Optional[datetime] = None
    sequence: int = 0

    def generate_session_token(self, nbytes: int = 32) -> str:
        """Method used to generate access tokens.

        This access tokens are granted during login so user does not have to authenticate every following request.

        Parameters
        ------------
        nbytes: :class:`int`
            Number of random bytes the token has.

        Returns
        ---------
        The access token: :class:`str`

        """
        return secrets.token_urlsafe(nbytes)

    def generate_snowflake(self) -> Snowflake:
        """Method used to generate snowflakes.

        Every user or item has a unique id known as a snowflake. This format was created by Twitter and is inspired from it.
        
        Returns
        ---------
        The snowflake: :class:`Snowflake`

        """
        now = datetime.now(timezone.utc)

        if self.last_datetime:
            if self.last_datetime == now and self.sequence < 4096:
                self.sequence += 1
            else:
                self.sequence = 0

        self.last_datetime = now
        return Snowflake(now, int(self.config['diaita']['worker_id']), self.sequence)

    def hash_email(self, email: str) -> bytes:
        """Method used to hash an email address using SHA-256.

        This method adds pepper to the hash which is provided in the config file.

        Parameters
        ------------
        email: :class:`str`
            The email address of the user to hash.

        Returns
        ---------
        The hashed email: :class:`bytes`
        
        """
        email_hash = hashlib.sha256(bytes(email + self.config['diaita']['pepper'], 'utf-8'))
        return email_hash.digest()

    def hash_password(self, password: str, iterations: int, salt: Optional[bytes] = None) -> tuple[bytes, bytes]:
        """Method used to hash a password using PBKDF2 and SHA-256.

        This method adds randomly generated salt and the pepper provided in the config file.

        Parameters
        ------------
        password: :class:`str`
            The password to hash.
        iterations: :class:`int`
            The number of times the password is to be hashed.
        salt: Optional[:class:`bytes`]
            The salt to be added to the password. If not provided it is generated using os.urandom.

        Returns
        ---------
        The hashed password and the salt: tuple[:class:`bytes`, :class:`bytes`]
        
        """
        salt = salt or os.urandom(32)
        password = password + self.config['diaita']['pepper']
        hash = hashlib.pbkdf2_hmac('sha256', bytes(password, 'utf-8'), salt, iterations)
        return hash, salt
