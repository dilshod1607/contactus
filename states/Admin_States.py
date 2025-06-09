from aiogram.dispatcher.filters.state import State, StatesGroup


class SendMessage(StatesGroup):
    text = State()


class RefState(StatesGroup):
    waiting_for_user_id = State()