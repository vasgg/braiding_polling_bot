import contextlib
import logging

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bot.internal.helpers import number_to_nomination, voting_available
from bot.internal.lexicon import texts
from bot.internal.states import VotingStates
from bot.keyboards.callbacks import (
    BackToNominationsCallback,
    NominationCallback,
    SubmitVoteCallback,
    ToggleNomineeCallback,
)
from bot.keyboards.markups import contact_kb, nominations_kb, nominee_checkbox_kb
from database.crud.nominee import get_nominees
from database.models import Nominee, User, Vote

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def start_message(message: types.Message, user: User, state: FSMContext) -> None:
    data = await state.get_data()
    if data.get('msg_id'):
        with contextlib.suppress(TelegramBadRequest):
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data['msg_id'])
    await state.clear()
    if not user.phone_number:
        await message.answer(text=texts['start_message'])
        await message.answer(text=texts['without_number_message'], reply_markup=contact_kb())
        return
    await message.answer(text=texts['start_message'])
    if voting_available(user):
        msg = await message.answer(text=texts['nomination_message'], reply_markup=nominations_kb(user))
        await state.update_data(msg_id=msg.message_id)
    else:
        await message.answer(text=texts['no_more_nominations_message'])


@router.message(F.contact)
async def handle_contact(message: types.Message, user: User, state: FSMContext) -> None:
    if user.phone_number or not message.contact:
        return
    user.phone_number = message.contact.phone_number
    await message.answer(text=texts['phone_number_accepted_message'], reply_markup=types.ReplyKeyboardRemove())
    if voting_available(user):
        msg = await message.answer(text=texts['nomination_message'], reply_markup=nominations_kb(user))
        await state.update_data(msg_id=msg.message_id)


@router.callback_query(NominationCallback.filter())
async def handle_nomination(
    callback: types.CallbackQuery,
    callback_data: NominationCallback,
    user: User,
    db_session: AsyncSession,
    state: FSMContext,
) -> None:
    if getattr(user, f'voted_{callback_data.nomination.value}'):
        await callback.answer('Вы уже проголосовали в этой номинации', show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=nominations_kb(user))
        return

    await callback.answer()
    nominees: list[Nominee] = await get_nominees(callback_data.nomination, db_session)
    nomination_name = number_to_nomination(callback_data.nomination.value)
    await state.update_data(nomination=callback_data.nomination.value, selected_ids=[])
    await state.set_state(VotingStates.selecting_nominees)
    await callback.message.edit_text(
        texts['select_three_prompt'].format(nomination_name),
        reply_markup=nominee_checkbox_kb(nominees, callback_data.nomination, []),
    )


@router.callback_query(BackToNominationsCallback.filter())
async def handle_back_to_nominations(
    callback: types.CallbackQuery,
    user: User,
    state: FSMContext,
) -> None:
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(
        text=texts['nomination_message'],
        reply_markup=nominations_kb(user),
    )


@router.callback_query(VotingStates.selecting_nominees, ToggleNomineeCallback.filter())
async def handle_toggle_nominee(
    callback: types.CallbackQuery,
    callback_data: ToggleNomineeCallback,
    db_session: AsyncSession,
    state: FSMContext,
) -> None:
    nominees: list[Nominee] = await get_nominees(callback_data.nomination, db_session)
    valid_ids = {n.id for n in nominees}
    if callback_data.nominee_id not in valid_ids:
        await callback.answer('Некорректный выбор', show_alert=True)
        return

    data = await state.get_data()
    selected_ids: list[int] = data.get('selected_ids', [])
    nominee_id = callback_data.nominee_id

    if nominee_id in selected_ids:
        selected_ids.remove(nominee_id)
    elif len(selected_ids) < 3:
        selected_ids.append(nominee_id)
    else:
        selected_ids.pop(0)
        selected_ids.append(nominee_id)

    await state.update_data(selected_ids=selected_ids)
    await callback.message.edit_reply_markup(
        reply_markup=nominee_checkbox_kb(nominees, callback_data.nomination, selected_ids),
    )
    await callback.answer()


@router.callback_query(VotingStates.selecting_nominees, SubmitVoteCallback.filter())
async def handle_submit_vote(
    callback: types.CallbackQuery,
    callback_data: SubmitVoteCallback,
    user: User,
    db_session: AsyncSession,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    selected_ids: list[int] = data.get('selected_ids', [])

    if len(selected_ids) != 3:
        await callback.answer('Нужно выбрать ровно 3 номинанта', show_alert=True)
        return

    vote_field = f'voted_{callback_data.nomination.value}'
    if getattr(user, vote_field):
        await callback.answer('Голос уже засчитан', show_alert=True)
        await state.clear()
        await callback.message.edit_text(text=texts['nomination_message'], reply_markup=nominations_kb(user))
        return

    nominees = await get_nominees(callback_data.nomination, db_session)
    valid_ids = {n.id for n in nominees}
    if not set(selected_ids).issubset(valid_ids):
        await callback.answer('Некорректный выбор', show_alert=True)
        return

    vote = Vote(
        user_id=user.id,
        nomination=callback_data.nomination,
        vote_for_1=selected_ids[0],
        vote_for_2=selected_ids[1],
        vote_for_3=selected_ids[2],
    )
    try:
        async with db_session.begin_nested():
            db_session.add(vote)
            setattr(user, vote_field, True)
            await db_session.flush()
    except IntegrityError:
        setattr(user, vote_field, False)
        await callback.answer('Голос уже засчитан', show_alert=True)
        await state.clear()
        return

    logger.info(
        'Vote saved: user_id=%s nomination=%s nominees=%s',
        user.id,
        callback_data.nomination.value,
        selected_ids,
    )
    await state.clear()

    if voting_available(user):
        await callback.answer(texts['vote_accepted_message'], show_alert=True)
        msg = await callback.message.edit_text(
            text=texts['nomination_message'],
            reply_markup=nominations_kb(user),
        )
        await state.update_data(msg_id=msg.message_id)
    else:
        await callback.answer(texts['last_vote_accepted_message'], show_alert=True)
        await callback.message.edit_text(texts['no_more_nominations_message'])
