import facade
import pytest
import schemas


@pytest.fixture(autouse=True)
def configure_db_session(db_session):
    facade.db_session = db_session


def test_get_item_list__empty():
    assert facade.get_all_items() == []


def test_get_item_list__with_item(item_1):
    assert facade.get_all_items() == [item_1]


def test_get_actionable_items(done_item_1, undone_item_1):
    assert facade.get_actionable_items() == [undone_item_1]


def test_get_item(item_1):
    assert facade.get_item(item_id=item_1.id) == item_1


def test_create_item():
    item = schemas.ItemCreate(name='Something')

    assert facade.create_item(item=item).id


@pytest.mark.parametrize('status', [*schemas.ItemStatus])
def test_set_item_status(item_1, status):
    facade.set_item_status(item=item_1, status=status)

    assert item_1.status == status


def test_get_tag_list__empty():
    assert facade.get_tag_list() == []


def test_get_tag_list__with_item(db_session, tag_1):
    assert facade.get_tag_list() == [tag_1]


def test_get_tag(tag_1):
    assert facade.get_tag(tag_id=tag_1.id) == tag_1


def test_create_tag():
    tag = schemas.TagCreate(name='Tag Name')

    assert facade.create_tag(tag=tag).id


def test_set_a_tag_in_a_item(db_session, item_1, tag_1):
    item_1.tags.append(tag_1)
    db_session.commit()

    assert tag_1.items == [item_1]


def test_set_a_item_in_a_tag(db_session, item_1, tag_1):
    tag_1.items.append(item_1)
    db_session.commit()

    assert item_1.tags == [tag_1]
