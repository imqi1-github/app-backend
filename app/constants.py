from enum import Enum


class UserRole(Enum):
    Admin = "admin"
    User = "user"


class FileType(Enum):
    Image = "image"


class UserStatus(Enum):
    Active = "active"
    Banned = "banned"