import time
from typing import Callable, List, Union

import click
import facade
import models
import schemas
from database import Base, db_session, engine
from InquirerPy import inquirer
from InquirerPy.base.control import Choice, Separator
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
    show_items(facade.get_actionable_items)


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

    tag_list = facade.get_list_of_tags_with_actionable_items()
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
            show_items(facade.get_inbox_items, **return_to_kwargs)
        elif action == 'actionable':
            show_items(facade.get_actionable_items, **return_to_kwargs)
        elif action == 'tags':
            show_tags(**return_to_kwargs)
        elif action.startswith('tag.'):
            tag_id = int(action[4:])

            show_items(
                facade.get_actionable_items_with_the_tag,
                context=facade.get_tag(tag_id),
                **return_to_kwargs,
            )


def name_is_valid(value: str) -> bool:
    return value.strip() != ''


def questions_when_creating_or_editing_an_item(
    item: models.Item = None,
) -> schemas.ItemCreate:
    new_data = item.__dict__.copy() if item else {}

    new_data['name'] = inquirer.text(
        message='Enter the title:',
        default=item.name if item else '',
        validate=name_is_valid,
        invalid_message='Name cannot be empty.',
    ).execute()

    new_data['description'] = (
        inquirer.text(
            message='Enter the description:',
            multiline=True,
            default=(item.description if item else None) or '',
        ).execute()
        or None
    )

    return schemas.ItemCreate(**new_data)


@return_to
def create_item(**_) -> Union[models.Item, None]:
    item = questions_when_creating_or_editing_an_item()

    if inquirer.confirm(message='Confirm?', default=True).execute():
        item = facade.create_item(item)
        edit_item_tags(item)

        db_session.commit()

        return item

    return None


@return_to
def edit_item(item: models.Item, **_):
    new_data = questions_when_creating_or_editing_an_item(item)

    if inquirer.confirm(message='Confirm?', default=True).execute():
        for (key, value) in new_data.dict().items():
            setattr(item, key, value)

        db_session.commit()


def validate_selected_item_tags(tag_id_list: [int]) -> bool:
    parent_list = []

    for tag_id in tag_id_list:
        tag = facade.get_tag(tag_id)

        if tag.parent_id:
            if tag.parent_id in parent_list:
                return False

            parent_list.append(tag.parent_id)

    return True


def get_grouped_tag_list_as_choices(
    group_name: str, tag_list: [models.Tag], tag_ids_to_select: [int]
) -> [Union[Separator, Choice]]:
    if tag_list:
        return [
            Separator(group_name),
            *get_tag_list_as_choices(
                tag_list=tag_list, tag_ids_to_select=tag_ids_to_select
            ),
        ]

    return []


def get_tag_list_as_choices(
    tag_list: [models.Tag], tag_ids_to_select: [int]
) -> [Choice]:
    result = []

    for tag in tag_list:
        choice_enabled = tag.id in tag_ids_to_select
        result.append(Choice(tag.id, name=tag.name, enabled=choice_enabled))

    return result


@return_to
def edit_item_tags(item: models.Item, **_):
    parent_list = facade.get_tag_list_without_parent()

    if not parent_list:
        click.echo('There are no tags to display.')
        return

    item_tag_id_list = [tag.id for tag in item.tags]
    choices = []
    tags_with_children = [tag for tag in parent_list if tag.children]
    independent_tags = [tag for tag in parent_list if not tag.children]

    for tag_list in tags_with_children:
        choices.extend(
            get_grouped_tag_list_as_choices(
                group_name=tag_list.name,
                tag_list=tag_list.children,
                tag_ids_to_select=item_tag_id_list,
            )
        )

    if independent_tags:
        choices.extend(
            get_grouped_tag_list_as_choices(
                group_name='Independent',
                tag_list=independent_tags,
                tag_ids_to_select=item_tag_id_list,
            )
        )

    action = inquirer.checkbox(
        message='Select one or more tags:',
        choices=choices,
        validate=validate_selected_item_tags,
        invalid_message='Select only one tag per group',
        transformer=get_selected_items_info,
    ).execute()

    tags = []
    for tag_id in action:
        tag = facade.get_tag(tag_id)
        if tag:
            tags.append(tag)
    item.tags = tags

    db_session.commit()


@return_to
def show_item_options(item: models.Item, **_):
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
    function_to_get_items: Callable,
    context: models.Tag = None,
    default_choice: int = None,
    **_,
):
    arguments = [context] if context else []
    item_list = function_to_get_items(*arguments)

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
        transformer=get_selected_items_info,
    ).execute()

    if select_items:
        if len(select_items) == 1:
            item_id = select_items[0]
            item = facade.get_item(item_id)
            if item:
                show_item_options(
                    item=item,
                    return_func=show_items,
                    return_args={
                        'function_to_get_items': function_to_get_items,
                        'default_choice': item_id,
                    },
                )
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


def questions_when_creating_or_editing_a_tag(
    tag: models.Tag = None,
) -> schemas.TagCreate:
    new_data = tag.__dict__.copy() if tag else {}

    new_data['name'] = inquirer.text(
        message='Enter the tag title:',
        default=tag.name if tag else '',
        validate=name_is_valid,
        invalid_message='Name cannot be empty.',
    ).execute()

    parent_id = ask_for_parent_tag_when_editing_a_tag(
        tag.parent_id if tag else None
    )

    if parent_id:
        new_data['parent_id'] = parent_id

    return schemas.TagCreate(**new_data)


@return_to
def create_tag(**_) -> Union[models.Tag, None]:
    tag = questions_when_creating_or_editing_a_tag()

    if inquirer.confirm(message='Confirm?', default=True).execute():
        tag = facade.create_tag(tag)

        db_session.commit()

        return tag

    return None


@return_to
def show_tag_options(tag: models.Tag, **_):
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
def edit_tag(tag: models.Tag, **_):
    new_data = questions_when_creating_or_editing_a_tag(tag)

    if inquirer.confirm(message='Confirm?', default=True).execute():
        for (key, value) in new_data.dict().items():
            setattr(tag, key, value)

        db_session.commit()


def ask_for_parent_tag_when_editing_a_tag(default_choice: int = None):
    choices = [Choice(value=None, name='No parent tag')]

    for tag_list_item in facade.get_tag_list_without_parent():
        choices.append(Choice(tag_list_item.id, name=tag_list_item.name))

    return inquirer.select(
        message='Select a parent tag:',
        choices=choices,
        default=default_choice,
    ).execute()


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    try:
        cli()
    finally:
        db_session.close()
