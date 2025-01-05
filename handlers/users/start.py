from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from filters import IsPrivate

from loader import dp


@dp.message_handler(IsPrivate(), CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"Assalamu Alaikum, {message.from_user.full_name}")

# @dp.message_handler(content_types=['text'])
# async def get_group_id(message: types.Message):
#     if message.chat.type in ['group', 'supergroup']:
#         await message.reply(f"Group ID: {message.chat.id}")

