import facade
import schemas


def test_get_item_list__empty(db_session):
    assert facade.get_all_items(db_session=db_session) == []


def test_get_item_list__with_item(db_session, item_1):
    assert facade.get_all_items(db_session=db_session) == [item_1]


def test_get_actionable_items(db_session, done_item_1, undone_item_1):
    expected = [undone_item_1]

    assert facade.get_actionable_items(db_session=db_session) == expected


def test_get_item(db_session, item_1):
    assert facade.get_item(db_session=db_session, item_id=item_1.id) == item_1


def test_create_item(db_session):
    item = schemas.ItemCreate(name='Something')

    assert facade.create_item(db_session=db_session, item=item)
