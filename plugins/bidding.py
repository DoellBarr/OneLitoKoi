from re import Match
from typing import List

from aiogram import Router, types, F
import configs
from controllers import auction
from controllers.auction import AuctionSchema
from schemas.auction import FishSchema, BidderSchema


bidding_router = Router(name="bidding_router")

pattern = r"^/ ?(all|[\d\s]+) ?([Oo][Bb]|[Kk][Bb]|\d+|)"


def add_ob(data: FishSchema, user: types.User):
    auction_data = auction.load_data()
    if not data.bidder or data.bidder.bid is None:
        data.bidder = BidderSchema(
            id=user.id, name=user.full_name, bid=auction_data.harga_ob
        )
        data.last_bidder = data.bidder
        return data
    return False


def add_kb(data: FishSchema, user: types.User):
    if not data.bidder:
        return False
    auction_data = auction.load_data()
    data.last_bidder = data.bidder
    data.bidder.bid += auction_data.harga_kb
    data.bidder.id = user.id
    data.bidder.name = user.full_name
    return data


def price_handler(data: FishSchema, price: int, user: types.User):
    auction_data = auction.load_data()
    if not data.bidder:
        data.bidder = BidderSchema(id=user.id, name=user.full_name, bid=price)
    if (data.bidder.bid - price) % auction_data.harga_kb != 0:
        return False
    data.bidder.bid = price
    data.bidder.id = user.id
    data.bidder.name = user.full_name
    return data


async def reply_alert(m: types.Message, data: set, text: str):
    data = sorted(data)
    data = ", ".join(map(str, data))
    auction_data = auction.load_data()
    await m.reply(text.format(data=data, harga_kb=auction_data.harga_kb))
    if (
        auction_data.extra_time_status
        and {auction_data.extra_time, auction_data.end_time} is not None
    ):
        await auction.send_message(m.bot)
        return await auction.stop(m.bot)
    return await auction.send_message(m.bot)


@bidding_router.message(F.text.regexp(pattern).as_("match"))
async def bidding_handler(m: types.Message, match: Match):
    if m.chat.id != configs.auction_chat_id:
        return await m.reply("Maaf, perintah ini hanya bisa digunakan di grup auction")
    data = auction.load_data()
    if not data or not data.running:
        return await m.reply("Saat ini sedang tidak ada lelang yang sedang berlangsung")
    fish_number = match[1]
    bid_type = match[2] or fish_number.strip().split(" ")[-1]
    if fish_number == "all":
        return await all_handler(m, bid_type, data)
    fish_numbers = list(map(int, fish_number.strip().split(" ")))
    if bid_type == "ob":
        return await ob_kb_handler(m, fish_numbers, data)
    elif bid_type == "kb":
        return await ob_kb_handler(m, fish_numbers, data, is_ob=False)
    elif bid_type.isdigit():
        price = int(bid_type)
        return await jumpbid_handler(m, fish_numbers, price, data)
    elif len(fish_numbers) > 2 and fish_numbers[1] >= data.harga_kb:
        fish_ids = fish_numbers[::2]
        fish_price = fish_numbers[1::2]
        if len(fish_ids) != len(fish_price):
            return await m.reply("Format bidding Anda salah")
        return await multibid_handler(m, fish_ids, fish_price, data)
    else:
        return await m.reply("Format bidding Anda salah")


