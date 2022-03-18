from unittest.mock import patch

import main
import pytest


@pytest.fixture(autouse=True)
def configure_db_session(db_session):
    main.db_session = db_session


def test_hello_world(runner):
    result = runner.invoke(main.hello_command, ['people'])

    assert result.exit_code == 0
    assert result.output == 'Hello people!\n'


@patch('main.show_items')
def test_list_command(mock, runner):
    mock.return_value.exit_code.return_value = 0

    result = runner.invoke(main.list_command)

    assert result.exit_code == 0


def test_add_command(runner):
    result = runner.invoke(main.add_command, ['A task'])

    assert result.exit_code == 0


def test_show_items__no_items(capsys):
    main.show_items([])
    out, _ = capsys.readouterr()

    assert 'no items' in out
