import faust

from .core.const import DAY_SECONDS, DEFAULT_BANNED_WORDS
from .core.types import AppTables


def create_tables(faust_app: faust.App) -> AppTables:
    """
    Функция для создания таблиц приложения.

    :param faust_app: faust.App, экземпляр Faust приложения

    :return: AppTables, таблицы приложения
    """
    return AppTables(
        banned_words=faust_app.Table(
            name="banned_words",
            default=lambda: DEFAULT_BANNED_WORDS,
            help="Запрещенные слова",
            partitions=3,
        ),
        blocked_users=faust_app.Table(
            name="blocked_users",
            default=dict,
            help="Заблокированные пользователи",
            partitions=3,
        ),
        messages_filtered=faust_app.Table(
            name="messages_filtered",
            default=list,
            help="Фильтрованные сообщения",
            partitions=3,
        ).tumbling(
            size=DAY_SECONDS,
            expires=DAY_SECONDS,
        ),
    )
