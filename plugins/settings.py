from aiogram.enums import ParseMode

import configs
from .state import *
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from datetime import datetime as dt, timedelta as td
from controllers import scheduler, auction
from schemas import auction as schemas


settings_router = Router(name="settings_router")


class SetWaktuCallback(CallbackData, prefix="set_waktu"):
    extra_time: int


class SetWaktuConfirm(CallbackData, prefix="set_waktu"):
    confirm: bool


def now():
    return (dt.now() + td(minutes=10)).strftime("%d/%m/%Y %H:%M")


# region Tata Tertib
@settings_router.message(Command("set_tata_tertib"))
async def set_tata_tertib(m: types.Message, state: FSMContext):
    if m.chat.id != configs.admin_chat_id:
        return await m.reply("Maaf, perintah ini hanya bisa digunakan oleh admin")
    data = auction.load_data()
    if data and data.running:
        return await m.reply(
            "Lelang sedang berlangsung, tidak bisa mengubah tata tertib"
        )
    else:
        await state.clear()
    await state.set_state(SetTataTertibState.tata_tertib)
    return await m.reply(
        "Masukkan tata tertib lelang",
        reply_markup=types.ForceReply(),
    )


@settings_router.message(SetTataTertibState.tata_tertib)
async def set_tata_tertib_tata_tertib(m: types.Message, state: FSMContext):
    data = auction.load_data()
    data.rules = m.text
    auction.save_data(data)
    rules = m.text
    await state.clear()
    return await m.reply(
        f"Tata tertib telah di set menjadi:\n{rules}",
    )


# endregion


# region Set Data Ikan
@settings_router.message(Command("set_data_ikan"))
async def set_data_ikan(m: types.Message, state: FSMContext):
    if m.chat.id != configs.admin_chat_id:
        return await m.reply("Maaf, perintah ini hanya bisa digunakan oleh admin")
    data = auction.load_data()
    if data and data.running:
        return await m.reply("Lelang sedang berlangsung, tidak bisa mengubah data ikan")
    else:
        await state.clear()
    await state.set_state(SetDataIkanState.data)
    return await m.reply(
        "Masukkan data ikan yang akan dilelang, ketik /skip untuk mengabaikan",
        reply_markup=types.ForceReply(),
    )


@settings_router.message(SetDataIkanState.data)
async def set_data_ikan_data(m: types.Message, state: FSMContext, bot: Bot):
    username = (await bot.me()).username
    data = auction.load_data()
    if m.text in ("/skip", f"/skip@{username}"):
        data.description = None
        return await m.reply("Data ikan tidak di set", reply_markup=types.ForceReply())
    data.description = m.text
    auction.save_data(data)
    data_ikan = m.text
    await state.clear()
    return await m.reply(
        f"Data ikan yang akan dilelang adalah:\n{data_ikan}",
    )


# endregion


# region Set Waktu Lelang
@settings_router.message(Command("set_waktu_lelang"))
async def set_waktu_lelang(m: types.Message, state: FSMContext):
    if m.chat.id != configs.admin_chat_id:
        return await m.reply("Maaf, perintah ini hanya bisa digunakan oleh admin")
    data = auction.load_data()
    if data and data.running:
        return await m.reply(
            "Lelang sedang berlangsung, tidak bisa mengubah waktu lelang"
        )
    else:
        await state.clear()
    data = auction.load_data()
    if not data or not data.rules:
        return await m.reply(
            "Silakan atur tata tertib terlebih dahulu dengan mengetik /set_tata_tertib",
            parse_mode=None,
        )
    await state.set_state(SetWaktuState.judul)
    return await m.reply("Masukkan judul lelang", reply_markup=types.ForceReply())


@settings_router.message(SetWaktuState.judul)
async def set_waktu_lelang_judul(m: types.Message, state: FSMContext):
    await state.update_data(judul=m.text)
    await state.set_state(SetWaktuState.start)
    return await m.reply(
        "Masukkan waktu mulai lelang (format: DD/MM/YYYY HH:MM)\n" f"Contoh: `{now()}`",
        reply_markup=types.ForceReply(),
    )


