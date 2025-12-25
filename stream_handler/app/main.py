import random
from collections.abc import Sequence
from typing import Callable, TypeAlias

import faust
from faker import Faker

from .src.agents import app_agents
from .src.core.config import settings
from .src.core.const import (
    BADWORD,
    FORBIDDENWORD,
    MAX_MOCK_USER_ID,
    MIN_MOCK_USER_ID,
    MOCK_MESSAGES_TIMEOUT,
)
from .src.core.logger import setup_logger
from .src.core.types import Message
from .src.dependencies import DEPENDENCIES, AppDependencies
from .src.tables import create_tables
from .src.topics import register_topics
from .src.views.banned_words import banned_words_view
from .src.views.messages import messages_view
from .src.views.users import users_view

RegisterMethod: TypeAlias = Sequence[Callable[[faust.App, AppDependencies], None]]


def register_views(
    app_object: faust.App,
    app_dependenies: AppDependencies,
    views_decorators: RegisterMethod,
) -> None:
    """
    Регистрация представления в приложении.

    :param app_object: faust.App, экземпляр приложения
    :param app_dependencies: AppDependencies, зависимости для функционирования приложения
    :views_decorators: views_decorators: RegisterMethod, список функций регистрации
        представлений для приложения

    :return: None
    """
    for register_view in views_decorators:
        register_view(app_object, app_dependenies)


register_agents = register_views

app = faust.App(
    settings.app_name,
    broker=settings.broker_address,
    store=settings.data_store,
    value_serializer="raw",
)

DEPENDENCIES.tables = create_tables(app)
DEPENDENCIES.topics = register_topics(app)
DEPENDENCIES.logger = setup_logger(name=settings.logger_name)

register_views(app, DEPENDENCIES, [users_view, banned_words_view, messages_view])
register_agents(app, DEPENDENCIES, [app_agents])

fake = Faker()


@app.timer(interval=MOCK_MESSAGES_TIMEOUT)
async def periodic_message_sender() -> None:
    """
    Периодически отправляет рандомные сообщения в топик сырых сообщений.
    """
    sender_id: str = str(random.randint(MIN_MOCK_USER_ID, MAX_MOCK_USER_ID))
    recipient_id: str = str(random.randint(MIN_MOCK_USER_ID, MAX_MOCK_USER_ID))
    if sender_id == recipient_id:
        return
    text: str = random.choice(
        (
            fake.sentence(),
            fake.text(max_nb_chars=50),
            fake.catch_phrase(),
            f"{fake.word()} is a {BADWORD}",
            f"{fake.word()} is a {FORBIDDENWORD}",
        )
    )
    if DEPENDENCIES.tables.blocked_users.get(recipient_id):
        if sender_id in DEPENDENCIES.tables.blocked_users.get(recipient_id, set()):
            DEPENDENCIES.logger.error(
                "Message from user %s to user %s was not sent because the sender is blocked.",
                sender_id,
                recipient_id,
            )
    await DEPENDENCIES.topics.messages_raw.send(
        key=recipient_id,
        value=Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            text=text,
            timestamp=int(fake.unix_time()),
        ),
    )


if __name__ == "__main__":
    app.main()
