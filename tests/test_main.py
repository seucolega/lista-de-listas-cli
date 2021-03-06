from unittest.mock import Mock, patch

import facade
import main
import pytest
import schemas
from InquirerPy.base.control import Choice, Separator


@pytest.fixture(autouse=True)
def configure_db_session(db_session):
    main.db_session = db_session
    facade.db_session = db_session


@patch('main.show_items')
def test_list_command__exists(mock, runner):
    runner.invoke(main.list_command)

    assert mock.call_count


def test_add_command(runner):
    result = runner.invoke(main.add_command, ['A task'])

    assert result.exit_code == 0


def test_show_items__no_items_message(capsys):
    main.show_items(lambda: [])
    out, _ = capsys.readouterr()

    assert 'no items' in out


@patch('main.inquirer.select')
def test_show_items__no_items_to_select(mock):
    main.show_items(lambda: [])

    assert not mock.call_count


@patch('main.inquirer.select')
def test_show_items__with_items(mock, item_1):
    main.show_items(lambda: [item_1])

    assert mock.call_count


def test_show_items__function_is_called():
    function_to_get_items = Mock()
    function_to_get_items.return_value = []

    main.show_items(function_to_get_items)

    assert function_to_get_items.call_count


def test_show_items__function_called_with_context(item_1, tag_1):
    function_to_get_items = Mock()
    function_to_get_items.return_value = []

    main.show_items(function_to_get_items, context=tag_1)

    assert function_to_get_items.call_args.args == (tag_1,)


@patch('main.start_interactive')
def test_interactive_command__calls_start_interactive(mock, runner):
    runner.invoke(main.interactive_command)

    assert mock.call_count


@patch('main.clear_screen')
def test_start_interactive__is_clearing_screen(mock, runner):
    runner.invoke(main.interactive_command)

    assert mock.call_count


@patch('main.inquirer.select')
def test_start_interactive__inquirer_called(mock, runner):
    mock.return_value.execute.return_value = None

    main.start_interactive()

    assert mock.call_count


def test_choices_for_interactive_menu__has_new_item_choice():
    choices = main.choices_for_interactive_menu()

    assert [choice for choice in choices if 'New item' in choice.name]


def test_choices_for_interactive_menu__has_no_inbox_choice():
    choices = main.choices_for_interactive_menu()

    assert not [choice for choice in choices if 'Inbox' in choice.name]


def test_choices_for_interactive_menu__has_inbox_choice(item_1):
    choices = main.choices_for_interactive_menu()

    assert [
        choice
        for choice in choices
        if isinstance(choice, Choice) and 'Inbox' in choice.name
    ]


def test_choices_for_interactive_menu__has_exit_choice():
    choices = main.choices_for_interactive_menu()

    assert [choice for choice in choices if 'Exit' in choice.name]


def test_choices_for_interactive_menu__has_manage_tags_choice():
    choices = main.choices_for_interactive_menu()

    assert [choice for choice in choices if 'Manage tags' in choice.name]


def test_choices_for_interactive_menu__has_context_choice(item_1, tag_1):
    item_1.tags = [tag_1]

    choices = main.choices_for_interactive_menu()

    assert [
        choice
        for choice in choices
        if isinstance(choice, Choice) and 'Context' in choice.name
    ]


def test_choices_for_interactive_menu__has_the_tag_name_choice(item_1, tag_1):
    item_1.tags = [tag_1]
    tag_1.name = 'My tag'

    choices = main.choices_for_interactive_menu()

    assert [
        choice
        for choice in choices
        if isinstance(choice, Choice) and tag_1.name in choice.name
    ]


def test_choices_for_interactive_menu__has_no_empty_context_tag(item_1, tag_1):
    tag_1.name = 'My tag'

    choices = main.choices_for_interactive_menu()

    assert not [
        choice
        for choice in choices
        if isinstance(choice, Choice) and tag_1.name in choice.name
    ]


def test_choices_for_interactive_menu__has_no_empty_context_tag_2(
    done_item_1, tag_1
):
    done_item_1.tags = [tag_1]
    tag_1.name = 'My tag'

    choices = main.choices_for_interactive_menu()

    assert not [choice for choice in choices if tag_1.name in choice.name]


