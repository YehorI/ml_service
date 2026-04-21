import json
import pathlib
from typing import AsyncIterable, Iterable

import yaml

from .models import FixtureItem


def _convert_content_to_item_generator(content: Iterable[dict]) -> Iterable[FixtureItem]:
    for fixture_item_content in content:
        fixture_item = FixtureItem(**fixture_item_content)
        yield fixture_item


async def yaml_fixture_loader(fixture_path: pathlib.Path) -> AsyncIterable[FixtureItem]:
    with open(fixture_path, "rt", encoding="utf-8") as fixture_file:
        fixture_content_loader = yaml.safe_load_all(fixture_file)
        fixture_item_generator = _convert_content_to_item_generator(content=fixture_content_loader)
        for fixture_item in fixture_item_generator:
            yield fixture_item


async def json_fixture_loader(fixture_path: pathlib.Path) -> AsyncIterable[FixtureItem]:
    with open(fixture_path, "rt", encoding="utf-8") as fixture_file:
        fixture_content = json.load(fixture_file)

    if isinstance(fixture_content, dict):
        fixture_content = [fixture_content]

    fixture_item_generator = _convert_content_to_item_generator(content=fixture_content)
    for fixture_item in fixture_item_generator:
        yield fixture_item
