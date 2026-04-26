from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData

from database import db
from states import NoteState

router = Router()

# Структура данных для callback кнопок
class NoteAction(CallbackData, prefix="note"):
    action: str
    note_id: int

@router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "Привет! Я твой личный менеджер заметок.\n\n"
        "Доступные команды:\n"
        "/add — Создать новую заметку\n"
        "/list — Посмотреть мои заметки"
    )
    await message.answer(text)

@router.message(F.text == "/add")
async def add_note_start(message: Message, state: FSMContext):
    await message.answer("Введите текст вашей новой заметки:")
    await state.set_state(NoteState.add_text)

@router.message(NoteState.add_text)
async def add_note_save(message: Message, state: FSMContext):
    await db.add_note(message.from_user.id, message.text)
    await message.answer("Заметка успешно сохранена! Посмотреть: /list")
    await state.clear()

@router.message(F.text == "/list")
async def list_notes(message: Message):
    notes = await db.get_notes(message.from_user.id)
    if not notes:
        await message.answer("У вас пока нет заметок. Создайте первую: /add")
        return
    
    await message.answer("Ваши заметки:")
    for note in notes:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Изменить", callback_data=NoteAction(action="edit", note_id=note['id']).pack()),
                InlineKeyboardButton(text="Удалить", callback_data=NoteAction(action="delete", note_id=note['id']).pack())
            ]
        ])
        await message.answer(f"Текст заметки: {note['text']}", reply_markup=keyboard)

@router.callback_query(NoteAction.filter(F.action == "delete"))
async def delete_note_handler(query: CallbackQuery, callback_data: NoteAction):
    await db.delete_note(callback_data.note_id, query.from_user.id)
    await query.message.delete()
    await query.answer("Заметка удалена", show_alert=False)

@router.callback_query(NoteAction.filter(F.action == "edit"))
async def edit_note_start(query: CallbackQuery, callback_data: NoteAction, state: FSMContext):
    await state.update_data(note_id=callback_data.note_id)
    await query.message.answer("Введите новый текст для этой заметки:")
    await state.set_state(NoteState.edit_text)
    await query.answer()

@router.message(NoteState.edit_text)
async def edit_note_save(message: Message, state: FSMContext):
    data = await state.get_data()
    note_id = data.get("note_id")
    
    await db.update_note(note_id, message.from_user.id, message.text)
    await message.answer("Заметка успешно обновлена! Посмотреть: /list")
    await state.clear()