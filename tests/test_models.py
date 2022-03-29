import pytest


def test_item_as_str(item_1):
    assert str(item_1) == item_1.name


def test_item_name_cannot_be_empty(item_1):
    with pytest.raises(ValueError):
        item_1.name = ''


def test_tag_as_str(tag_1):
    assert str(tag_1) == tag_1.name


def test_tag_name_cannot_be_empty(tag_1):
    with pytest.raises(ValueError):
        tag_1.name = ''


def test_parent_tag(tag_1, tag_2):
    tag_2.parent_id = tag_1.id

    assert tag_1.children == [tag_2]


def test_mother_tag_cannot_be_your_daughter(tag_1, tag_2):
    tag_2.parent_id = tag_1.id

    with pytest.raises(ValueError):
        tag_1.parent_id = tag_2.id


def test_set_a_tag_in_a_item(item_1, tag_1):
    item_1.tags.append(tag_1)

    assert tag_1.items == [item_1]


def test_set_a_item_in_a_tag(item_1, tag_1):
    tag_1.items.append(item_1)

    assert item_1.tags == [tag_1]


def test_item_with_two_tags(item_1, tag_1, tag_2):
    item_1.tags.append(tag_1)
    item_1.tags.append(tag_2)

    assert item_1.tags == [tag_1, tag_2]


def test_item_with_one_child_tag(
    item_1, child_tag_1_of_parent_tag_1, child_tag_2_of_parent_tag_1
):
    item_1.tags = [child_tag_1_of_parent_tag_1]

    item_1.tags.append(child_tag_2_of_parent_tag_1)

    assert item_1.tags == [child_tag_2_of_parent_tag_1]


def test_item_with_parent_and_child_tags(
    item_1, tag_1, child_tag_1_of_parent_tag_1, child_tag_2_of_parent_tag_1
):
    item_1.tags = [tag_1, child_tag_1_of_parent_tag_1]

    item_1.tags.append(child_tag_2_of_parent_tag_1)

    assert item_1.tags == [tag_1, child_tag_2_of_parent_tag_1]
