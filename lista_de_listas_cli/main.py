from typing import List, Union

import click
import facade
import models
import schemas
from database import Base, db_session, engine
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from utils import clear_screen, get_selected_items_info, return_to


@click.group()
def cli():
    pass


# @click.command(name='hello')
# @click.argument('name')
# def hello_command(name):
#     click.echo(f'Hello {name}!')


@cli.command(name='list')
def list_command():
    show_items(item_list=facade.get_actionable_items())


@cli.command(name='add')
@click.argument('name')
def add_command(name: str):
    item = schemas.ItemCreate(name=name)

    facade.create_item(item)


# @cli.command(name='reset')
# def reset_command():
#     for tbl in reversed(Base.metadata.sorted_tables):
#         engine.execute(tbl.delete())


@cli.command(name='interactive')
def interactive_command():
    start_interactive()


def choices_for_interactive_menu() -> List[Union[Choice, Separator]]:
    choices = [
        Choice('create', name='New item'),
        Choice('inbox', name='Inbox'),
    ]

    tag_list = facade.get_actionable_tag_list()
    for tag in tag_list:
        choices.append(Choice(f'tag.{tag.id}', name=f'Context {tag.name}'))

    choices += [
        # Choice('all', name='All items'),
        Choice('actionable', name='Actionable items'),
        # Choice('non_actionable', name='Non-actionable items'),
        Separator(line=''),
        Choice(value=None, name='Exit'),
    ]

    return choices


def start_interactive(default_choice: int = None):
    clear_screen()

    choices = choices_for_interactive_menu()

    action = inquirer.select(
        message='Select an action:',
        choices=choices,
        default=default_choice or choices[0].value,
    ).execute()

    if action:
        return_to_kwargs = {
            'return_func': start_interactive,
            'return_choice': action,
        }

        if action == 'create':
            create_item(**return_to_kwargs)
        elif action == 'inbox':
            show_items(item_list=facade.get_inbox_items(), **return_to_kwargs)
        elif action == 'actionable':
            show_items(
                item_list=facade.get_actionable_items(), **return_to_kwargs
            )
        elif action.startswith('tag.'):
            tag_id = int(action[4:])

            item_list = (
                db_session.query(models.Item)
                .filter(models.Item.tags.any(id=tag_id))
                .all()
            )

            show_items(item_list=item_list, **return_to_kwargs)


@return_to
def create_item(**_):
    item = schemas.ItemCreate(
        name=inquirer.text(message='Enter the item title:').execute()
    )

    if inquirer.confirm(message='Confirm?').execute():
        facade.create_item(item)


@return_to
def edit_item(item: schemas.Item, **_):
    item.name = inquirer.text(
        message='Enter the item title:', default=item.name
    ).execute()

    if inquirer.confirm(message='Confirm?').execute():
        db_session.commit()
    else:
        db_session.rollback()


@return_to
def edit_item_tags(item: schemas.Item, default_choice: int = None, **_):
    tag_list = facade.get_tag_list()

    if not tag_list:
        click.echo('There are no tags to display.')
        return

    choices = []
    for tag in tag_list:
        choices.append(Choice(tag.id, name=tag.name))

    choices += [Separator(line=''), Choice(value=None, name='Return')]

    action = inquirer.select(
        message='Select one or more tags:',
        choices=choices,
        default=default_choice or choices[0].value,
        multiselect=True,
        transformer=lambda result: get_selected_items_info(result),
    ).execute()

    if action:
        for tag_id in action:
            tag = facade.get_tag(tag_id=tag_id)
            if tag:
                item.tags.append(tag)

        db_session.commit()


@return_to
def show_item_options(item: schemas.Item, **_):
    choices = [
        Choice(schemas.ItemStatus.DONE, name='Done'),
        Choice(schemas.ItemStatus.WONT, name="Won't do"),
        Choice('edit', name='Edit'),
        # Choice('subtask', name='Add subtask'),
        # Choice('move-to', name='Move to'),
        Choice('tags', name='Tags'),
        # Choice('duplicate', name='Duplicate'),
        Choice(schemas.ItemStatus.NOTE, name='Convert to note'),
        # Choice('delete', name='Delete'),
        Separator(line=''),
        Choice(value=None, name='Return'),
    ]

    action = inquirer.select(
        message='Select an action:',
        choices=choices,
        default=choices[0].value,
    ).execute()

    if isinstance(action, schemas.ItemStatus):
        facade.set_item_status(item=item, status=action)
    elif action == 'edit':
        edit_item(item=item)
    elif action == 'tags':
        edit_item_tags(item=item)


@return_to
def show_items(item_list: [schemas.Item], default_choice: int = None, **_):
    if not item_list:
        click.echo('There are no items to display.')
        return

    choices = []
    for item in item_list:
        choices.append(Choice(item.id, name=item.name))

    choices += [Separator(line=''), Choice(value=None, name='Return')]

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
            item = facade.get_item(item_id=item_id)
            if item:
                show_item_options(item)
        else:
            ...


@cli.command(name='init_tags')
def init_tags_command():
    init_tags()


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


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    try:
        cli()
    finally:
        db_session.close()
