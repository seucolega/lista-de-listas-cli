import models
import schemas
from database import db_session
from sqlalchemy import func


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


def get_inbox_items(skip: int = 0, limit: int = 100) -> [schemas.Item]:
    return (
        db_session.query(models.Item)
        .filter_by(status=schemas.ItemStatus.UNDONE)
        .filter(~models.Item.tags.any())
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


def get_tag_list(skip: int = 0, limit: int = 100) -> [schemas.Item]:
    return db_session.query(models.Tag).offset(skip).limit(limit).all()


def get_list_of_tags_with_items(
    skip: int = 0, limit: int = 100
) -> [schemas.Item]:
    return (
        db_session.query(models.Tag)
        .filter(models.Tag.items.any())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_actionable_tag_list(skip: int = 0, limit: int = 100) -> [schemas.Item]:
    return (
        db_session.query(models.Tag)
        .filter(~models.Tag.children.any())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_tag(tag_id: int) -> schemas.Tag:
    return db_session.query(models.Tag).filter_by(id=tag_id).first()


def get_tag_by_name(tag_name: str) -> schemas.Tag:
    return (
        db_session.query(models.Tag)
        .filter(func.lower(models.Tag.name) == func.lower(tag_name))
        .first()
    )


def create_tag(tag: schemas.TagCreate) -> schemas.Tag:
    tag = models.Tag(
        id=len(get_tag_list()) + 1,
        **tag.dict(),
    )

    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)

    return tag
