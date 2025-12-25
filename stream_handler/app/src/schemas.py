from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator

from .core.const import (
    BLOCK_USER_COMMENT_MAX_LENGTH,
    USER_MESSAGE_MAX_LENGTH,
)
from .core.types import OperationType


class BlockUserSerializer(BaseModel):
    """
    Сериализатор для блокировки пользователя.
    """

    user_id: int
    blocked_id: int
    operation_type: OperationType
    comment: str | None = Field(
        max_length=BLOCK_USER_COMMENT_MAX_LENGTH,
        description="Комментарий с причиной блокировки пользователя.",
    )

    @model_validator(mode="after")
    def check_user_ids(self) -> Self:
        """
        Проверка на самоблокировку пользователя.
        """
        if self.user_id == self.blocked_id:
            raise ValueError("Users cannot block or unblock themselves.")
        return self


class BannedWordsSerializer(BaseModel):
    """
    Сериализатор для списка запрещенных слов.
    """

    words: list[str] = Field(..., min_length=1, max_length=50)
    operation_type: OperationType

    @field_validator("words")
    @classmethod
    def validate_words(cls, v) -> list[str]:
        """
        Валидация списка запрещенных слов.
        """
        if not all(isinstance(word, str) and word.strip() for word in v):
            raise ValueError("All words must be non-empty strings")
        return [word.strip().lower() for word in v]


class MessageSerializer(BaseModel):
    """
    Сериализатор для сообщения.
    """

    sender_id: int
    recipient_id: int
    text: str = Field(
        max_length=USER_MESSAGE_MAX_LENGTH, description="Сообщение пользователя."
    )
