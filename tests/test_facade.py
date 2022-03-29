import facade
import pytest
import schemas


@pytest.fixture(autouse=True)
def configure_db_session(db_session):
    facade.db_session = db_session


def test_get_item_list__empty():
    assert facade.get_item_list() == []


def test_get_item_list__with_item(item_1):
    assert facade.get_item_list() == [item_1]


def test_get_actionable_items__empty():
    assert facade.get_actionable_items() == []


def test_get_actionable_items__with_a_done_item(done_item_1):
    assert facade.get_actionable_items() == []


def test_get_actionable_items__with_done_and_undone_items(
    done_item_1, undone_item_1
):
    assert facade.get_actionable_items() == [undone_item_1]


def test_get_actionable_items_with_the_tag__empty(tag_1):
    assert facade.get_actionable_items_with_the_tag(tag_1.id) == []


def test_get_inbox_items__empty():
    assert facade.get_inbox_items() == []


def test_get_inbox_items__with_a_done_item(done_item_1):
    assert facade.get_inbox_items() == []


def test_get_inbox_items__with_done_and_undone_items(
    done_item_1, undone_item_1
):
    assert facade.get_inbox_items() == [undone_item_1]


def test_get_inbox_items__with_a_undone_and_tagged_item(undone_item_1, tag_1):
    undone_item_1.tags = [tag_1]

    assert facade.get_inbox_items() == []


def test_get_actionable_items_with_the_tag__with_a_done_item(
    tag_1, done_item_1
):
    assert facade.get_actionable_items_with_the_tag(tag_1.id) == []


def test_get_actionable_items_with_the_tag__with_items_without_the_tag(
    tag_1, done_item_1, undone_item_1
):
    assert facade.get_actionable_items_with_the_tag(tag_1.id) == []


def test_get_actionable_items_with_the_tag__with_items_and_the_tag(
    tag_1, done_item_1, undone_item_1
):
    tag_1.items = [done_item_1, undone_item_1]

    assert facade.get_actionable_items_with_the_tag(tag_1.id) == [
        undone_item_1
    ]


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


def test_get_list_of_tags_with_items(item_1, tag_1, tag_2):
    item_1.tags = [tag_1]

    assert facade.get_list_of_tags_with_items() == [tag_1]


def test_get_actionable_tag_list(tag_1, child_tag_1_of_parent_tag_1):
    result = facade.get_actionable_tag_list()

    assert result == [tag_1, child_tag_1_of_parent_tag_1]


def test_get_tag_list__with_item(db_session, tag_1):
    assert facade.get_tag_list() == [tag_1]


def test_get_tag(tag_1):
    assert facade.get_tag(tag_id=tag_1.id) == tag_1


def test_create_tag():
    tag = schemas.TagCreate(name='Tag Name')

    assert facade.create_tag(tag=tag).id


def test_get_tag_by_name__case_insensitive(tag_1):
    tag_1.name = 'Next Actions'

    assert facade.get_tag_by_name('next actions')


def test_get_tag_by_name__not_found(tag_1):
    tag_1.name = 'Next Actions'

    assert not facade.get_tag_by_name('waiting')


def test_get_item_text_to_show__item_name_without_tags(item_1):
    item_1.name = 'Item name'
    item_1.tags = []

    assert facade.get_item_text_to_show(item_1) == item_1.name


def test_get_item_text_to_show__item_with_one_tag(item_1, tag_1):
    item_1.name = 'Item name'
    item_1.tags = [tag_1]
    tag_1.name = 'Waiting'

    expected = 'Item name @Waiting'

    assert facade.get_item_text_to_show(item_1) == expected


def test_get_item_text_to_show__item_with_one_spaced_tag(item_1, tag_1):
    item_1.name = 'Item name'
    item_1.tags = [tag_1]

    tag_1.name = 'First Tag'

    expected = 'Item name @First_Tag'

    assert facade.get_item_text_to_show(item_1) == expected


def test_get_item_text_to_show__item_with_two_tags(item_1, tag_1, tag_2):
    item_1.name = 'Item name'
    item_1.tags = [tag_1, tag_2]

    tag_1.name = 'First Tag'
    tag_2.name = 'Second Tag'

    expected = 'Item name @First_Tag @Second_Tag'

    assert facade.get_item_text_to_show(item_1) == expected


def test_get_item_text_to_show__item_with_one_tag_and_context(item_1, tag_1):
    item_1.name = 'Item name'
    item_1.tags = [tag_1]

    tag_1.name = 'Waiting'

    result = facade.get_item_text_to_show(item=item_1, context=tag_1)

    expected = 'Item name'

    assert result == expected


def test_get_item_text_to_show__item_with_two_tags_and_context(
    item_1, tag_1, tag_2
):
    item_1.name = 'Item name'
    item_1.tags = [tag_1, tag_2]

    tag_1.name = 'First Tag'
    tag_2.name = 'Second Tag'

    result = facade.get_item_text_to_show(item=item_1, context=tag_1)

    expected = 'Item name @Second_Tag'

    assert result == expected


def test_get_tag_text_to_show__tag_without_parent_tag(tag_1):
    assert facade.get_tag_text_to_show(tag_1) == tag_1.name


def test_get_tag_text_to_show__item_with_parent_tag(
    parent_tag_1, child_tag_1_of_parent_tag_1
):
    child_tag_1_of_parent_tag_1.name = 'Tag name'
    parent_tag_1.name = 'Waiting'

    expected = 'Tag name @Waiting'

    assert facade.get_tag_text_to_show(child_tag_1_of_parent_tag_1) == expected


def test_get_tag_text_to_show__item_with_one_spaced_tag(
    parent_tag_1, child_tag_1_of_parent_tag_1
):
    child_tag_1_of_parent_tag_1.name = 'Tag name'
    parent_tag_1.name = 'Parent Tag'

    expected = 'Tag name @Parent_Tag'

    assert facade.get_tag_text_to_show(child_tag_1_of_parent_tag_1) == expected


def test_get_tag_text_to_show__item_with_one_tag_and_context(
    parent_tag_1, child_tag_1_of_parent_tag_1
):
    child_tag_1_of_parent_tag_1.name = 'Tag name'
    parent_tag_1.name = 'Waiting'

    result = facade.get_tag_text_to_show(
        tag=child_tag_1_of_parent_tag_1, context=parent_tag_1
    )

    expected = 'Tag name'

    assert result == expected


def test_get_list_of_tags_with_actionable_items__with_a_done_item(
    done_item_1, tag_1
):
    done_item_1.tags = [tag_1]

    assert facade.get_list_of_tags_with_actionable_items() == []


def test_get_list_of_tags_with_actionable_items__with_an_undone_item(
    undone_item_1, tag_1
):
    undone_item_1.tags = [tag_1]

    assert facade.get_list_of_tags_with_actionable_items() == [tag_1]
