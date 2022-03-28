from enum import Enum
from typing import Optional

from pydantic import BaseModel
from pydantic.class_validators import validator


class ItemStatus(Enum):
    DONE = 'done'
    UNDONE = 'undone'
    WONT = 'wont'
    NOTE = 'note'


class ItemBase(BaseModel):
    name: str
    status: ItemStatus = ItemStatus.UNDONE
    tags: list = []

    @validator('name')
    def name_cannot_be_empty(cls, value: str):
        if not value.strip():
            raise ValueError('Name cannot be empty.')

        return value


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True


class TagBase(BaseModel):
    name: str
    parent_id: Optional[int]
    children: list = []
    items: list = []

    @validator('name')
    def name_cannot_be_empty(cls, value: str):
        if not value.strip():
            raise ValueError('Name cannot be empty.')

        return value


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True
