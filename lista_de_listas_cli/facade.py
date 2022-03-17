import models
import schemas
from sqlalchemy.orm import Session


def get_all_items(
    db_session: Session, skip: int = 0, limit: int = 100
) -> [schemas.Item]:
    return db_session.query(models.Item).offset(skip).limit(limit).all()


def get_actionable_items(
    db_session: Session, skip: int = 0, limit: int = 100
) -> [schemas.Item]:
    return (
        db_session.query(models.Item)
        .filter_by(status=schemas.ItemStatus.UNDONE)
        .offset(skip)
        .limit(limit)
        .all()
    )


# def get_non_actionable_items(
#         db_session: Session, skip: int = 0, limit: int = 100
# ) -> [schemas.Item]:
#     return db_session.query(models.Item) \
#         .filter_by(status=schemas.ItemStatus.NOTE) \
#         .offset(skip).limit(limit).all()


def get_item(db_session: Session, item_id: int) -> schemas.Item:
    return db_session.query(models.Item).filter_by(id=item_id).first()


def create_item(db_session: Session, item: schemas.ItemCreate) -> schemas.Item:
    item = models.Item(
        id=len(get_all_items(db_session=db_session)) + 1,
        **item.dict(),
    )

    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    return item
