import logging
from dataclasses import dataclass

import faust

from .core.types import AppTables, AppTopics


@dataclass(slots=True)
class AppDependencies:
    """
    Объекты, необходимые для работы приложения.
    """

    app: faust.App | None = None
    tables: AppTables | None = None
    topics: AppTopics | None = None
    logger: logging.Logger | None = None


DEPENDENCIES = AppDependencies()
