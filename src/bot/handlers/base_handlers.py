from aiogram import F, Router, types
from aiogram.filters import CommandStart
from gspread import Client
from sqlalchemy.ext.asyncio import AsyncSession

from bot.enums import Action
from bot.internal.gsheets import create_new_vote_record_gsheet
from bot.internal.helpers import get_nominees_list, number_to_nomination, voting_available
from bot.keyboards.callbacks import NominationCallback, NomineeCallback, VoteConfirmationCallback
from bot.keyboards.markups import contact_kb, nominations_kb, nominee_kb, vote_confirmation_kb
from bot.lexicon import texts
from database.crud.nominee import get_nominee, get_nominees
from database.models import Nominee, User, Vote

router = Router()


@router.message(CommandStart())
async def start_message(message: types.Message, user: User) -> None:
    if not user.phone_number:
        await message.answer(text=texts['start_message'])
        await message.answer(text=texts['without_number_message'],
                             reply_markup=contact_kb())
        return
    else:
        await message.answer(text=texts['start_message'])
        if voting_available(user):
            await message.answer(text=texts['nomination_message'],
                                 reply_markup=nominations_kb(user))
        else:
            await message.answer(text=texts['no_more_nominations_message'])


@router.message(F.contact)
async def handle_contact(message: types.Message, user: User) -> None:
    if message.contact:
        user.phone_number = message.contact.phone_number
        if voting_available(user):
            await message.answer(text=texts['nomination_message'],
                                 reply_markup=nominations_kb(user))


@router.callback_query(NominationCallback.filter())
async def handle_nomination(callback: types.CallbackQuery, callback_data: NominationCallback, db_session: AsyncSession) -> None:
    await callback.answer()
    nominees: list[Nominee] = await get_nominees(callback_data.nomination, db_session)
    await callback.message.edit_text(await get_nominees_list(callback_data.nomination, nominees),
                                     reply_markup=nominee_kb(nominees),
                                     disable_web_page_preview=True)


@router.callback_query(NomineeCallback.filter())
async def handle_nominee(
    callback: types.CallbackQuery,
    callback_data: NomineeCallback,
    db_session: AsyncSession
) -> None:
    await callback.answer()
    nomenee = await get_nominee(callback_data.nominee_id, db_session)
    nomenee_name = nomenee.name + ' ' + nomenee.last_name if nomenee.last_name else nomenee.name
    await callback.message.edit_text(texts['vote_are_you_sure_message'].format(number_to_nomination(callback_data.nomination), nomenee_name),
                                     reply_markup=vote_confirmation_kb(callback_data.nomination, callback_data.nominee_id))


@router.callback_query(VoteConfirmationCallback.filter())
async def handle_vote_confirmation(
    callback: types.CallbackQuery,
    callback_data: NomineeCallback,
    user: User,
    gspread_client: Client,
    db_session: AsyncSession
) -> None:
    nominees: list[Nominee] = await get_nominees(callback_data.nomination, db_session)
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
        if voting_available(user):
            await callback.answer(texts['vote_accepted_message'], show_alert=True)
            await callback.message.edit_text(text=texts['nomination_message'],
                                             reply_markup=nominations_kb(user))
            await create_new_vote_record_gsheet(vote, gspread_client, db_session)
            return
        else:
            await callback.message.edit_text(texts['no_more_nominations_message'])
            return
    else:
        await callback.message.edit_text(await get_nominees_list(callback_data.nomination, nominees),
                                         reply_markup=nominee_kb(nominees),
                                         disable_web_page_preview=True)
