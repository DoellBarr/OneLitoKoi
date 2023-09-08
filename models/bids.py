from tortoise import Model, fields


class Bids(Model):
    id = fields.IntField(pk=True, null=False, auto_increment=True)
    bid_id = fields.IntField(null=False, default=1)
    message_id_admin = fields.CharField(max_length=255, default=None)
    message_id_auction = fields.CharField(max_length=255, default=None)
    user_id = fields.BigIntField(default=None)
    upload_time = fields.DatetimeField()
    ob = fields.CharField(max_length=255, default=None)
    kb = fields.CharField(max_length=255, default=None)
    caption = fields.CharField(max_length=255, default=None)
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    extra_time = fields.CharField(max_length=255, default=None)
    final_bid = fields.CharField(max_length=255, default=None)
    file_ids = fields.CharField(max_length=2000, default=None)
    created_at = fields.DatetimeField()
    updated_at = fields.DatetimeField()
    status = fields.CharField(max_length=255, default=None)

    class Meta:
        table = "bid_table"
