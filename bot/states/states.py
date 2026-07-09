from aiogram.fsm.state import StatesGroup, State


class SenderStates(StatesGroup):
    wait_for_send_message = State()
