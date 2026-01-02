import datetime as dt
from http import HTTPStatus
from typing import Any

import faust
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from pydantic import ValidationError

from ..core.types import Message
from ..core.utils import get_serializer_errors
from ..dependencies import AppDependencies
from ..schemas import MessageSerializer


def messages_view(app: faust.App, dependencies: AppDependencies) -> None:
    """
    Регистрация представления для управления сообщениями пользователей.
    """

    @app.page("/messages/")
    class MessagesView(faust.web.View):
        async def post(self, request: Request) -> Response:
            """
            Блокировка пользователя по идентификатору.
            """
            data: dict[str, Any] = await request.json()
            try:
                serializer = MessageSerializer(**data)
            except ValidationError as e:
                return self.json(
                    {"errors": get_serializer_errors(e)}, status=HTTPStatus.BAD_REQUEST
                )
            if str(serializer.sender_id) in dependencies.tables.blocked_users.get(
                str(serializer.recipient_id), set()
            ):
                return self.json(
                    {"error": "you were blocked by this user"},
                    status=HTTPStatus.FORBIDDEN,
                )
            await dependencies.topics.messages_raw.send(
                key=str(serializer.recipient_id),
                value=Message(
                    sender_id=str(serializer.sender_id),
                    recipient_id=str(serializer.recipient_id),
                    text=serializer.text,
                    timestamp=dt.datetime.now(dt.timezone.utc).timestamp(),
                ),
            )
            dependencies.logger.info(
                "Message from user %s to user %s sent by API.",
                serializer.sender_id,
                serializer.recipient_id,
            )
            return self.json("accepted", status=HTTPStatus.ACCEPTED)

        async def get(self, request: Request) -> Response:
            """
            Получение списка всех сообщений.
            """
            user_id: str = request.match_info.get("user_id", "")
            limit = min(int(request.query.get("limit", 50)), 100)
            offset = int(request.query.get("offset", 0))
            if not (user_id := request.query.get("user_id", "")):
                return self.json(
                    {"error": "user_id query parameter is required"},
                    status=HTTPStatus.BAD_REQUEST,
                )
            return self.json(
                {
                    "user_id": user_id,
                    "messages": [
                        msg
                        for msg in dependencies.tables.messages_filtered.get(
                            user_id, []
                        ).now()[offset : offset + limit]
                    ],
                },
                status=HTTPStatus.OK,
            )
