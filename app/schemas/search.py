from pydantic import BaseModel
from datetime import datetime
from typing import Union


class ListSearchResult(BaseModel):
    id: int
    url: str
    name: str
    created_at: Union[str, datetime] | None

    class Config:
        orm_mode = True


class MakeSearchRequest(BaseModel):
    search_text: str


class CreateSearchResult(BaseModel):
    url: str
    name: str
