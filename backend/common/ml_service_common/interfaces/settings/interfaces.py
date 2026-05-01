import pathlib

from ml_service_common.interfaces.dto import DTOInterface


class SettingsInterface(DTOInterface):
    @classmethod
    def load(
            cls,
            env_file: str | pathlib.Path | None = None,
            env_prefix: str | None = None,
            env_nested_delimiter: str | None = "__",
            secrets_dir: str | pathlib.Path = pathlib.Path("/run/secrets"),
    ) -> "SettingsInterface":
        raise NotImplementedError
