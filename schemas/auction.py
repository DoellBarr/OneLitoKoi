from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class BidderSchema(BaseModel):
    id: int
    name: str
    bid: int = 0

    @property
    def bidder(self):
        return f"[{self.name}](tg://user?id={self.id})"

    @property
    def price(self):
        return self.bid


class FishSchema(BaseModel):
    no: int
    bidder: Optional[BidderSchema] = None
    last_bidder: Optional[BidderSchema] = None


class AuctionSchema(BaseModel):
    judul: str = ""
    rules: str = ""
    description: str = ""
    start_time: datetime = datetime.now()
    end_time: datetime = datetime.now()
    fish_data: List["FishSchema"] = []
    harga_ob: int = 0
    harga_kb: int = 0
    extra_time: int = 0
    running: bool = False
    extra_time_status: bool = False
    bidder_in_extra_time: bool = False
