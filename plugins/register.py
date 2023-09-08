from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram import types, Router, F, Dispatcher
from aiogram.enums import ChatType

import configs
from plugins.state import RegisterState

register_router = Router(name="register_router")


class RegisterCallback(CallbackData, prefix="register"):
    status: str


@register_router.message(Command("registrasi", ignore_mention=True))
async def state_nama(m: types.Message, state: FSMContext):
    if m.chat.type != ChatType.PRIVATE:
        return await m.reply(
            "Silakan tekan tombol dibawah ini untuk melakukan registrasi",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="Registrasi",
                            url=f"t.me/{configs.bot_username}?start=registrasi",
                        )
                    ]
                ]
            ),
        )
    await state.set_state(RegisterState.alamat)
    return await m.answer("Siapa nama kamu?", reply_markup=types.ForceReply())


@register_router.message(RegisterState.alamat)
async def state_alamat(m: types.Message, state: FSMContext):
    await state.update_data(nama=m.text)
    await state.set_state(RegisterState.kota)
    return await m.answer("Alamat lengkap kamu?", reply_markup=types.ForceReply())


@register_router.message(RegisterState.kota)
async def state_kota(m: types.Message, state: FSMContext):
    await state.update_data(alamat=m.text)
    await state.set_state(RegisterState.no_wa)
    return await m.answer("Kota domisili kamu?", reply_markup=types.ForceReply())


@register_router.message(RegisterState.no_wa)
async def state_no_wa(m: types.Message, state: FSMContext):
    await state.update_data(kota=m.text)
    await state.set_state(RegisterState.confirmation)
    return await m.answer("Nomor WhatsApp kamu?", reply_markup=types.ForceReply())


@register_router.message(RegisterState.confirmation)
async def state_finish(m: types.Message, state: FSMContext):
    await state.update_data(no_wa=m.text)
    data = await state.get_data()
    await state.clear()
    nama = data["nama"]
    alamat = data["alamat"]
    kota = data["kota"]
    no_wa = data["no_wa"]
    return await m.answer(
        f"""Apakah data Anda sudah benar?
Nama: {nama}
Alamat: {alamat}
Kota: {kota}
Nomor WhatsApp: {no_wa}""",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Sudah",
                        callback_data=RegisterCallback(status="finish").pack(),
                    ),
                    types.InlineKeyboardButton(
                        text="Belum",
                        callback_data=RegisterCallback(status="cancel").pack(),
                    ),
                ]
            ]
        ),
    )


@register_router.callback_query(
    RegisterCallback.filter(F.status.in_({"finish", "cancel"}))
)
async def callback_query(
    call: types.CallbackQuery, state: FSMContext, callback_data: RegisterCallback
):
    if callback_data == RegisterCallback(status="finish"):
        # TODO: Masukin ke db
        await call.answer("Terima kasih sudah mendaftar!")
        await call.message.delete()
    elif callback_data == RegisterCallback(status="cancel"):
        return await state_nama(call.message, state)
