from database import Base, engine
from schemas import ItemStatus
from sqlalchemy import BigInteger, Column, Enum, String

Base.metadata.create_all(bind=engine)


class Item(Base):
    __tablename__ = 'item'

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    status = Column(Enum(ItemStatus), default=ItemStatus.UNDONE)

    def __str__(self):
        return self.name
