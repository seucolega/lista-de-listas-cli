import click
import facade
import schemas
from database import db_session
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from utils import clear_screen, get_selected_items_info, return_to


@click.group()
def cli():
    pass


@click.command(name='hello')
@click.argument('name')
def hello_command(name):
    click.echo(f'Hello {name}!')


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


def start_interactive(default_choice: int = None):
    clear_screen()

    choices = [
        Choice('create_item', name='Create a new item'),
        # Choice('list_all', name='Show all items'),
        Choice('list_actionable', name='Show actionable items'),
        # Choice('list_non_actionable', name='Show non-actionable items'),
        Separator(line='----'),
        Choice(value=None, name='Exit'),
    ]

    action = inquirer.select(
        message='Select an action:',
        choices=choices,
        default=default_choice or choices[0].value,
    ).execute()

    if not action:
        return

    return_to_kwargs = {
        'return_func': start_interactive,
        'return_choice': action,
    }

    if action == 'create_item':
        create_item(**return_to_kwargs)
    elif action == 'list_actionable':
        show_items(item_list=facade.get_actionable_items(), **return_to_kwargs)


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
def show_item_options(item: schemas.Item, **_):
    choices = [
        Choice(schemas.ItemStatus.DONE, name='Done'),
        Choice('edit', name='Edit'),
        # Choice('subtask', name='Add subtask'),
        Choice(schemas.ItemStatus.WONT, name="Won't do"),
        # Choice('move-to', name='Move to'),
        # Choice('tags', name='Tags'),
        # Choice('duplicate', name='Duplicate'),
        Choice(schemas.ItemStatus.NOTE, name='Convert to note'),
        # Choice('delete', name='Delete'),
        Separator(line='------'),
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


@return_to
def show_items(item_list: [schemas.Item], default_choice: int = None, **_):
    if not item_list:
        click.echo('There are no items to display.')
        return

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
            item = facade.get_item(item_id=item_id)
            if item:
                show_item_options(item)
        else:
            ...


if __name__ == '__main__':
    try:
        cli()
    finally:
        db_session.close()
