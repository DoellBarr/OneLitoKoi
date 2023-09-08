from aiogram import Router, types, Dispatcher, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from .state import AuctionState

rekap_router = Router(name="rekap_router")


@rekap_router.message(Command("rekap"))
async def rekap_handler(m: types.Message, bot: Bot, dispatcher: Dispatcher):
    ctx: FSMContext = dispatcher.fsm.get_context(bot, m.from_user.id, m.from_user.id)
    state_data = await ctx.get_state()
    if not state_data or state_data != AuctionState.running:
        return await m.reply("Tidak ada lelang yang berjalan saat ini")
    return await m.reply("Rekap lelang.")
