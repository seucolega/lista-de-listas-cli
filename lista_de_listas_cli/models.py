from database import Base, engine
from schemas import ItemStatus
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    String,
    Table,
)
from sqlalchemy.orm import relationship

Base.metadata.create_all(bind=engine)

item_and_tag = Table(
    'item_tag',
    Base.metadata,
    Column('item_id', ForeignKey('item.id'), primary_key=True),
    Column('tag_id', ForeignKey('tag.id'), primary_key=True),
)


class Item(Base):
    __tablename__ = 'item'

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    status = Column(Enum(ItemStatus), default=ItemStatus.UNDONE)
    tags = relationship('Tag', secondary=item_and_tag, back_populates='items')

    def __str__(self):
        return self.name


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String)
    parent_id = Column(BigInteger, ForeignKey('tag.id'), nullable=True)
    multi_children = Column(Boolean, default=False)
    children = relationship('Tag')
    items = relationship('Item', secondary=item_and_tag, back_populates='tags')

    def __str__(self):
        return self.name
