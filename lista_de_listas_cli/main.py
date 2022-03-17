from typing import Callable

import click
import facade
import schemas
from database import Base, SessionLocal, engine
from InquirerPy import inquirer, prompt
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator


def init_db():
    Base.metadata.create_all(bind=engine)


@click.group()
def cli():
    pass


@click.command(name='hello')
@click.argument('name')
def hello_command(name):
    click.echo(f'Hello {name}!')


@cli.command(name='list')
def cli_list():
    start_to_show_items(
        item_list=facade.get_actionable_items(db_session=db_session)
    )


@cli.command(name='add')
@click.argument('name')
def add_command(name: str):
    item = schemas.ItemCreate(name=name)

    facade.create_item(db_session=db_session, item=item)


@cli.command(name='reset')
def reset_command():
    for tbl in reversed(Base.metadata.sorted_tables):
        engine.execute(tbl.delete())


@cli.command(name='interactive')
def interactive_command():
    start_interactive()


def start_interactive(default_choice: int = None):
    # click.echo('')

    choices = [
        Choice('create', name='Create a new item'),
        # Choice('list_all', name='Show all items'),
        Choice('list_actionable', name='Show actionable items'),
        Choice('list_non_actionable', name='Show non-actionable items'),
        Separator(line='----'),
        Choice(value=None, name='Exit'),
    ]

    action = inquirer.select(
        message='Select an action:',
        choices=choices,
        default=default_choice or choices[0].value,
    ).execute()

    return_to_kwargs = {
        'return_func': start_interactive,
        'return_args': {'default_choice': action},
    }

    # if action:
    #     click.echo('')

    # if action == 'list_all':
    #     start_to_show_items(
    #         item_list=facade.get_all_items(db_session=db_session),
    #     )
    if action == 'list_actionable':
        start_to_show_items(
            item_list=facade.get_actionable_items(db_session=db_session),
            return_func=start_interactive,
        )
    # elif action == 'list_non_actionable':
    #     start_to_show_items(
    #         item_list=facade.get_actionable_items(db_session=db_session),
    #     )
    elif action == 'create':
        create_item(**return_to_kwargs)


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


def return_to(function):
    def inner(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
        finally:
            return_func = kwargs.get('return_func')
            if isinstance(return_func, Callable):
                return_func(**kwargs.get('return_args', {}))

        return result

    return inner


@return_to
def start_to_show_items(item_list: [schemas.Item], **_):
    if item_list:
        show_items(item_list)
    else:
        click.echo('There are no items to display.')


@return_to
def create_item(**_):
    # item = schemas.ItemCreate(
    #     name=inquirer.text(message='Enter the item title:').execute()
    # )

    questions = [
        {'type': 'input', 'message': 'Enter the item title:', 'name': 'name'},
        {'type': 'confirm', 'message': 'Confirm?', 'name': 'confirm'},
    ]
    result = prompt(questions)

    if result['confirm']:
        item = schemas.ItemCreate(name=result['name'])

        facade.create_item(db_session=db_session, item=item)


@return_to
def show_item_options(item: schemas.Item, **_):
    # click.echo('')

    choices = [
        Choice('done', name='Done'),
        # Choice('edit', name='Edit'),
        # Choice('subtask', name='Add subtask'),
        # Choice('wont-do', name='Won\'t do'),
        # Choice('move-to', name='Move to'),
        # Choice('tags', name='Tags'),
        # Choice('duplicate', name='Duplicate'),
        # Choice('note', name='Convert to note'),
        # Choice('delete', name='Delete'),
        Separator(line='------'),
        Choice(value=None, name='Return'),
    ]

    action = inquirer.select(
        message='Select an action:',
        choices=choices,
        default=choices[0].value,
    ).execute()

    if action == 'done':
        item.status = schemas.ItemStatus.DONE
        db_session.commit()


def get_selected_items_info(action: list):
    if len(action):
        if len(action) > 1:
            return (
                f"{len(action)} item{'s' if len(action) > 1 else ''} selected",
            )
        return action[0]


def show_items(item_list: [schemas.Item], default_choice: int = None):
    choices = []
    for item in item_list:
        choices.append(Choice(item.id, name=item.name))

    choices += [Separator(line='------'), Choice(value=None, name='Return')]

    action = inquirer.select(
        message='Select one or more items:',
        choices=choices,
        default=default_choice or choices[0].value,
        multiselect=True,
        transformer=lambda result: get_selected_items_info(result),
    ).execute()

    if action:
        if len(action) == 1:
            item_id = action[0]
            item = facade.get_item(db_session=db_session, item_id=item_id)
            if item:
                show_item_options(
                    item,
                    # return_func=show_items,
                    # return_args={
                    #     'item_list': item_list,
                    #     'default_choice': item_id,
                    # },
                )
        else:
            ...


if __name__ == '__main__':
    init_db()

    db_session = SessionLocal()
    try:
        cli()
    finally:
        db_session.close()

    # say_hello('qwe', 'asd', 'zxc', 'rty')
