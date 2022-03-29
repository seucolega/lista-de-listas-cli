import pytest
import schemas
from pydantic.error_wrappers import ValidationError


def test_item_create__with_empty_name():
    with pytest.raises(ValidationError, match='Name cannot be empty.'):
        schemas.ItemCreate(name='')


def test_tag_create__with_empty_name():
    with pytest.raises(ValidationError, match='Name cannot be empty.'):
        schemas.TagCreate(name='')
