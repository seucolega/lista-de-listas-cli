import os

import facade
import pytest as pytest
import schemas
from click.testing import CliRunner
from database import Base
from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

SQLALCHEMY_DATABASE_URL = config(
    'DATABASE_TEST_URL', f'sqlite:///{os.path.dirname(__file__)}/test.db'
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)


@pytest.fixture(scope='session', autouse=True)
def create_test_database():
    """Create a clean database on every test case.

    We use the `sqlalchemy_utils` package here for a few helpers in
    consistently creating and dropping the database.
    """
    if database_exists(SQLALCHEMY_DATABASE_URL):
        drop_database(SQLALCHEMY_DATABASE_URL)

    create_database(SQLALCHEMY_DATABASE_URL)  # Create the test database.
    Base.metadata.create_all(engine)  # Create the tables.

    yield  # Run the tests.

    drop_database(SQLALCHEMY_DATABASE_URL)  # Drop the test database.


@pytest.fixture(autouse=True)
def db_session():
    """Returns a sqlalchemy session, and after the test tears down everything
    properly."""
    session_local = sessionmaker(bind=engine)
    session: Session = session_local()

    yield session

    session.rollback()

    # Drop all data after each test
    for tbl in reversed(Base.metadata.sorted_tables):
        engine.execute(tbl.delete())

    # put back the connection to the connection pool
    session.close()


@pytest.fixture(autouse=True)
def configure_db_session(db_session):
    facade.db_session = db_session


@pytest.fixture
def item_1(db_session):
    item = schemas.ItemCreate(name='Something')

    return facade.create_item(item=item)


@pytest.fixture
def done_item_1(db_session):
    item = schemas.ItemCreate(name='Something', status=schemas.ItemStatus.DONE)

    return facade.create_item(item=item)


@pytest.fixture
def undone_item_1(db_session):
    item = schemas.ItemCreate(
        name='Something', status=schemas.ItemStatus.UNDONE
    )

    return facade.create_item(item=item)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tag_1(db_session):
    return facade.create_tag(
        schemas.TagCreate(name='Tag name', parent_id=None)
    )


@pytest.fixture
def tag_2(db_session):
    return facade.create_tag(
        schemas.TagCreate(name='A second tag', parent_id=None)
    )


@pytest.fixture
def parent_tag_1(db_session):
    return facade.create_tag(
        schemas.TagCreate(name='Parent tag 1', parent_id=None)
    )


@pytest.fixture
def child_tag_1_of_parent_tag_1(db_session, parent_tag_1):
    return facade.create_tag(
        schemas.TagCreate(
            name='Child 1 of Parent tag 1', parent_id=parent_tag_1.id
        )
    )


@pytest.fixture
def child_tag_2_of_parent_tag_1(db_session, parent_tag_1):
    return facade.create_tag(
        schemas.TagCreate(
            name='Child 2 of Parent tag 1', parent_id=parent_tag_1.id
        )
    )
