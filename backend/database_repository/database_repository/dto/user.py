from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class UserRoleDTO(Enum):
    USER = "user"
    ADMIN = "admin"


@dataclass
class UserCreateDTO:
    username: str
    email: str
    password_hash: str
    role: UserRoleDTO = field(default=UserRoleDTO.USER)


@dataclass
class UserReadDTO:
    id: int
    username: str
    email: str
    password_hash: str
    role: UserRoleDTO
    created_at: datetime
