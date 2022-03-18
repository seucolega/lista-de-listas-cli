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

    assert facade.create_item(item=item)


@pytest.mark.parametrize('status', [*schemas.ItemStatus])
def test_set_item_status(item_1, status):
    facade.set_item_status(item=item_1, status=status)

    assert item_1.status == status
