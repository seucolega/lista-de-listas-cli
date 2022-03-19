from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ItemStatus(Enum):
    DONE = 'done'
    UNDONE = 'undone'
    WONT = 'wont'
    NOTE = 'note'


class ItemBase(BaseModel):
    name: str
    status: ItemStatus = ItemStatus.UNDONE
    tags: list = []


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True


class TagBase(BaseModel):
    name: str
    parent_id: Optional[int]
    multi_children: bool = False
    children: list = []


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True