@settings_router.message(SetWaktuState.start)
async def set_waktu_lelang_start(m: types.Message, state: FSMContext):
    try:
        start_time = dt.strptime(m.text, "%d/%m/%Y %H:%M")
    except ValueError:
        await m.reply("Format waktu salah")
        return await m.reply(
            "Masukkan waktu mulai lelang (format: DD/MM/YYYY HH:MM)\n"
            f"Contoh: `{now()}`",
            reply_markup=types.ForceReply(),
        )
    if start_time < dt.now():
        await m.reply("Waktu mulai lelang tidak boleh kurang dari sekarang")
        return await m.reply(
            "Masukkan waktu mulai lelang (format: DD/MM/YYYY HH:MM)\n"
            f"Contoh: `{now()}`",
            reply_markup=types.ForceReply(),
        )
    await state.update_data(start=start_time)
    await state.set_state(SetWaktuState.end)
    return await m.reply(
        "Masukkan waktu berakhir lelang (format: DD/MM/YYYY HH:MM)\n"
        f"Contoh: `{now()}`",
        reply_markup=types.ForceReply(),
    )


@settings_router.message(SetWaktuState.end)
async def set_waktu_lelang_end(m: types.Message, state: FSMContext):
    try:
        end = dt.strptime(m.text, "%d/%m/%Y %H:%M")
    except ValueError:
        await m.reply("Format waktu salah")
        return await m.reply(
            "Masukkan waktu berakhir lelang (format: DD/MM/YYYY HH:MM)\n"
            f"Contoh: `{now()}`",
            reply_markup=types.ForceReply(),
        )
    data = await state.get_data()
    start_time = data["start"]
    if end < start_time:
        await m.reply("Waktu berakhir lelang tidak boleh kurang dari waktu mulai")
        return await m.reply(
            "Masukkan waktu berakhir lelang (format: DD/MM/YYYY HH:MM)\n"
            f"Contoh: `{now()}`",
            reply_markup=types.ForceReply(),
        )
    await state.update_data(end=end)
    await state.set_state(SetWaktuState.jumlah_ikan)
    return await m.reply(
        "Masukkan jumlah ikan yang akan dilelang", reply_markup=types.ForceReply()
    )


@settings_router.message(SetWaktuState.jumlah_ikan)
async def set_waktu_lelang_jumlah_ikan(m: types.Message, state: FSMContext):
    jumlah_ikan = m.text
    if not jumlah_ikan.isdigit():
        await m.reply("Jumlah ikan harus berupa angka")
        return await m.reply(
            "Masukkan jumlah ikan yang akan dilelang",
            reply_markup=types.ForceReply(),
        )
    jumlah_ikan = int(jumlah_ikan)
    if jumlah_ikan < 1:
        await m.reply("Jumlah ikan tidak boleh kurang dari 1")
        return await m.reply(
            "Masukkan jumlah ikan yang akan dilelang",
            reply_markup=types.ForceReply(),
        )
    await state.update_data(jumlah_ikan=jumlah_ikan)
    await state.set_state(SetWaktuState.ob)
    return await m.reply(
        "Masukkan harga open bid untuk semua ikan yang akan dilelang",
        reply_markup=types.ForceReply(),
    )


@settings_router.message(SetWaktuState.ob)
async def set_waktu_lelang_ob(m: types.Message, state: FSMContext):
    harga_ob = m.text
    if not harga_ob.isdigit():
        await m.reply("Harga open bid harus berupa angka")
        return await m.reply(
            "Masukkan harga open bid untuk semua ikan yang akan dilelang",
            reply_markup=types.ForceReply(),
        )
    harga_ob = int(harga_ob)
    if harga_ob < 1:
        await m.reply("Harga open bid tidak boleh kurang dari 1")
        return await m.reply(
            "Masukkan harga open bid untuk semua ikan yang akan dilelang",
            reply_markup=types.ForceReply(),
        )
    await state.update_data(harga_ob=harga_ob)
    await state.set_state(SetWaktuState.kb)
    return await m.reply(
        "Masukkan harga kelipatan bid untuk semua ikan yang akan dilelang",
        reply_markup=types.ForceReply(),
    )


