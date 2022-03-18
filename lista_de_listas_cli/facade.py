import models
import schemas
from database import db_session


def get_all_items(skip: int = 0, limit: int = 100) -> [schemas.Item]:
    return db_session.query(models.Item).offset(skip).limit(limit).all()


def get_actionable_items(skip: int = 0, limit: int = 100) -> [schemas.Item]:
    return (
        db_session.query(models.Item)
        .filter_by(status=schemas.ItemStatus.UNDONE)
        .offset(skip)
        .limit(limit)
        .all()
    )


# def get_non_actionable_items(
#         skip: int = 0, limit: int = 100
# ) -> [schemas.Item]:
#     return db_session.query(models.Item) \
#         .filter_by(status=schemas.ItemStatus.NOTE) \
#         .offset(skip).limit(limit).all()


def get_item(item_id: int) -> schemas.Item:
    return db_session.query(models.Item).filter_by(id=item_id).first()


def create_item(item: schemas.ItemCreate) -> schemas.Item:
    item = models.Item(
        id=len(get_all_items()) + 1,
        **item.dict(),
    )

    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    return item


def set_item_status(item: schemas.Item, status: schemas.ItemStatus):
    item.status = status
    db_session.commit()
