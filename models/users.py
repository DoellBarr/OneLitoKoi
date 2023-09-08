from tortoise import Model, fields


class Users(Model):
    user_id = fields.BigIntField(pk=True, null=False)
    full_name = fields.CharField(max_length=255)
    alamat_tinggal = fields.CharField(max_length=255)
    kota_tinggal = fields.CharField(max_length=255)
    no_telp = fields.CharField(max_length=32)
    upload_time = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now=True)
    updated_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "member_table"
