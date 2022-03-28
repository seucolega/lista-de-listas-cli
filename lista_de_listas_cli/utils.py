import os
from typing import Any, Callable, Union

import facade
import schemas


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def return_to(function: Callable):
    def inner(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
        finally:
            if isinstance(kwargs.get('return_func'), Callable):
                return_func = kwargs.pop('return_func')
                return_args = kwargs.get('return_args', {})
                if 'return_choice' in kwargs:
                    return_choice = kwargs.pop('return_choice')
                    return_args['default_choice'] = return_choice
                return_func(**return_args)

        return result

    return inner


# def decorator_factory(argument):
#     def decorator(function):
#         def wrapper(*args, **kwargs):
#             # funny_stuff()
#             # something_with_argument(argument)
#             # result = function(*args, **kwargs)
#             # more_funny_stuff()
#             return result
#
#         return wrapper
#
#     return decorator


# def decorator_with_arguments(arg1, arg2, arg3):
#     def wrap(f):
#         print("Inside wrap()")
#
#         def wrapped_f(*args):
#             print("Inside wrapped_f()")
#             print("Decorator arguments:", arg1, arg2, arg3)
#             f(*args)
#             print("After f(*args)")
#
#         return wrapped_f
#
#     return wrap
#
#
# @decorator_with_arguments("hello", "world", 42)
# def say_hello(a1, a2, a3, a4):
#     print('say_hello arguments:', a1, a2, a3, a4)


def get_selected_items_info(action: list) -> Union[Any, str, None]:
    if len(action):
        if len(action) > 1:
            return f'{len(action)} items selected'

        return action[0]

    return None


def init_tags():
    status_tag = schemas.TagCreate(name='Status')
    if not facade.get_tag_by_name(status_tag.name):
        status_tag = facade.create_tag(status_tag)

    sub_tags = ['Next', 'Waiting', 'Schedule', 'Someday']
    for tag_name in sub_tags:
        if not facade.get_tag_by_name(tag_name):
            tag = schemas.TagCreate(name=tag_name, parent_id=status_tag.id)
            facade.create_tag(tag)

    status_tag = schemas.TagCreate(name='Area')
    if not facade.get_tag_by_name(status_tag.name):
        status_tag = facade.create_tag(status_tag)

    sub_tags = ['Personal', 'Work']
    for tag_name in sub_tags:
        if not facade.get_tag_by_name(tag_name):
            tag = schemas.TagCreate(name=tag_name, parent_id=status_tag.id)
            facade.create_tag(tag)
