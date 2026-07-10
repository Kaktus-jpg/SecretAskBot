from aiogram.filters.callback_data import CallbackData


class AnonymousReplyCallback(CallbackData, prefix="anon_reply"):
    anonymous_message_id: int


class RevealSenderCallback(CallbackData, prefix="anon_reveal"):
    anonymous_message_id: int


class ToggleAdminCallback(CallbackData, prefix="anon_admin"):
    anonymous_message_id: int
