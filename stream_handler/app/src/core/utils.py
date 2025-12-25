from pydantic import ValidationError as PydanticError

from .types import SerializationError


def get_serializer_errors(e: PydanticError) -> list[SerializationError]:
    """
    Функция для унификации ошибок веб-представлений приложения.
    """
    return [
        {
            "type": err["type"],
            "loc": err.get("loc", ()),
            "msg": err["msg"],
            "input": err.get("input"),
        }
        for err in e.errors()
    ]
