from http import HTTPStatus

import faust
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from pydantic import ValidationError

from ..core.utils import get_serializer_errors
from ..dependencies import AppDependencies
from ..schemas import BannedWordsSerializer


def banned_words_view(app: faust.App, dependencies: AppDependencies) -> None:
    """
    Регистрация представления для управления списком запрещенных слов.
    """

    @app.page("/banned_words/")
    class BannedWordsView(faust.web.View):
        """
        Представление для взаимодействия со списком запрещенных слов.
        """

        async def post(self, request: Request) -> Response:
            """
            Добавление слова в список запрещенных слов.
            """
            data = await request.json()
            try:
                serializer = BannedWordsSerializer(**data)
            except ValidationError as e:
                return self.json(
                    {"errors": get_serializer_errors(e)}, status=HTTPStatus.BAD_REQUEST
                )
            for word in {word.strip().lower() for word in serializer.words}:
                await dependencies.topics.banned_words.send(
                    key=word,
                    value={"word": word, "operation_type": serializer.operation_type},
                )
            dependencies.logger.info(
                "User trying to update banned words by API: %s %s",
                serializer.operation_type,
                serializer.words,
            )
            return self.json("accepted", status=HTTPStatus.ACCEPTED)

        async def get(self, request: Request) -> Response:
            """
            Получение списка запрещенных слов.
            """
            words: set[str] = dependencies.tables.banned_words.get("global", set())
            return self.json(set(words), status=HTTPStatus.OK)
