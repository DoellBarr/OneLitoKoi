from aiogram import Router, types
from aiogram.filters import Command
import configs


info_router = Router(name="info_router")


@info_router.message(Command("info", "help"))
async def info_handler(m: types.Message):
    admin_text = (
        "\n/set_waktu_lelang: untuk menentukan waktu mulai dan berakhirnya  lelang"
        if m.chat.id == configs.admin_chat_id
        else ""
    )
    text = f"""Halo {m.from_user.mention}!
Untuk menggunakan bot ini, ada beberapa perintah, di antaranya:
/help atau /info: Untuk memunculkan bantuan ini
{admin_text}
/registrasi untuk melakukan registrasi ke grup auction

/1 ob : untuk melakukan bidding dengan harga ob ke nomor ikan atau semua ikan
Contoh: /1 2 ob -> Untuk melakukan ob ke nomor ikan satu dan dua, atau /all ob -> untuk melakukan ob ke semua ikan

/1 kb : Untuk melakukan bidding dengan harga kb ke nomor ikan atau semua ikan
Contoh: /1 2 kb -> Untuk melakukan kb dengan nomor ikan satu dan dua, atau /all kb -> Untuk melakukan kb ke semua ikan

/1 200 : Untuk melakukan jump bid dengan harga yang diinginkan ke nomor ikan yang ditentukan, dan harga yang di berikan pada akhir teks
Contoh: /1 2 200 -> Untuk melakukan jump bid ke nomor ikan satu dan dua dengan harga Rp.200 Ribu

/1 2 200 ob : Untuk melakukan jump bid dengan harga yang diinginkan ke nomor ikan yang ditentukan, dan harga yang di berikan pada akhir teks, dengan jenis bidding ob

/1 2 200 kb : Untuk melakukan jump bid dengan harga yang diinginkan ke nomor ikan yang ditentukan, dan harga yang di berikan pada akhir teks, dengan jenis bidding kb
    """
    return await m.reply(text)
