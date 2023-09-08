from aiogram import Router, types
from aiogram.enums import ChatType
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from plugins import register
from .state import AuctionState


start_router = Router(name="start_router")


@start_router.message(Command("run"))
async def run_handler(m: types.Message, state: FSMContext):
    await state.set_state(AuctionState.running)
    return await m.reply("Lelang telah dimulai")


@start_router.message(CommandStart(ignore_mention=True))
async def start_handler(m: types.Message, state: FSMContext, command: CommandObject):
    if m.chat in {ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL}:
        return await m.answer("Halo Member Grup!")
    args = command.args
    if args and args == "registrasi":
        return await register.state_nama(m, state)
    return await m.reply(
        f"Halo {m.from_user.full_name}!\n"
        f"Jika ingin mendaftar, silakan ketik /registrasi, dan jika ingin membaca "
        f"panduan silakan ketik /info. Terima kasih."
    )
