from unittest.mock import Mock

import pytest
import utils


def test_clear_screen(capsys):
    utils.clear_screen()
    out, error = capsys.readouterr()

    assert not out + error


def test_return_to__called():
    @utils.return_to
    def function_to_call(**_):
        pass

    function_to_return = Mock()

    function_to_call(return_func=function_to_return)

    function_to_return.assert_called_once()


def test_return_to__called_with_return_args():
    @utils.return_to
    def function_to_call(**_):
        pass

    function_to_return = Mock()
    return_args = {'id': 1}

    function_to_call(return_func=function_to_return, return_args=return_args)

    function_to_return.assert_called_once_with(**return_args)


def test_return_to__called_with_return_choice():
    @utils.return_to
    def function_to_call(**_):
        pass

    function_to_return = Mock()

    function_to_call(return_func=function_to_return, return_choice=1)

    function_to_return.assert_called_once_with(default_choice=1)


def test_get_selected_items_info__no_items():
    assert utils.get_selected_items_info([]) is None


def test_get_selected_items_info__with_one_item():
    assert utils.get_selected_items_info([1]) == 1


def test_get_selected_items_info__with_two_items():
    assert utils.get_selected_items_info([1, 2]) == '2 items selected'
