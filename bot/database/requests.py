from datetime import datetime, timedelta
import logging
from typing import Dict, Iterable

from bot.database import User, AnonymousMessage

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


def set_user(
    user_id: int,
    first_name: str,
    username: str | None,
    second_name: str | None,
    is_sub: bool = False,
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


def get_user(user_id: int) -> User:
    return User.get(User.user_id == user_id)


def get_users() -> Dict[str, Iterable[User]]:
    response = {
        "users": User.select(),
        "usernames": User.select().where(User.username.is_null(False)),
        "names": User.select().where(User.first_name.is_null(False)),
        "surnames": User.select().where(User.second_name.is_null(False)),
        "ids": User.select().where(User.user_id.is_null(False)),
    }
    return response


def set_anonymous_message(
    sender_id: int,
    receiver_id: int,
    receiver_message_id: int | None,
) -> AnonymousMessage:
    anonymous_message = AnonymousMessage.get_or_none(
        receiver_message_id=receiver_message_id
    )

    if anonymous_message is None:
        anonymous_message = AnonymousMessage.create(
            sender=sender_id,
            receiver=receiver_id,
            receiver_message_id=receiver_message_id,
        )
    return anonymous_message


def get_anonymous_message(
    anonymous_message_id: int,
) -> AnonymousMessage | None:
    return AnonymousMessage.get_or_none(AnonymousMessage.id == anonymous_message_id)


def close_anonymous_message(
    anonymous_message_id: int,
) -> None:
    (
        AnonymousMessage.update(
            is_active=False,
            replied_at=datetime.now(),
        )
        .where(AnonymousMessage.id == anonymous_message_id)
        .execute()
    )


def delete_old_anonymous_messages(
    days: int = 30,
) -> int:
    deadline = datetime.now() - timedelta(days=days)

    return (
        AnonymousMessage.delete()
        .where(AnonymousMessage.created_at < deadline)
        .execute()
    )


def delete_closed_anonymous_messages(
    days: int = 3,
) -> int:
    deadline = datetime.now() - timedelta(days=days)

    return (
        AnonymousMessage.delete()
        .where(
            (AnonymousMessage.is_active == False)
            & (AnonymousMessage.replied_at < deadline)
        )
        .execute()
    )
