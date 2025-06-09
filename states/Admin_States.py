from aiogram.dispatcher.filters.state import State, StatesGroup


class SendMessage(StatesGroup):
    text = State()
