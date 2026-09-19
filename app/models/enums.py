import enum

from sqlalchemy import Enum


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    PROVIDER = "provider"
    ADMIN = "admin"


def sql_enum(enum_class: type[enum.Enum], name: str) -> Enum:
    return Enum(enum_class, name=name, values_callable=lambda values: [item.value for item in values])
