from aiogram.fsm.state import StatesGroup, State


class AuctionState(StatesGroup):
    running = State()


class RegisterState(StatesGroup):
    nama = State()
    alamat = State()
    kota = State()
    no_wa = State()
    confirmation = State()


class SetDataIkanState(StatesGroup):
    data = State()


class SetTataTertibState(StatesGroup):
    tata_tertib = State()


class SetWaktuState(StatesGroup):
    judul = State()
    start = State()
    end = State()
    jumlah_ikan = State()
    ob = State()
    kb = State()
    extra_time = State()