@patch('main.init_tags')
def test_init_tags_command__calls_init_tags(mock, runner):
    runner.invoke(main.init_tags_command)

    assert mock.call_count


def test_name_is_valid__empty():
    assert not main.name_is_valid('')


def test_name_is_valid__only_a_space():
    assert not main.name_is_valid(' ')


def test_name_is_valid():
    assert main.name_is_valid('Something')


@patch('main.inquirer.text')
def test_questions_when_creating_or_editing_an_item__return_class(text_mock):
    text_mock.return_value.execute.return_value = 'Something'

    result = main.questions_when_creating_or_editing_an_item()

    assert isinstance(result, schemas.ItemCreate)


@patch('main.inquirer.text')
def test_questions_when_creating_or_editing_an_item__with_name(text_mock):
    text_mock.return_value.execute.return_value = 'Something'

    result = main.questions_when_creating_or_editing_an_item()

    assert result.name == 'Something'


@patch('main.inquirer.text')
def test_questions_when_creating_or_editing_an_item__with_description(mock):
    mock.return_value.execute.side_effect = ['Item name', 'Item description']

    result = main.questions_when_creating_or_editing_an_item()

    assert result.description == 'Item description'


@patch('main.inquirer.confirm')
@patch('main.inquirer.text')
def test_create_item__with_name_and_confirm_called(
    text_mock, confirm_mock, runner
):
    text_mock.return_value.execute.return_value = 'Something'
    confirm_mock.return_value.execute.return_value = False

    main.create_item()

    assert confirm_mock.call_count


@patch('facade.create_item')
@patch('main.inquirer.confirm')
@patch('main.inquirer.text')
def test_create_item__with_name_and_not_confirmed(
    text_mock, confirm_mock, create_item_mock, runner
):
    text_mock.return_value.execute.return_value = 'Something'
    confirm_mock.return_value.execute.return_value = False

    main.create_item()

    assert not create_item_mock.call_count


@patch('main.edit_item_tags')
@patch('main.inquirer.confirm')
@patch('main.inquirer.text')
def test_create_item__with_name_and_confirmed(
    text_mock, confirm_mock, edit_item_tags_mock, runner
):
    text_mock.return_value.execute.return_value = 'Something'
    confirm_mock.return_value.execute.return_value = True
    edit_item_tags_mock.return_value = None

    main.create_item()

    assert len(facade.get_item_list()) == 1


@patch('main.edit_item_tags')
@patch('main.inquirer.confirm')
@patch('main.inquirer.text')
def test_create_item__asserting_name(
    text_mock, confirm_mock, edit_item_tags_mock, runner
):
    text_mock.return_value.execute.return_value = 'Something'
    confirm_mock.return_value.execute.return_value = True
    edit_item_tags_mock.return_value = None

    item = main.create_item()

    assert item.name == 'Something'


@patch('main.edit_item_tags')
@patch('main.inquirer.confirm')
@patch('main.inquirer.text')
def test_create_item__asserting_description(
    text_mock, confirm_mock, edit_item_tags_mock, runner
):
    text_mock.return_value.execute.side_effect = [
        'Item name',
        'Item description',
    ]
    confirm_mock.return_value.execute.return_value = True
    edit_item_tags_mock.return_value = None

    item = main.create_item()

    assert item.description == 'Item description'


@patch('main.edit_item_tags')
@patch('main.inquirer.confirm')
@patch('main.inquirer.text')
def test_create_item__item_tags_called(
    text_mock, confirm_mock, edit_item_tags_mock, runner
):
    text_mock.return_value.execute.return_value = 'Something'
    confirm_mock.return_value.execute.return_value = True
    edit_item_tags_mock.return_value = None

    main.create_item()

    assert edit_item_tags_mock.call_count


@patch('main.inquirer.select')
@patch('main.inquirer.text')
def test_questions_when_creating_or_editing_a_tag__return_class(
    text_mock, select_mock
):
    text_mock.return_value.execute.return_value = 'Something'
    select_mock.return_value.execute.return_value = None

    result = main.questions_when_creating_or_editing_a_tag()

    assert isinstance(result, schemas.TagCreate)


