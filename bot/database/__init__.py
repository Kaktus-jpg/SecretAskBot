from bot.database.models import AnonymousMessage, Payment, User, create_tables
from bot.database.requests import (
    close_anonymous_message,
    delete_closed_anonymous_messages,
    delete_old_anonymous_messages,
    get_anonymous_message,
    get_last_paid_payment,
    get_payment,
    get_user,
    set_anonymous_message,
    set_payment,
    set_user,
)
