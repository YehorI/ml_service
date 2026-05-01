from typing import AsyncIterable, Protocol, TypeVar

from ml_service_common.interfaces.transaction import TransactionInterface

FixtureItemType = TypeVar("FixtureItemType")  # pylint: disable=invalid-name


class FixturesInterface(TransactionInterface, Protocol[FixtureItemType]):
    async def apply_fixture(self, fixture_id: str):
        fixture_loader = await self.get_fixture_loader(fixture_id=fixture_id)
        if fixture_loader is None:
            raise ValueError(f"Cannot get fixture loader for fixture '{fixture_id}'")

        async with self.transaction():
            async for item in fixture_loader:
                await self.apply_fixture_item(fixture_id=fixture_id, item=item)

    async def get_fixtures(self) -> AsyncIterable[str]:
        raise NotImplementedError

    async def get_fixture_loader(
            self,
            fixture_id: str,
    ) -> AsyncIterable[FixtureItemType] | None:
        raise NotImplementedError

    async def apply_fixture_item(self, fixture_id: str, item: FixtureItemType):
        raise NotImplementedError
