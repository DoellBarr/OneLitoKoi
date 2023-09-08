from tortoise import Model, fields


class Bidders(Model):
    id = fields.IntField(pk=True, null=False, auto_increment=True)
    bid_time = fields.DatetimeField()
    user_id = fields.BigIntField(default=None)
    bid_id = fields.CharField(max_length=255, default=None)
    price_offered = fields.IntField(default=None)
    bid_type = fields.CharField(max_length=255, default=None)
    created_at = fields.DatetimeField()
    status = fields.CharField(default="bidder", max_length=255)

    class Meta:
        table = "bidder_table"
