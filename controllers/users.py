from models import Users


async def get(user_id: int):
    return await Users.get_or_none(user_id=user_id)


async def get_all():
    return await Users.all()


async def create(
    user_id: int,
    full_name: str,
    alamat_tinggal: str,
    kota_tinggal: str,
    no_telp: str,
):
    return await Users.create(
        user_id=user_id,
        full_name=full_name,
        alamat_tinggal=alamat_tinggal,
        kota_tinggal=kota_tinggal,
        no_telp=no_telp,
    )


async def update(user_id: int, **kwargs):
    return await Users.filter(user_id=user_id).update(**kwargs)


async def delete(user_id: int):
    if await get(user_id):
        return await Users.filter(user_id=user_id).delete()
    return None
