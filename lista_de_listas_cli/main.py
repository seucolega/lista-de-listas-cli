import click

import facade
import schemas
from database import Base, SessionLocal, engine
from facade import get_item_list


def init_db():
    Base.metadata.create_all(bind=engine)


@click.command()
@click.argument('name')
def hello(name):
    click.echo(f'Hello {name}!')


@click.group()
def cli():
    pass


@cli.command()
def lst():
    item_list = get_item_list(db_session=db_session)

    for item in item_list:
        click.echo(item)


@cli.command()
@click.argument('name')
def add(name: str):
    item = schemas.ItemCreate(name=name)
    facade.create_item(db_session=db_session, item=item)


@cli.command()
def reset():
    for tbl in reversed(Base.metadata.sorted_tables):
        engine.execute(tbl.delete())


if __name__ == '__main__':
    init_db()

    db_session = SessionLocal()
    try:
        cli()
    finally:
        db_session.close()