@settings_router.message(SetWaktuState.kb)
async def set_waktu_lelang_kb(m: types.Message, state: FSMContext):
    harga_kb = m.text
    if not harga_kb.isdigit():
        await m.reply("Harga kelipatan bid harus berupa angka")
        return await m.reply(
            "Masukkan harga kelipatan bid untuk semua ikan yang akan dilelang",
            reply_markup=types.ForceReply(),
        )
    harga_kb = int(harga_kb)
    if harga_kb < 1:
        await m.reply("Harga kelipatan bid tidak boleh kurang dari 1")
        return await m.reply(
            "Masukkan harga kelipatan bid untuk semua ikan yang akan dilelang",
            reply_markup=types.ForceReply(),
        )
    await state.update_data(harga_kb=harga_kb)
    await state.set_state(SetWaktuState.extra_time)
    return await m.reply(
        "Silakan pilih tombol extra time untuk semua ikan yang akan dilelang",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="+0 Menit",
                        callback_data=SetWaktuCallback(extra_time=0).pack(),
                    ),
                    types.InlineKeyboardButton(
                        text="+5 Menit",
                        callback_data=SetWaktuCallback(extra_time=5).pack(),
                    ),
                    types.InlineKeyboardButton(
                        text="+10 Menit",
                        callback_data=SetWaktuCallback(extra_time=10).pack(),
                    ),
                ],
            ]
        ),
    )


@settings_router.callback_query(SetWaktuCallback.filter(F.extra_time.in_({0, 5, 10})))
async def set_waktu_lelang_extra_time(
    c: types.CallbackQuery, state: FSMContext, callback_data: SetWaktuCallback
):
    await c.message.delete()
    data = callback_data
    if data == SetWaktuCallback(extra_time=0):
        extra_time = 0
    elif data == SetWaktuCallback(extra_time=5):
        extra_time = 5
    elif data == SetWaktuCallback(extra_time=10):
        extra_time = 10
    else:
        return await c.reply("Error", show_alert=True)
    await state.update_data(extra_time=extra_time)
    data = await state.get_data()
    judul = data["judul"]
    start_time = data["start"]
    end_time = data["end"]
    jumlah_ikan = data["jumlah_ikan"]
    harga_ob = data["harga_ob"]
    harga_kb = data["harga_kb"]
    extra_time = data["extra_time"]
    return await c.message.answer(
        f"""Apakah data Anda sudah benar?
Judul: {judul}
Waktu Mulai: {start_time.strftime("%d/%m/%Y %H:%M")}
Waktu Berakhir: {end_time.strftime("%d/%m/%Y %H:%M")}
Jumlah Ikan: {jumlah_ikan}
Harga Open Bid: {harga_ob}
Harga Kelipatan Bid: {harga_kb}
Extra Time: {extra_time} Menit""",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Sudah",
                        callback_data=SetWaktuConfirm(confirm=True).pack(),
                    ),
                    types.InlineKeyboardButton(
                        text="Belum",
                        callback_data=SetWaktuConfirm(confirm=False).pack(),
                    ),
                ]
            ]
        ),
    )


@settings_router.callback_query(SetWaktuConfirm.filter(F.confirm.in_({True, False})))
async def set_waktu_lelang_confirm(
    c: types.CallbackQuery,
    callback_data: SetWaktuConfirm,
    bot: Bot,
    state: FSMContext,
):
    data = callback_data
    await c.message.delete()
    if data == SetWaktuConfirm(confirm=True):
        data = await state.get_data()
        await state.clear()
        auction_data = auction.load_data()
        start_time = data["start"]
        auction_data.start_time = start_time
        auction_data.end_time = data["end"]
        auction_data.extra_time = int(data["extra_time"])
        auction_data.harga_ob = int(data["harga_ob"])
        auction_data.harga_kb = int(data["harga_kb"])
        auction_data.judul = data["judul"]

        jumlah_ikan = int(data["jumlah_ikan"])
        auction_data.fish_data = [
            schemas.FishSchema(no=i) for i in range(1, jumlah_ikan + 1)
        ]
        auction.save_data(auction_data)
        scheduler.add_job(
            auction.start,
            "date",
            run_date=start_time - td(seconds=30),
            args=(c.message.bot,),
            id=f"lelang_{c.message.chat.id}_{start_time.timestamp()}",
            misfire_grace_time=60 * 5,
        )
        await c.message.answer(
            "Lelang berhasil ditambahkan, silakan cek grup auction untuk melihat status lelang.",
        )
        return await bot.send_message(
            configs.auction_chat_id,
            f"Akan ada lelang yang akan dimulai pada {start_time.strftime('%d/%m/%Y %H:%M')}",
        )
    await state.clear()
    return await set_waktu_lelang(c.message, state)


# endregion