async def all_handler(m: types.Message, bid_type: str, data: AuctionSchema):
    # sourcery skip: low-code-quality
    user = m.from_user
    accepted = set()
    under_price = set()
    same_price = set()
    cant_bid_kb = set()
    cant_bid_ob = set()
    forbidden = set()
    for fish in data.fish_data:
        if bid_type == "ob":
            if fish_data := add_ob(fish, user):
                accepted.add(fish.no)
                fish.bidder = fish_data.bidder
                fish.last_bidder = fish_data.last_bidder
                fish.no = fish_data.no
            else:
                cant_bid_ob.add(fish.no)
        elif bid_type == "kb":
            if fish_data := add_kb(fish, user):
                fish.last_bidder = fish_data.last_bidder
                fish.bidder = fish_data.bidder
                fish.no = fish_data.no
                accepted.add(fish.no)
            else:
                cant_bid_kb.add(fish.no)
        elif bid_type.isdigit():
            price = int(bid_type)
            if fish.bidder.bid > price:
                under_price.add(fish.no)
            elif fish.bidder.bid == price:
                same_price.add(fish.no)
            elif fish_data := price_handler(fish, price, user):
                fish.bidder = fish_data.bidder
                fish.last_bidder = fish_data.last_bidder
                fish.no = fish_data.no
                accepted.add(fish.no)
            else:
                forbidden.add(fish.no)
        else:
            return await m.reply("Format bidding Anda salah")
    if cant_bid_ob:
        text = "Ikan {data} bid tidak sah karena sudah ada yang melakukan bid"
        bid_data = cant_bid_ob
    elif cant_bid_kb:
        text = "Ikan {data} bid tidak sah karena anda belum melakukan bid"
        bid_data = cant_bid_kb
    elif under_price:
        text = "Ikan {data} bid tidak sah karena nominal yg anda bid kurang dari harga saat ini"
        bid_data = under_price
    elif forbidden:  # kalo harga tidak sesuai dengan kelipatan kb
        text = "Ikan {data} tidak bisa di bid karena harga yang anda bid tidak sesuai dengan kelipatan {harga_kb}"
        bid_data = forbidden
    elif same_price:
        text = "Ikan {data} bid tidak sah karena harga yang anda berikan sama dengan harga saat ini"
        bid_data = same_price
    else:
        text = "Ikan {data} bid sah"
        bid_data = accepted
    auction.save_data(data)
    return await reply_alert(m, bid_data, text)


async def ob_kb_handler(
    m: types.Message,
    fish_numbers: List[int],
    data: AuctionSchema,
    is_ob: bool = True,
):  # sourcery skip: merge-duplicate-blocks
    user = m.from_user
    forbidden = set()
    accepted = set()
    wrong_fish_no = set()
    cant_kb = set()
    for no, fish in enumerate(data.fish_data):
        fish_number = fish.no
        if fish_number not in fish_numbers:
            wrong_fish_no.add(fish_number)
        if is_ob:
            if not (fish_data := add_ob(fish, user)):  # Kalo udah ada yang ob
                # gabisa ob lagi
                forbidden.add(fish_number)
            else:
                accepted.add(fish_number)
                data.fish_data[no] = fish_data
        else:
            if fish_data := add_kb(fish, user):
                accepted.add(fish_number)
                data.fish_data[no] = fish_data
            else:
                forbidden.add(fish_number)
                cant_kb.add(fish_number)
    if forbidden:
        text = "Ikan {data} bid tidak sah karena sudah ada yang melakukan bid"
        bid_data = forbidden
    elif cant_kb:
        text = "Ikan {data} bid tidak sah karena belum dilakukan ob"
        bid_data = cant_kb
    elif wrong_fish_no:
        text = "Ikan {data} bid tidak sah karena nomor ikan tidak ada"
        bid_data = wrong_fish_no
    else:
        text = "Ikan {data} bid sah"
        bid_data = accepted
    auction.save_data(data)
    return await reply_alert(m, bid_data, text)


