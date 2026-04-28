import os
import pathlib
from typing import Self

import pydantic_settings
from ml_service_common.interfaces.settings import SettingsInterface
from ml_service_common.pydantic_dto import PydanticDTO


class PydanticSettings(PydanticDTO, SettingsInterface):
    @classmethod
    def load(
            cls,
            env_file: str | pathlib.Path | None = None,
            env_prefix: str | None = None,
            env_nested_delimiter: str | None = "__",
            secrets_dir: str | pathlib.Path = pathlib.Path("/run/secrets"),
    ) -> Self:
        cls._move_values_from_secrets_to_environ(secrets_dir=pathlib.Path(secrets_dir))
        settings_class = cls._generate_pydantic_settings_class(
            env_nested_delimiter=env_nested_delimiter,
            env_file=None if env_file is None else str(env_file),
            env_prefix=env_prefix,
            secrets_dir=str(secrets_dir),
        )

        return settings_class

    @staticmethod
    def _move_values_from_secrets_to_environ(secrets_dir: pathlib.Path):
        """Workaround for loading values from secrets."""

        secrets_dir = pathlib.Path(secrets_dir)
        if not secrets_dir.is_dir():
            return

        for secret_file in secrets_dir.iterdir():
            if not secret_file.is_file():
                continue

            secret_file_content = secret_file.read_text()
            os.environ[secret_file.name] = secret_file_content.strip()

    @classmethod
    def _generate_pydantic_settings_class(
            cls,
            env_file: str | None,
            env_prefix: str | None,
            env_nested_delimiter: str | None,
            secrets_dir: str | None,
    ) -> Self:
        class_name = cls.__name__
        base_classes = (cls, pydantic_settings.BaseSettings)
        config_dict = pydantic_settings.SettingsConfigDict(
            env_nested_delimiter=env_nested_delimiter,
            env_file=env_file,
            env_prefix=env_prefix or "",
            extra="ignore",
            secrets_dir=secrets_dir,
        )
        attributes = {"model_config": config_dict}

        settings_class = type(class_name, base_classes, attributes)

        return settings_class()
