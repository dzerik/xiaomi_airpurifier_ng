"""Model profiles must select real drivers and reject unknown hardware."""

import pytest
from miio import AirDogX3, AirHumidifierJsq, AirHumidifierJsqs, AirPurifierMiot, Fan1C

from custom_components.xiaomi_miio_airpurifier_ng.const import SUPPORTED_MODELS, DeviceCategory


def test_every_supported_model_has_a_driver():
    """Adding a model without a usable driver cannot silently fall back."""
    from custom_components.xiaomi_miio_airpurifier_ng.device_profiles import (
        create_device,
        get_device_profile,
    )

    for model in SUPPORTED_MODELS:
        profile = get_device_profile(model)
        device = create_device("192.0.2.1", "0" * 32, model)
        assert type(device) is profile.driver
        assert profile.category is not DeviceCategory.UNKNOWN
        assert callable(device.status)


def test_dehumidifier_is_selectable():
    """The documented dehumidifier must be offered by manual/cloud setup."""
    assert "nwt.derh.wdh318efw1" in SUPPORTED_MODELS


@pytest.mark.parametrize(
    "model,driver",
    [
        ("zhimi.airpurifier.ma4", AirPurifierMiot),
        ("dmaker.fan.1c", Fan1C),
        ("airdog.airpurifier.x3", AirDogX3),
        ("shuii.humidifier.jsq001", AirHumidifierJsq),
        ("deerma.humidifier.jsq2w", AirHumidifierJsqs),
    ],
)
def test_family_selects_its_protocol(model, driver):
    from custom_components.xiaomi_miio_airpurifier_ng.device_profiles import create_device

    assert type(create_device("192.0.2.1", "0" * 32, model)) is driver


@pytest.mark.parametrize("model", [None, "", "unknown.model", "zhimi.fan.not_supported"])
def test_unknown_model_is_rejected(model):
    from custom_components.xiaomi_miio_airpurifier_ng.device_profiles import (
        UnsupportedModelError,
        get_device_profile,
    )

    with pytest.raises(UnsupportedModelError):
        get_device_profile(model)


def test_jsq001_does_not_advertise_target_humidity():
    from custom_components.xiaomi_miio_airpurifier_ng.device_profiles import get_device_profile

    profile = get_device_profile("shuii.humidifier.jsq001")
    assert profile.humidity is None
    assert "set_target_humidity" not in profile.commands


def test_documented_v3_volume_and_2s_filter_reset_are_available():
    """Historical feature masks cannot hide a supported, described driver command."""
    from custom_components.xiaomi_miio_airpurifier_ng.device_profiles import get_device_profile

    assert "set_volume" in get_device_profile("zhimi.airpurifier.v3").commands
    assert "reset_filter" in get_device_profile("zhimi.airpurifier.mc1").commands


@pytest.mark.parametrize("value,expected", [(40, 40), (45, 40), (50, 50), (55, 60), (60, 60)])
def test_dehumidifier_quantizes_within_supported_range(value, expected):
    from custom_components.xiaomi_miio_airpurifier_ng.device_profiles import get_device_profile

    assert get_device_profile("nwt.derh.wdh318efw1").humidity.normalize(value) == expected


@pytest.mark.parametrize("value", [30, 61, 80])
def test_dehumidifier_rejects_out_of_range(value):
    from custom_components.xiaomi_miio_airpurifier_ng.device_profiles import get_device_profile

    with pytest.raises(ValueError):
        get_device_profile("nwt.derh.wdh318efw1").humidity.normalize(value)
