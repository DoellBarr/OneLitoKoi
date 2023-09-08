import asyncio
from typing import Union
from models import AuctionResults
from aiogram import Bot
import json
import configs
from controllers import scheduler
from schemas.auction import AuctionSchema
from datetime import timedelta as td


def to_schema(data: dict) -> AuctionSchema:
    return AuctionSchema(**data)


def load_data() -> Union[AuctionSchema, None]:
    with open("data/auction.json", "r") as f:
        data = f.read()
    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        return AuctionSchema()
    else:
        return to_schema(data) if data else None


def save_data(data: AuctionSchema):
    with open("data/auction.json", "w") as f:
        dump_json = data.model_dump_json(indent=4)
        f.write(dump_json)


def clear_data():
    with open("data/auction.json", "w") as f:
        f.write(json.dumps({}))
    return True


def extract_text(data: AuctionSchema) -> str:
    deskripsi = data.description
    extra_time = data.extra_time
    fish_data = data.fish_data
    tata_tertib = data.rules
    start_time = data.start_time.strftime("%d %B %Y %H:%M:%S")
    end_time = data.end_time.strftime("%d %B %Y %H:%M:%S")
    harga_ob = data.harga_ob
    harga_kb = data.harga_kb
    total_fish = len(fish_data)
    desc_text = (
        f"Data Ikan: \n{deskripsi}\n" if deskripsi else "Data Ikan TERTERA PADA FOTO"
    )
    extra_time_text = (
        f"Extra Time: {extra_time} menit, berlaku kelipatan hingga selesai\n"
        if extra_time
        else ""
    )
    fish_text = "".join(
        f"Ikan {fish.no}: {fish.bidder.bid if fish.bidder else ''} {fish.bidder.bidder if fish.bidder else ''}\n"
        for fish in fish_data
    )
    return f"""{data.judul}

Start: {start_time}
End: {end_time}
{extra_time_text}

Total Ikan: {total_fish}
OB: {harga_ob}K
KB: {harga_kb}K

Jump bid dipersilahkan dan menyesuaikan kelipatan bid

**WAJIB DIBACA, TATA TERTIB LELANG**
{tata_tertib}

{'-'*20}
{desc_text}

Rekap Update Lelang:
{fish_text}

Formula Penulisan bidding ketik /info

⚠️** HATI-HATI PENIPUAN **⚠️

Rekening pembayaran Onelito Koi hanya ada 1 yaitu:
**BCA KCP Gedung Talavera Jakarta Selatan a/n PT ONELITO KOI AQUATIC a/c 522.561.6016**

__Detail TATA TERTIB GROUP dapat dilihat pada pinned message diatas__

** -\r-Make Hobbyist Happy -\r-**
"""


async def send_message(bot: Bot):
    data = load_data()
    text = extract_text(data)
    return await bot.send_message(configs.auction_chat_id, text)


async def start(bot: Bot):
    i = 30
    data = load_data()
    if not data.running:
        data.running = True
        save_data(data)
    while i > 0:
        if i % 10 == 0:
            await bot.send_message(
                configs.auction_chat_id, f"Lelang akan dimulai dalam {i} detik"
            )
        if i in range(5):
            await bot.send_message(
                configs.auction_chat_id, f"Lelang akan dimulai: {i} detik lagi"
            )
        i -= 1
        await asyncio.sleep(1)
        data = load_data()
        if not data.running:
            break
    await send_message(bot)
    save_data(data)
    scheduler.add_job(
        stop,
        "date",
        run_date=data.end_time,
        args=[bot],
        id=f"stop_auction{data.end_time}",
    )


async def send_alert(bot: Bot):
    data = load_data()
    extra_time = data.extra_time
    extra_time *= 60
    for i in range(extra_time):
        data = load_data()
        if not data.running:
            break
        if i % 60 == 0:
            await bot.send_message(
                configs.auction_chat_id, f"Lelang akan berakhir dalam {i // 60} menit"
            )
            await asyncio.sleep(1)
        if i in range(3) and data.extra_time_status:
            await rekap_akhir(bot)
        i -= 1


async def stop(bot: Bot):
    data = load_data()
    data.extra_time_status = True
    data.bidder_in_extra_time = False
    end_time = data.end_time
    if data.extra_time_status and data.bidder_in_extra_time:
        extra_time = data.extra_time
        end_time = end_time + td(minutes=extra_time)
    await asyncio.sleep(2)
    data.end_time = end_time
    save_data(data)
    return await send_alert(bot)


async def rekap_akhir(bot: Bot):
    final_text = "-\r- [ FINAL RESULT ] -\r-\n\n"
    data = load_data()
    text = extract_text(data)
    await bot.send_message(configs.auction_chat_id, final_text)
    data.running = False
    fish_data = data.fish_data
    winner = {}
    for fish in fish_data:
        user = fish.bidder
        if user.bid:
            fish_number = fish.no
            if user not in winner:
                winner[user] = [fish_number]
            else:
                winner[user].append(fish_number)
    if not winner:
        clear_data()
        return await bot.send_message(
            configs.auction_chat_id, "Tidak ada yang memenangkan lelang pada hari ini"
        )
    winner_text = "".join(
        f"{user.bidder}: Ikan {fish}\n" for user, fish in winner.items()
    )
    text = f"{text}\n\n{winner_text}\nSelanjutnya akan difollow-up oleh admin"
    await bot.send_message(configs.auction_chat_id, text)
    await asyncio.gather(save_to_db())


async def save_to_db():
    data = load_data()
    auction_results = []
    for fish in data.fish_data:
        if bidder := fish.bidder:
            result = AuctionResults(
                start_time=data.start_time,
                end_time=data.end_time,
                ob=data.harga_ob,
                kb=data.harga_kb,
                extra_time=data.extra_time,
                nomor_ikan=fish.no,
                judul_lelang=data.judul,
                winner_user_id=bidder.id,
                harga_akhir=bidder.bid,
                full_name=bidder.name,
            )
            auction_results.append(result)
    await AuctionResults.bulk_create(auction_results)
    clear_data()
