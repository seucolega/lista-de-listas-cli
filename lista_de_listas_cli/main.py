import time
from typing import List

import click
import facade
import models
import schemas
from database import Base, db_session, engine
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from utils import clear_screen, get_selected_items_info, init_tags, return_to


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


@cli.command(name='interactive')
def interactive_command():
    start_interactive()


@cli.command(name='init_tags')
def init_tags_command():
    init_tags()


# @cli.command(name='reset')
# def reset_command():
#     for tbl in reversed(Base.metadata.sorted_tables):
#         engine.execute(tbl.delete())


def choices_for_interactive_menu() -> List[Choice]:
    choices = [Choice('create', name='New item')]

    if facade.get_inbox_items(limit=1):
        choices.append(Choice('inbox', name='Inbox'))

    tag_list = facade.get_list_of_tags_with_items()
    for tag in tag_list:
        choices.append(Choice(f'tag.{tag.id}', name=f'Context {tag.name}'))

    choices += [
        # Choice('all', name='All items'),
        Choice('actionable', name='Actionable items'),
        # Choice('non_actionable', name='Non-actionable items'),
        Choice('tags', name='Manage tags'),
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
        elif action == 'tags':
            show_tags(**return_to_kwargs)
        elif action.startswith('tag.'):
            tag_id = int(action[4:])

            item_list = facade.get_actionable_items_with_the_tag(tag_id)

            show_items(
                item_list=item_list,
                context=facade.get_tag(tag_id),
                **return_to_kwargs,
            )


@return_to
def create_item(**_):
    item = schemas.ItemCreate(
        name=inquirer.text(message='Enter the item title:').execute()
    )

    if inquirer.confirm(message='Confirm?', default=True).execute():
        item = facade.create_item(item)
        edit_item_tags(item)


@return_to
def edit_item(item: schemas.Item, **_):
    item.name = inquirer.text(
        message='Enter the item title:', default=item.name
    ).execute()

    if inquirer.confirm(message='Confirm?', default=True).execute():
        db_session.commit()
    else:
        db_session.rollback()


@return_to
def edit_item_tags(item: schemas.Item, **_):
    tag_list = facade.get_actionable_tag_list()

    if not tag_list:
        click.echo('There are no tags to display.')
        return

    item_tag_id_list = [tag.id for tag in item.tags]
    choices = []

    for tag in tag_list:
        choice_enabled = tag.id in item_tag_id_list
        choices.append(Choice(tag.id, name=tag.name, enabled=choice_enabled))

    action = inquirer.checkbox(
        message='Select one or more tags:',
        choices=choices,
        transformer=lambda result: get_selected_items_info(result),
    ).execute()

    tags = []
    for tag_id in action:
        tag = facade.get_tag(tag_id)
        if tag:
            tags.append(tag)
    item.tags = tags

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
        edit_item(item)
    elif action == 'tags':
        edit_item_tags(item)


@return_to
def show_items(
    item_list: [schemas.Item],
    context: schemas.Tag = None,
    default_choice: int = None,
    **_,
):
    if not item_list:
        # TODO: Create a function to show the message and wait a second
        click.echo('There are no items to display.')
        time.sleep(1)
        return

    choices = []

    for item in item_list:
        choice_name = facade.get_item_text_to_show(item, context=context)
        choices.append(Choice(item.id, name=choice_name))

    choices.append(Choice(value=None, name='Return'))

    select_items = inquirer.select(
        message='Select one or more items:',
        choices=choices,
        default=default_choice or choices[0].value,
        multiselect=True,
        transformer=lambda result: get_selected_items_info(result),
    ).execute()

    if select_items:
        if len(select_items) == 1:
            item_id = select_items[0]
            item = facade.get_item(item_id)
            if item:
                show_item_options(item)
        else:
            ...


@return_to
def show_tags(default_choice: int = None, **_):
    tag_list = facade.get_tag_list()

    if not tag_list:
        click.echo('There are no items to display.')
        time.sleep(1)
        return

    choices = [Choice('create', name='New tag')]

    for tag in tag_list:
        choices.append(Choice(tag.id, name=facade.get_tag_text_to_show(tag)))

    choices.append(Choice(value=None, name='Return'))

    action = inquirer.select(
        message='Select an action:',
        choices=choices,
        default=default_choice or choices[0].value,
    ).execute()

    if action:
        return_to_kwargs = {
            'return_func': show_tags,
            'return_choice': action,
        }

        if action == 'create':
            create_tag(**return_to_kwargs)
        else:
            tag = facade.get_tag(action)
            if tag:
                show_tag_options(tag)


@return_to
def create_tag(**_):
    tag = schemas.TagCreate(
        name=inquirer.text(message='Enter the tag title:').execute()
    )

    if inquirer.confirm(message='Confirm?', default=True).execute():
        facade.create_tag(tag)


@return_to
def show_tag_options(tag: schemas.Tag, **_):
    choices = [
        Choice('edit', name='Edit'),
        # Choice('delete', name='Delete'),
        Choice(value=None, name='Return'),
    ]

    action = inquirer.select(
        message='Select an action:',
        choices=choices,
        default=choices[0].value,
    ).execute()

    if action == 'edit':
        edit_tag(tag)


@return_to
def edit_tag(tag: schemas.Tag, **_):
    tag.name = inquirer.text(
        message='Enter the tag title:', default=tag.name
    ).execute()

    if inquirer.confirm(message='Confirm?', default=True).execute():
        db_session.commit()
    else:
        db_session.rollback()


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    try:
        cli()
    finally:
        db_session.close()
