from __future__ import annotations

from pydantic import BaseModel

class UserPayload(BaseModel):
    email: str
    password: str

class UserAuthenticatedPayload(BaseModel):
    token: str
