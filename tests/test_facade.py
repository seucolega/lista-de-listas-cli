import facade
import schemas


def test_get_item_list__empty(db_session):
    assert facade.get_item_list(db_session=db_session) == []


def test_get_item_list__with_item(db_session, item_1):
    assert facade.get_item_list(db_session=db_session) == [item_1]


def test_create_item(db_session):
    item = schemas.ItemCreate(name='Something')

    assert facade.create_item(db_session=db_session, item=item)
