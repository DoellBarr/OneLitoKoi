from tortoise import Model, fields


class AuctionResults(Model):
    id = fields.IntField(pk=True, null=False)
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    ob = fields.IntField()
    kb = fields.IntField()
    extra_time = fields.IntField()
    nomor_ikan = fields.IntField()
    judul_lelang = fields.TextField()
    winner_user_id = fields.BigIntField()
    harga_akhir = fields.IntField(default=0)
    full_name = fields.CharField(max_length=255, default="")
    created_at = fields.DatetimeField(auto_now=True)
    updated_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "auction_results"
