from aiogram.fsm.state import State, StatesGroup


class VotingStates(StatesGroup):
    selecting_nominees = State()