@patch('main.inquirer.select')
@patch('main.inquirer.text')
def test_questions_when_creating_or_editing_a_tag__with_name(
    text_mock, select_mock
):
    text_mock.return_value.execute.return_value = 'Something'
    select_mock.return_value.execute.return_value = None

    result = main.questions_when_creating_or_editing_a_tag()

    assert result.name == 'Something'


@patch('main.inquirer.select')
@patch('main.inquirer.text')
def test_questions_when_creating_or_editing_a_tag__with_parent(
    text_mock, select_mock, tag_1
):
    text_mock.return_value.execute.return_value = 'Something'
    select_mock.return_value.execute.return_value = tag_1.id

    result = main.questions_when_creating_or_editing_a_tag()

    assert result.parent_id == tag_1.id


@patch('main.inquirer.confirm')
@patch('main.ask_for_parent_tag_when_editing_a_tag')
@patch('main.inquirer.text')
def test_create_tag__with_name_and_confirm_called(
    text_mock, parent_id_mock, confirm_mock, runner
):
    text_mock.return_value.execute.return_value = 'Something'
    parent_id_mock.return_value = None
    confirm_mock.return_value.execute.return_value = False

    main.create_tag()

    assert confirm_mock.call_count


@patch('facade.create_tag')
@patch('main.inquirer.confirm')
@patch('main.ask_for_parent_tag_when_editing_a_tag')
@patch('main.inquirer.text')
def test_create_tag__with_name_and_not_confirmed(
    text_mock, parent_id_mock, confirm_mock, create_tag_mock, runner
):
    text_mock.return_value.execute.return_value = 'Something'
    parent_id_mock.return_value = None
    confirm_mock.return_value.execute.return_value = False

    main.create_tag()

    assert not create_tag_mock.call_count


@patch('main.inquirer.confirm')
@patch('main.ask_for_parent_tag_when_editing_a_tag')
@patch('main.inquirer.text')
def test_create_tag__with_name_and_confirmed(
    text_mock, parent_id_mock, confirm_mock, runner
):
    text_mock.return_value.execute.return_value = 'Something'
    parent_id_mock.return_value = None
    confirm_mock.return_value.execute.return_value = True

    main.create_tag()

    assert len(facade.get_tag_list()) == 1


@patch('main.inquirer.confirm')
@patch('main.inquirer.text')
def test_edit_item__not_confirmed(text_mock, confirm_mock, item_1):
    item_1.name = 'My item'

    text_mock.return_value.execute.return_value = 'Something'
    confirm_mock.return_value.execute.return_value = False

    main.edit_item(item_1)

    assert item_1.name == 'My item'


@patch('main.inquirer.confirm')
@patch('main.inquirer.text')
def test_edit_item__asserting_name(text_mock, confirm_mock, item_1):
    item_1.name = 'My item'

    text_mock.return_value.execute.return_value = 'Something'
    confirm_mock.return_value.execute.return_value = True

    main.edit_item(item_1)

    assert item_1.name == 'Something'


@patch('main.inquirer.confirm')
@patch('main.inquirer.text')
def test_edit_item__asserting_description(text_mock, confirm_mock, item_1):
    text_mock.return_value.execute.side_effect = [
        'Item name',
        'Item description',
    ]
    confirm_mock.return_value.execute.return_value = True

    main.edit_item(item_1)

    assert item_1.description == 'Item description'


@patch('main.inquirer.confirm')
@patch('main.inquirer.text')
def test_edit_item__without_changing_tags(
    text_mock, confirm_mock, item_1, tag_1
):
    item_1.tags = [tag_1]

    text_mock.return_value.execute.return_value = 'Something'
    confirm_mock.return_value.execute.return_value = True

    main.edit_item(item_1)

    assert item_1.tags == [tag_1]


def test_get_grouped_tag_list_as_choices__without_tags():
    result = main.get_grouped_tag_list_as_choices(
        group_name='Tag group', tag_list=[], tag_ids_to_select=[]
    )

    assert result == []


def test_get_grouped_tag_list_as_choices__first_item_is_a_separator(item_1):
    result = main.get_grouped_tag_list_as_choices(
        group_name='Tag group', tag_list=[item_1], tag_ids_to_select=[]
    )

    assert isinstance(result[0], Separator)


