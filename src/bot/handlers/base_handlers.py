from asyncio import Queue, sleep
import contextlib

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.internal.enums import Action, TaskType
from bot.internal.helpers import get_nominees_list, number_to_nomination, voting_available
from bot.internal.schemas import TaskModel, VoteTask
from bot.keyboards.callbacks import NominationCallback, NomineeCallback, VoteConfirmationCallback
from bot.keyboards.markups import contact_kb, nominations_kb, nominee_kb, vote_confirmation_kb
from bot.internal.lexicon import texts
from database.crud.nominee import get_nominee, get_nominees
from database.models import Nominee, User, Vote

router = Router()


@router.message(CommandStart())
async def start_message(message: types.Message, user: User, state: FSMContext) -> None:
    data = await state.get_data()
    if data.get('msg_id'):
        with contextlib.suppress(TelegramBadRequest):
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data['msg_id'])
    if not user.phone_number:
        await message.answer(text=texts['start_message'])
        await sleep(1.5)
        await message.answer(text=texts['without_number_message'], reply_markup=contact_kb())
        return
    else:
        await message.answer(text=texts['start_message'])
        await sleep(1.5)
        if voting_available(user):
            msg = await message.answer(text=texts['nomination_message'], reply_markup=nominations_kb(user))
            await state.update_data(msg_id=msg.message_id)
        else:
            await message.answer(text=texts['no_more_nominations_message'])


@router.message(F.contact)
async def handle_contact(message: types.Message, user: User) -> None:
    if message.contact:
        user.phone_number = message.contact.phone_number
        await message.answer(text=texts['phone_number_accepted_message'], reply_markup=types.ReplyKeyboardRemove())
        if voting_available(user):
            await message.answer(text=texts['nomination_message'], reply_markup=nominations_kb(user))


@router.callback_query(NominationCallback.filter())
async def handle_nomination(
    callback: types.CallbackQuery, callback_data: NominationCallback, db_session: AsyncSession
) -> None:
    await callback.answer()
    nominees: list[Nominee] = await get_nominees(callback_data.nomination, db_session)
    await callback.message.edit_text(
        await get_nominees_list(callback_data.nomination, nominees),
        reply_markup=nominee_kb(nominees),
        disable_web_page_preview=True,
    )


@router.callback_query(NomineeCallback.filter())
async def handle_nominee(
    callback: types.CallbackQuery, callback_data: NomineeCallback, db_session: AsyncSession
) -> None:
    await callback.answer()
    nomenee = await get_nominee(callback_data.nominee_id, db_session)
    nomenee_name = nomenee.name + ' ' + nomenee.last_name if nomenee.last_name else nomenee.name
    await callback.message.edit_text(
        texts['vote_are_you_sure_message'].format(number_to_nomination(callback_data.nomination), nomenee_name),
        reply_markup=vote_confirmation_kb(callback_data.nomination, callback_data.nominee_id),
    )


@router.callback_query(VoteConfirmationCallback.filter())
async def handle_vote_confirmation(
    callback: types.CallbackQuery,
    callback_data: NomineeCallback,
    user: User,
    queue: Queue,
    db_session: AsyncSession,
) -> None:
    nominees: list[Nominee] = await get_nominees(callback_data.nomination, db_session)
    nominee = await get_nominee(callback_data.nominee_id, db_session)
    username = '@' + user.username if user.username else ''
    nominee_name = nominee.name + ' ' + nominee.last_name if nominee.last_name else nominee.name
    if callback_data.action == Action.VOTE:
        vote_field_name = f"voted_{callback_data.nomination.value}"
        if hasattr(user, vote_field_name):
            setattr(user, vote_field_name, True)
        vote = Vote(
            user_id=user.id,
            nomination=callback_data.nomination,
            vote_for=callback_data.nominee_id,
        )
        db_session.add(vote)
        await db_session.flush()
        vote_task: VoteTask = VoteTask(
            nomination=callback_data.nomination,
            user_fullname=user.fullname,
            user_id=user.id,
            user_username=username,
            user_phone_number=user.phone_number,
            nominee_name=nominee_name,
            user_vote_for=nominee.id,
            date=vote.created_at.strftime("%d.%m.%Y %H:%M:%S"),
        )
        task = TaskModel(task_type=TaskType.VOTE_LOGGER, task_data=vote_task)
        queue.put_nowait(task)
        if voting_available(user):
            await callback.answer(texts['vote_accepted_message'], show_alert=True)
            await callback.message.edit_text(text=texts['nomination_message'], reply_markup=nominations_kb(user))
            return
        else:
            await callback.answer(texts['last_vote_accepted_message'], show_alert=True)
            await callback.message.edit_text(texts['no_more_nominations_message'])
            return
    else:
        await callback.message.edit_text(
            await get_nominees_list(callback_data.nomination, nominees),
            reply_markup=nominee_kb(nominees),
            disable_web_page_preview=True,
        )
