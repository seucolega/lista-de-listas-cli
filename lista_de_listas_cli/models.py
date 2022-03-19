from typing import Any, Union

from database import Base, engine
from schemas import ItemStatus
from sqlalchemy import BigInteger, Column, Enum, ForeignKey, String, Table
from sqlalchemy.orm import relationship, validates

Base.metadata.create_all(bind=engine)

item_and_tag = Table(
    'item_tag',
    Base.metadata,
    Column('item_id', ForeignKey('item.id'), primary_key=True),
    Column('tag_id', ForeignKey('tag.id'), primary_key=True),
)


class Item(Base):
    __tablename__ = 'item'

    id: int = Column(BigInteger, primary_key=True, index=True)
    name: str = Column(String)
    description: str = Column(String, nullable=True)
    status: Enum = Column(Enum(ItemStatus), default=ItemStatus.UNDONE)
    tags: Union[list, Any] = relationship(
        'Tag', secondary=item_and_tag, back_populates='items'
    )

    def __str__(self):
        return self.name

    @validates('tags')
    def just_a_child_tag(self, _, tag):
        if tag.parent_id:
            for index, existent_tag in enumerate(self.tags):
                if existent_tag.parent_id == tag.parent_id:
                    del self.tags[index]

        return tag


class Tag(Base):
    __tablename__ = 'tag'

    id: int = Column(BigInteger, primary_key=True, index=True)
    name: str = Column(String)
    parent_id: int = Column(BigInteger, ForeignKey('tag.id'), nullable=True)
    children: list = relationship('Tag')
    items: Union[list, Any] = relationship(
        'Item', secondary=item_and_tag, back_populates='tags'
    )

    def __str__(self):
        return self.name

    @validates('parent_id')
    def mother_tag_cannot_be_your_child(self, _, parent_id):
        for tag in self.children:
            if parent_id == tag.id:
                raise ValueError('Mother tag cannot also be your child')
        return parent_id
