from dataclasses import dataclass
from enum import StrEnum
from typing import Any, TypedDict

import faust


class OperationType(StrEnum):
    """
    Тип операции со словами.
    """

    ADD = "add"
    REMOVE = "remove"


class SerializationError(TypedDict):
    """
    Ошибка сериализации запроса.

    NOTE:
    - type, тип ошибки
    - loc, поля сериализатора с ошибками
    - msg, сообщение об ошибке для инициатора запроса
    - input, введенные пользователем данные, которые привели к ошибке сериализации
    """

    type: str
    loc: list[str]
    msg: str
    input: Any


class Message(faust.Record, serializer="json"):
    sender_id: str
    recipient_id: str
    text: str
    timestamp: int


class UserBlockingRecord(faust.Record, serializer="json"):
    user_id: str
    blocked_id: str
    date_blocked: str  # NOTE: UTC ISO format
    operation_type: OperationType
    comment: str | None = None


class BannedWord(faust.Record, serializer="json"):
    word: str
    operation_type: OperationType


@dataclass
class AppTables:
    """
    Класс для хранения таблиц приложения.
    """

    banned_words: faust.Table
    blocked_users: faust.Table
    messages_filtered: faust.Table


@dataclass(slots=True)
class AppTopics:
    """
    Класс для хранения таблиц приложения.
    """

    messages_raw: faust.Topic
    messages_filtered: faust.Topic
    blocked_users: faust.Topic
    banned_words: faust.Topic
