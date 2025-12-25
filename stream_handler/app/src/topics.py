import faust

from .core.types import AppTopics, BannedWord, Message, UserBlockingRecord


def register_topics(faust_app: faust.App) -> AppTopics:
    """
    Регистрация топиков кафки для приложения.

    :param faust_app: faust.App, экземпляр Faust приложения

    :return: AppTopics, топики кафки
    """
    return AppTopics(
        messages_raw=faust_app.topic(
            "messages",
            key_type=int,
            value_type=Message,
            partitions=3,
        ),
        messages_filtered=faust_app.topic(
            "filtered_messages",
            key_type=int,
            value_type=Message,
            partitions=3,
        ),
        blocked_users=faust_app.topic(
            "blocked_users",
            key_type=int,
            value_type=UserBlockingRecord,
            partitions=3,
        ),
        banned_words=faust_app.topic(
            "banned_words",
            key_type=str,
            value_type=BannedWord,
            partitions=3,
        ),
    )
