import models
import schemas
from database import db_session
from sqlalchemy import func


def get_item_list(skip: int = 0, limit: int = 100) -> [schemas.Item]:
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


def get_actionable_items_with_the_tag(
    tag_id: int, skip: int = 0, limit: int = 100
) -> [schemas.Item]:
    return (
        db_session.query(models.Item)
        .filter_by(status=schemas.ItemStatus.UNDONE)
        .filter(models.Item.tags.any(id=tag_id))
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
        id=len(get_item_list()) + 1,
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


def get_list_of_tags_with_actionable_items(
    skip: int = 0, limit: int = 100
) -> [schemas.Item]:
    return (
        db_session.query(models.Tag)
        .join(models.ItemTag, models.ItemTag.tag_id == models.Tag.id)
        .join(models.Item, models.Item.id == models.ItemTag.item_id)
        .filter(models.Item.status == schemas.ItemStatus.UNDONE)
        .distinct()
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


def get_tag_list_without_parent(
    skip: int = 0, limit: int = 100
) -> [schemas.Tag]:
    return (
        db_session.query(models.Tag)
        .filter_by(parent_id=None)
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


def get_item_text_to_show(
    item: schemas.Item, context: schemas.Tag = None
) -> str:
    result = item.name

    tags = []

    for tag in item.tags:
        if context != tag:
            tags.append('@' + tag.name.replace(' ', '_'))

    if tags:
        result += ' ' + ' '.join(tags)

    return result


def get_tag_text_to_show(tag: schemas.Tag, context: schemas.Tag = None) -> str:
    result = tag.name

    if tag.parent_id:
        parent_tag = get_tag(tag.parent_id)
        if parent_tag and context != parent_tag:
            result += ' @' + parent_tag.name.replace(' ', '_')

    return result
