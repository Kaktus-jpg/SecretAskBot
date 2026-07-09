import logging
from typing import Dict, Iterable

from bot.database import User

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def set_user(
    user_id: int,
    first_name: str,
    username: str | None,
    second_name: str | None,
    is_sub: bool | None = None,
) -> None:
    user = User.get_or_none(User.user_id == user_id)

    if not user:
        user = User.create(
            user_id=user_id,
            first_name=first_name,
            second_name=second_name,
            username=username,
            is_sub=is_sub,
        )
        user.save()


async def get_user(user_id: int) -> User:
    return User.get(User.user_id == user_id)


async def get_users() -> Dict[str, Iterable[User]]:
    response = {
        "users": User.select(),
        "usernames": User.select().where(User.username.is_null(False)),
        "names": User.select().where(User.first_name.is_null(False)),
        "surnames": User.select().where(User.second_name.is_null(False)),
        "ids": User.select().where(User.user_id.is_null(False)),
    }
    return response
