from aiogram.fsm.state import State, StatesGroup

class NoteState(StatesGroup):
    add_text = State()
    edit_text = State()