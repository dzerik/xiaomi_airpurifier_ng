"""Fan entities for Xiaomi Miio Air Purifier NG integration."""

from .air_fresh import XiaomiAirFreshFan
from .base import XiaomiGenericFan, XiaomiMiioBaseFan
from .humidifier import XiaomiAirHumidifierFan
from .purifier import XiaomiAirPurifierFan
from .standing import XiaomiStandingFan

__all__ = [
    "XiaomiMiioBaseFan",
    "XiaomiGenericFan",
    "XiaomiAirPurifierFan",
    "XiaomiAirHumidifierFan",
    "XiaomiAirFreshFan",
    "XiaomiStandingFan",
]
