from sqlalchemy.orm import Session

import models
import schemas


def get_item_list(db_session: Session, skip: int = 0, limit: int = 100):
    return db_session.query(models.Item).offset(skip).limit(limit).all()


def get_item(db_session: Session, item_id: int) -> schemas.Item:
    return db_session.query(models.Item).filter_by(id=item_id).first()


def create_item(db_session: Session, item: schemas.ItemCreate) -> schemas.Item:
    item = models.Item(
        id=len(get_item_list(db_session=db_session)) + 1,
        name=item.name,
    )

    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    return item
