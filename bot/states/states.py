from aiogram.fsm.state import StatesGroup, State


class SenderStates(StatesGroup):
    wait_for_send_message = State()


class ReceiverStates(StatesGroup):
    wait_for_answer_message = State()


class StopSub(StatesGroup):
    get_stop_message = State()
