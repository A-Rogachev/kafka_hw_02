import logging
from functools import partial
from typing import AsyncGenerator, Final

import faust

from .core.types import (
    BannedWord,
    Message,
    OperationType,
    UserBlockingRecord,
)
from .dependencies import AppDependencies
from .services.censorship import censor_text

INTERVAL_TO_GET_BANNED_WORDS_SEC: Final[int] = 3
AMOUNT_OF_BANNED_WORDS_TO_GET: Final[int] = 100


async def banned_word_log(word: BannedWord, logger: logging.Logger) -> None:
    """
    Запись в лог информации о добавлении или удалении запрещенного слова.

    :param word: BannedWord, информация о запрещенном слове

    :return: None
    """
    if word.operation_type == OperationType.ADD:
        logger.success("user added word to blacklist: %s", word.word)
    elif word.operation_type == OperationType.REMOVE:
        logger.success("user removed word from blacklist: %s", word.word)


def app_agents(app: faust.App, dependencies: AppDependencies) -> None:
    """
    Регистрация агентов в приложении.
    """

    @app.agent(
        channel=dependencies.topics.banned_words,
        sink=[partial(banned_word_log, logger=dependencies.logger)],
    )
    async def update_banned_words(
        words: faust.Stream[BannedWord],
    ) -> AsyncGenerator[BannedWord, None]:
        """
        Агент для обновления списка запрещенных слов.
        """
        async for _word in words:
            current: set = dependencies.tables.banned_words.setdefault("global", set())
            _operation_type, _value = _word.operation_type, _word.word
            if _operation_type == OperationType.ADD and _value not in current:
                current.add(_value)
                yield _word
            elif _operation_type == OperationType.REMOVE and _value in current:
                current.discard(_value)
                yield _word

    @app.agent(dependencies.topics.messages_raw)
    async def censor_agent(messages: faust.Stream[Message]) -> None:
        """
        Агент для цензуры сообщений.
        """
        async for msg in messages:
            censored = censor_text(
                msg.text, dependencies.tables.banned_words.get("global", set())
            )
            if censored != msg.text:
                msg.text = censored
                dependencies.logger.warning(
                    "Message from user %s to user %s was censored.",
                    msg.sender_id,
                    msg.recipient_id,
                )
            await dependencies.topics.messages_filtered.send(value=msg)

    @app.agent(dependencies.topics.messages_filtered)
    async def store_filtered_messages(messages: faust.Stream[Message]) -> None:
        """
        Агент для сохранения отфильтрованных сообщений в таблицу.
        """
        async for msg in messages:
            current: list = dependencies.tables.messages_filtered.setdefault(
                msg.recipient_id, []
            )
            current.append(msg)
            dependencies.tables.messages_filtered[msg.recipient_id] = current

    @app.agent(dependencies.topics.blocked_users)
    async def process_users_blocking(
        messages: faust.Stream[UserBlockingRecord],
    ) -> None:
        """
        Блокировка и разблокировка пользователей.
        """
        async for msg in messages:
            user_id = msg.user_id
            current: dict = dependencies.tables.blocked_users.setdefault(user_id, {})

            if msg.operation_type == OperationType.REMOVE:  # разблокировка
                if msg.blocked_id in current:
                    del current[msg.blocked_id]
                    dependencies.tables.blocked_users[user_id] = current
                    dependencies.logger.success(
                        "User %s unblocked user %s.", user_id, msg.blocked_id
                    )
            else:  # OperationType.ADD - блокировка
                current[msg.blocked_id] = {
                    "blocking_date": msg.date_blocked,
                    "comment": msg.comment,
                }
                dependencies.tables.blocked_users[user_id] = current
                dependencies.logger.success(
                    "User %s blocked user %s.", user_id, msg.blocked_id
                )
