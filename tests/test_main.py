from unittest.mock import patch

import facade
import main
import pytest


@pytest.fixture(autouse=True)
def configure_db_session(db_session):
    main.db_session = db_session
    facade.db_session = db_session


# def test_hello_world(runner):
#     result = runner.invoke(main.hello_command, ['people'])
#
#     assert result.exit_code == 0
#     assert result.output == 'Hello people!\n'


@patch('main.show_items')
def test_list_command__exists(mock, runner):
    runner.invoke(main.list_command)

    assert mock.call_count


def test_add_command(runner):
    result = runner.invoke(main.add_command, ['A task'])

    assert result.exit_code == 0


def test_show_items__no_items(capsys):
    main.show_items([])
    out, _ = capsys.readouterr()

    assert 'no items' in out


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

    assert [choice for choice in choices if 'Inbox' in choice.name]


def test_choices_for_interactive_menu__has_exit_choice():
    choices = main.choices_for_interactive_menu()

    assert [choice for choice in choices if 'Exit' in choice.name]


def test_choices_for_interactive_menu__has_manage_tags_choice():
    choices = main.choices_for_interactive_menu()

    assert [choice for choice in choices if 'Manage tags' in choice.name]


def test_choices_for_interactive_menu__has_context_choice(item_1, tag_1):
    item_1.tags = [tag_1]

    choices = main.choices_for_interactive_menu()

    assert [choice for choice in choices if 'Context' in choice.name]


def test_choices_for_interactive_menu__has_the_tag_name_choice(item_1, tag_1):
    item_1.tags = [tag_1]
    tag_1.name = 'My tag'

    choices = main.choices_for_interactive_menu()

    assert [choice for choice in choices if tag_1.name in choice.name]


@patch('main.init_tags')
def test_init_tags_command__calls_init_tags(mock, runner):
    runner.invoke(main.init_tags_command)

    assert mock.call_count


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
def test_create_item__item_tags_called(
    text_mock, confirm_mock, edit_item_tags_mock, runner
):
    text_mock.return_value.execute.return_value = 'Something'
    confirm_mock.return_value.execute.return_value = True
    edit_item_tags_mock.return_value = None

    main.create_item()

    assert edit_item_tags_mock.call_count


@patch('main.inquirer.confirm')
@patch('main.inquirer.text')
def test_create_tag__with_name_and_confirm_called(
    text_mock, confirm_mock, runner
):
    text_mock.return_value.execute.return_value = 'Something'
    confirm_mock.return_value.execute.return_value = False

    main.create_tag()

    assert confirm_mock.call_count


@patch('facade.create_tag')
@patch('main.inquirer.confirm')
@patch('main.inquirer.text')
def test_create_tag__with_name_and_not_confirmed(
    text_mock, confirm_mock, create_tag_mock, runner
):
    text_mock.return_value.execute.return_value = 'Something'
    confirm_mock.return_value.execute.return_value = False

    main.create_tag()

    assert not create_tag_mock.call_count


@patch('main.inquirer.confirm')
@patch('main.inquirer.text')
def test_create_tag__with_name_and_confirmed(text_mock, confirm_mock, runner):
    text_mock.return_value.execute.return_value = 'Something'
    confirm_mock.return_value.execute.return_value = True

    main.create_tag()

    assert len(facade.get_tag_list()) == 1
