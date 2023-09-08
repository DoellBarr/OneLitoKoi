from .info import info_router
from .register import register_router
from .start import start_router
from .bidding import bidding_router
from .settings import settings_router
from .rekap import rekap_router


routers = [
    info_router,
    register_router,
    start_router,
    bidding_router,
    settings_router,
    rekap_router,
]