def test_get_grouped_tag_list_as_choices__separator_as_group_name(item_1):
    result = main.get_grouped_tag_list_as_choices(
        group_name='Tag group', tag_list=[item_1], tag_ids_to_select=[]
    )

    assert str(result[0]) == 'Tag group'


def test_get_grouped_tag_list_as_choices__second_item_is_a_choice(tag_1):
    result = main.get_grouped_tag_list_as_choices(
        group_name='Tag group', tag_list=[tag_1], tag_ids_to_select=[]
    )

    assert isinstance(result[1], Choice)


def test_get_tag_list_as_choices__choice_with_tag_name(tag_1):
    result = main.get_tag_list_as_choices(
        tag_list=[tag_1], tag_ids_to_select=[]
    )

    assert str(result[0].name) == str(tag_1)


def test_get_tag_list_as_choices__no_tag_selected(tag_1, tag_2):
    result = main.get_tag_list_as_choices(
        tag_list=[tag_1, tag_2], tag_ids_to_select=[]
    )

    assert not result[0].enabled and not result[1].enabled


def test_get_tag_list_as_choices__first_tag_selected(tag_1, tag_2):
    result = main.get_tag_list_as_choices(
        tag_list=[tag_1, tag_2], tag_ids_to_select=[tag_1.id]
    )

    assert result[0].enabled and not result[1].enabled


def test_get_tag_list_as_choices__second_tag_selected(tag_1, tag_2):
    result = main.get_tag_list_as_choices(
        tag_list=[tag_1, tag_2], tag_ids_to_select=[tag_2.id]
    )

    assert not result[0].enabled and result[1].enabled


def test_get_tag_list_as_choices__all_tags_selected(tag_1, tag_2):
    result = main.get_tag_list_as_choices(
        tag_list=[tag_1, tag_2], tag_ids_to_select=[tag_1.id, tag_2.id]
    )

    assert result[0].enabled and result[1].enabled


def test_edit_item_tags__no_tags_message(capsys, item_1):
    main.edit_item_tags(item_1)
    out, _ = capsys.readouterr()

    assert 'no tags' in out


@patch('main.inquirer.checkbox')
def test_edit_item_tags__no_tags_to_select(mock, item_1):
    main.edit_item_tags(item_1)

    assert not mock.call_count


@patch('main.inquirer.checkbox')
def test_edit_item_tags__with_tags(mock, item_1, tag_1):
    main.edit_item_tags(item_1)

    assert mock.call_count


@patch('main.inquirer.checkbox')
@patch('main.get_grouped_tag_list_as_choices')
def test_edit_item_tags__grouping_child_tag(
    mock_1, checkbox_mock, item_1, child_tag_1_of_parent_tag_1
):
    mock_1.return_value = []
    checkbox_mock.return_value.execute.return_value = []

    main.edit_item_tags(item_1)

    assert mock_1.call_count


@patch('main.inquirer.checkbox')
@patch('main.get_grouped_tag_list_as_choices')
def test_edit_item_tags__grouping_independent_tag(
    mock_1, checkbox_mock, item_1, tag_1
):
    mock_1.return_value = []
    checkbox_mock.return_value.execute.return_value = []

    main.edit_item_tags(item_1)

    assert mock_1.call_args.kwargs['group_name'] == 'Independent'


@patch('main.inquirer.checkbox')
def test_edit_item_tags__setting_tags(mock, item_1, tag_1):
    mock.return_value.execute.return_value = [tag_1.id]

    main.edit_item_tags(item_1)

    assert item_1.tags == [tag_1]


def test_validate_selected_item_tags__with_independent_tags(
    tag_1, child_tag_1_of_parent_tag_1
):
    tag_id_list = [
        tag_1.id,
        child_tag_1_of_parent_tag_1.id,
    ]

    assert main.validate_selected_item_tags(tag_id_list)


def test_validate_selected_item_tags__with_two_tags_from_the_same_group(
    child_tag_1_of_parent_tag_1, child_tag_2_of_parent_tag_1
):
    tag_id_list = [
        child_tag_1_of_parent_tag_1.id,
        child_tag_2_of_parent_tag_1.id,
    ]

    assert not main.validate_selected_item_tags(tag_id_list)
