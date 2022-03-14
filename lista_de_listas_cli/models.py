from sqlalchemy import BigInteger, Column, String

from database import Base, engine

Base.metadata.create_all(bind=engine)


class Item(Base):
    __tablename__ = 'item'

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    # document_id = Column(BigInteger)
    # item_id = Column(BigInteger, unique=True)
    # product_id = Column(BigInteger)
    # supplier_id = Column(BigInteger)
    # quantity_acquired = Column(Float)
    # document_date = Column(Date)
    # payroll_balance = Column(Float)

    def __str__(self):
        return self.name
