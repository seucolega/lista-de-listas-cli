from enum import Enum

from pydantic import BaseModel


class ItemStatus(Enum):
    DONE = 'done'
    UNDONE = 'undone'
    WONT = 'wont'
    NOTE = 'note'


class ItemBase(BaseModel):
    name: str
    status: ItemStatus = ItemStatus.UNDONE


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True
