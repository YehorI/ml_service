from typing import Iterable, Protocol


class MigrationsInterface(Protocol):
    def get_migrations(self) -> Iterable[str]:
        raise NotImplementedError

    def get_current_migration(self) -> str:
        raise NotImplementedError

    def create_migration(
            self,
            migration_id: str | None = None,
            **kwargs,
    ) -> str:
        raise NotImplementedError

    def migrate(self, migration_id: str | None = None) -> str:
        raise NotImplementedError

    def rollback(self, migration_id: str | None = None) -> str:
        raise NotImplementedError

    def squash_migrations(self, new_migration_id: str | None = None, **kwargs) -> str:
        raise NotImplementedError
