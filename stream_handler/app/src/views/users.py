import datetime as dt
from http import HTTPStatus
from typing import Any

import faust
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from pydantic import ValidationError

from ..core.types import OperationType, UserBlockingRecord
from ..core.utils import get_serializer_errors
from ..dependencies import AppDependencies
from ..schemas import BlockUserSerializer


def users_view(app: faust.App, dependencies: AppDependencies) -> None:
    """
    Регистрация представления для управления пользователями.
    """

    @app.page("/block_user/")
    class BlockUserView(faust.web.View):
        async def post(self, request: Request) -> Response:
            """
            Блокировка пользователя по идентификатору.
            """
            data: dict[str, Any] = await request.json()
            try:
                serializer = BlockUserSerializer(**data)
            except ValidationError as e:
                return self.json(
                    {"errors": get_serializer_errors(e)}, status=HTTPStatus.BAD_REQUEST
                )
            await dependencies.topics.blocked_users.send(
                key=str(serializer.user_id),
                value=UserBlockingRecord(
                    user_id=str(serializer.user_id),
                    blocked_id=str(serializer.blocked_id),
                    date_blocked=dt.datetime.now(dt.timezone.utc).isoformat(),
                    comment=serializer.comment,
                    operation_type=serializer.operation_type,
                ),
            )
            operation = (
                "block" if serializer.operation_type == OperationType.ADD else "unblock"
            )
            dependencies.logger.info(
                "User %s tried to %s user %s by API.",
                serializer.user_id,
                operation,
                serializer.blocked_id,
            )
            return self.json("accepted", status=HTTPStatus.ACCEPTED)

    @app.page("/users/")
    class UsersListView(faust.web.View):
        async def get(self, request: Request) -> Response:
            """
            Получение списка всех пользователей с блокировками.
            """
            return self.json(
                dict(dependencies.tables.blocked_users.items()), status=HTTPStatus.OK
            )

    @app.page("/users/{user_id}/")
    class UserDetailView(faust.web.View):
        async def get(self, request: Request, user_id: str) -> Response:
            """
            Получение информации о блокировках конкретного пользователя.
            """
            if user_id not in dependencies.tables.blocked_users.keys():
                return self.json(
                    {"error": "user not found"}, status=HTTPStatus.NOT_FOUND
                )
            blocked_users: dict = dependencies.tables.blocked_users.get(user_id)
            return self.json(
                {
                    "user_id": user_id,
                    "blocked_users": blocked_users,
                    "total_blocked": len(blocked_users or {}),
                },
                status=HTTPStatus.OK,
            )