async def jumpbid_handler(
    m: types.Message, fish_numbers: List[int], price: int, data: AuctionSchema
):
    user = m.from_user
    accepted = set()
    under_price = set()
    forbidden = set()
    same_price = set()
    no_ob = set()
    wrong_fish_no = set()
    for fish in data.fish_data:
        if fish.no in fish_numbers:
            if bidder := fish.bidder:
                if bidder.price > price:
                    under_price.add(fish.no)
                elif bidder.price == price:
                    same_price.add(fish.no)
                elif (price - bidder.price) % data.harga_kb != 0:
                    forbidden.add(fish.no)
                else:
                    fish_data = price_handler(fish, price, user)
                    fish.bidder = fish_data.bidder
                    fish.last_bidder = fish_data.last_bidder
                    fish.no = fish_data.no
                    accepted.add(fish.no)
            elif not bidder:
                no_ob.add(fish.no)
            elif bidder.price % data.harga_kb != 0:
                forbidden.add(fish.no)
            else:
                fish_data = price_handler(fish, price, user)
                fish.bidder = fish_data.bidder
                fish.last_bidder = fish_data.last_bidder
                fish.no = fish_data.no
                accepted.add(fish.no)
        else:
            wrong_fish_no.add(fish.no)
    if wrong_fish_no:
        text = "Ikan {data} bid tidak sah karena nomor ikan tidak ada"
        bid_data = wrong_fish_no
    elif no_ob:
        text = "Ikan {data} bid tidak sah karena belum dilakukan ob"
        bid_data = no_ob
    elif under_price:
        text = "Ikan {data} bid tidak sah karena nominal yg anda bid kurang dari harga saat ini"
        bid_data = under_price
    elif forbidden:
        text = "Ikan {data} tidak bisa di bid karena harga yang anda bid tidak sesuai dengan kelipatan {harga_kb}"
        bid_data = forbidden
    elif same_price:
        text = "Ikan {data} bid tidak sah karena harga yang anda berikan sama dengan harga saat ini"
        bid_data = same_price
    else:
        text = "Ikan {data} bid sah"
        bid_data = accepted
    auction.save_data(data)
    return await reply_alert(m, bid_data, text)


async def multibid_handler(
    m: types.Message, fish_ids: List[int], fish_price: List[int], data: AuctionSchema
):
    under_price = set()
    forbidden = set()
    wrong_fish_no = set()
    accepted = set()
    same_price = set()
    no_ob = set()
    for fish in data.fish_data:
        if fish.no not in fish_ids:
            wrong_fish_no.add(fish.no)
        else:
            price = fish_price[fish_ids.index(fish.no)]
            if bidder := fish.bidder:
                if bidder.price > price:
                    under_price.add(fish.no)
                elif bidder.price == price:
                    same_price.add(fish.no)
                elif (price - bidder.price) % data.harga_kb != 0:
                    forbidden.add(fish.no)
                else:
                    fish_data = price_handler(fish, price, m.from_user)
                    fish.bidder = fish_data.bidder
                    fish.last_bidder = fish_data.last_bidder
                    fish.no = fish_data.no
                    accepted.add(fish.no)
            elif (bidder.price - price) % data.harga_kb != 0:
                forbidden.add(fish.no)
            else:
                fish_data = price_handler(fish, price, m.from_user)
                fish.bidder = fish_data.bidder
                fish.last_bidder = fish_data.last_bidder
                fish.no = fish_data.no
                accepted.add(fish.no)
    if wrong_fish_no:  # noqa
        text = "Ikan {data} bid tidak sah karena nomor ikan tidak ada"
        bid_data = wrong_fish_no
    elif no_ob:
        text = "Ikan {data} bid tidak sah karena belum dilakukan ob"
        bid_data = no_ob
    elif under_price:
        text = "Ikan {data} bid tidak sah karena nominal yg anda bid kurang dari harga saat ini"
        bid_data = under_price
    elif forbidden:
        text = "Ikan {data} tidak bisa di bid karena harga yang anda bid tidak sesuai dengan kelipatan {harga_kb}"
        bid_data = forbidden
    elif same_price:
        text = "Ikan {data} bid tidak sah karena harga yang anda berikan sama dengan harga saat ini"
        bid_data = same_price
    else:
        text = "Ikan {data} bid sah"
        bid_data = accepted
    auction.save_data(data)
    return await reply_alert(m, bid_data, text)
