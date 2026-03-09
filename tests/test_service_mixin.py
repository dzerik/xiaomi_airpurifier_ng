"""Tests for DeviceServiceMixin in service_mixin.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.xiaomi_miio_airpurifier_ng.const import (
    FEATURE_RESET_FILTER,
    FEATURE_SET_AUTO_DETECT,
    FEATURE_SET_BUZZER,
    FEATURE_SET_CHILD_LOCK,
    FEATURE_SET_CLEAN_MODE,
    FEATURE_SET_DISPLAY_ORIENTATION,
    FEATURE_SET_DRY,
    FEATURE_SET_EXTRA_FEATURES,
    FEATURE_SET_FAN_LEVEL,
    FEATURE_SET_FAVORITE_LEVEL,
    FEATURE_SET_FAVORITE_SPEED,
    FEATURE_SET_LEARN_MODE,
    FEATURE_SET_LED,
    FEATURE_SET_LED_BRIGHTNESS,
    FEATURE_SET_MOTOR_SPEED,
    FEATURE_SET_NATURAL_MODE,
    FEATURE_SET_OSCILLATION_ANGLE,
    FEATURE_SET_PTC,
    FEATURE_SET_PTC_LEVEL,
    FEATURE_SET_TARGET_HUMIDITY,
    FEATURE_SET_VOLUME,
    FEATURE_SET_WET_PROTECTION,
)
from custom_components.xiaomi_miio_airpurifier_ng.service_mixin import (
    DeviceServiceMixin,
)


class ConcreteServiceHost(DeviceServiceMixin):
    """Конкретный класс-хост для тестирования DeviceServiceMixin.

    Имитирует XiaomiMiioEntity + CoordinatorEntity, предоставляя
    _device_features, _try_command и coordinator.
    """

    def __init__(self, features: int) -> None:
        self._device_features = features
        self.coordinator = MagicMock()
        self.coordinator.device = MagicMock()
        self.coordinator.async_request_refresh = AsyncMock()
        self._try_command = AsyncMock()


@pytest.fixture
def host_all_features() -> ConcreteServiceHost:
    """Хост со всеми feature-флагами включенными."""
    all_flags = (
        FEATURE_SET_BUZZER
        | FEATURE_SET_LED
        | FEATURE_SET_CHILD_LOCK
        | FEATURE_SET_LED_BRIGHTNESS
        | FEATURE_SET_FAVORITE_LEVEL
        | FEATURE_SET_AUTO_DETECT
        | FEATURE_SET_LEARN_MODE
        | FEATURE_SET_VOLUME
        | FEATURE_RESET_FILTER
        | FEATURE_SET_EXTRA_FEATURES
        | FEATURE_SET_TARGET_HUMIDITY
        | FEATURE_SET_DRY
        | FEATURE_SET_OSCILLATION_ANGLE
        | FEATURE_SET_NATURAL_MODE
        | FEATURE_SET_FAN_LEVEL
        | FEATURE_SET_MOTOR_SPEED
        | FEATURE_SET_PTC
        | FEATURE_SET_PTC_LEVEL
        | FEATURE_SET_FAVORITE_SPEED
        | FEATURE_SET_DISPLAY_ORIENTATION
        | FEATURE_SET_WET_PROTECTION
        | FEATURE_SET_CLEAN_MODE
    )
    return ConcreteServiceHost(all_flags)


@pytest.fixture
def host_no_features() -> ConcreteServiceHost:
    """Хост без единого feature-флага."""
    return ConcreteServiceHost(0)


# ---------------------------------------------------------------------------
# Вспомогательные данные: описание каждого сервис-метода
# (method_name, feature_flag, device_method_name, extra_args)
# Для on/off-пар: bool-аргумент True/False
# Для методов без feature-guard: feature_flag = None
# ---------------------------------------------------------------------------

TOGGLE_SERVICES = [
    ("async_set_buzzer_on", FEATURE_SET_BUZZER, "set_buzzer", (True,)),
    ("async_set_buzzer_off", FEATURE_SET_BUZZER, "set_buzzer", (False,)),
    ("async_set_child_lock_on", FEATURE_SET_CHILD_LOCK, "set_child_lock", (True,)),
    ("async_set_child_lock_off", FEATURE_SET_CHILD_LOCK, "set_child_lock", (False,)),
    ("async_set_led_on", FEATURE_SET_LED, "set_led", (True,)),
    ("async_set_led_off", FEATURE_SET_LED, "set_led", (False,)),
    ("async_set_auto_detect_on", FEATURE_SET_AUTO_DETECT, "set_auto_detect", (True,)),
    ("async_set_auto_detect_off", FEATURE_SET_AUTO_DETECT, "set_auto_detect", (False,)),
    ("async_set_learn_mode_on", FEATURE_SET_LEARN_MODE, "set_learn_mode", (True,)),
    ("async_set_learn_mode_off", FEATURE_SET_LEARN_MODE, "set_learn_mode", (False,)),
    ("async_set_dry_on", FEATURE_SET_DRY, "set_dry", (True,)),
    ("async_set_dry_off", FEATURE_SET_DRY, "set_dry", (False,)),
    ("async_set_clean_mode_on", FEATURE_SET_CLEAN_MODE, "set_clean_mode", (True,)),
    ("async_set_clean_mode_off", FEATURE_SET_CLEAN_MODE, "set_clean_mode", (False,)),
    (
        "async_set_wet_protection_on",
        FEATURE_SET_WET_PROTECTION,
        "set_wet_protection",
        (True,),
    ),
    (
        "async_set_wet_protection_off",
        FEATURE_SET_WET_PROTECTION,
        "set_wet_protection",
        (False,),
    ),
    (
        "async_set_natural_mode_on",
        FEATURE_SET_NATURAL_MODE,
        "set_natural_mode",
        (True,),
    ),
    (
        "async_set_natural_mode_off",
        FEATURE_SET_NATURAL_MODE,
        "set_natural_mode",
        (False,),
    ),
    ("async_set_ptc_on", FEATURE_SET_PTC, "set_ptc", (True,)),
    ("async_set_ptc_off", FEATURE_SET_PTC, "set_ptc", (False,)),
]

PARAMETERIZED_SERVICES = [
    (
        "async_set_led_brightness",
        FEATURE_SET_LED_BRIGHTNESS,
        "set_led_brightness",
        {"brightness": 2},
    ),
    (
        "async_set_favorite_level",
        FEATURE_SET_FAVORITE_LEVEL,
        "set_favorite_level",
        {"level": 5},
    ),
    ("async_set_fan_level", FEATURE_SET_FAN_LEVEL, "set_fan_level", {"level": 3}),
    ("async_set_volume", FEATURE_SET_VOLUME, "set_volume", {"volume": 75}),
    (
        "async_set_extra_features",
        FEATURE_SET_EXTRA_FEATURES,
        "set_extra_features",
        {"features": 42},
    ),
    (
        "async_set_target_humidity",
        FEATURE_SET_TARGET_HUMIDITY,
        "set_target_humidity",
        {"humidity": 60},
    ),
    (
        "async_set_motor_speed",
        FEATURE_SET_MOTOR_SPEED,
        "set_motor_speed",
        {"motor_speed": 1200},
    ),
    (
        "async_set_favorite_speed",
        FEATURE_SET_FAVORITE_SPEED,
        "set_favorite_speed",
        {"speed": 800},
    ),
    (
        "async_set_oscillation_angle",
        FEATURE_SET_OSCILLATION_ANGLE,
        "set_angle",
        {"angle": 90},
    ),
    ("async_set_ptc_level", FEATURE_SET_PTC_LEVEL, "set_ptc_level", {"level": "high"}),
    (
        "async_set_display_orientation",
        FEATURE_SET_DISPLAY_ORIENTATION,
        "set_display_orientation",
        {"orientation": "landscape"},
    ),
]

# Методы без feature-guard (всегда выполняются)
NO_GUARD_SERVICES = [
    ("async_set_delay_off", "delay_off", {"delay_off_countdown": 120}),
    ("async_set_display_on", "set_display", {}),
    ("async_set_display_off", "set_display", {}),
    ("async_set_filters_cleaned", "reset_dust_filter", {}),
]


# ===========================================================================
# Тесты: toggle-сервисы (on/off пары)
# ===========================================================================


class TestToggleServicesWithFeatureEnabled:
    """Тесты toggle-сервисов при включенном feature-флаге."""

    @pytest.mark.parametrize(
        "method_name,feature_flag,device_method,args",
        TOGGLE_SERVICES,
        ids=[t[0] for t in TOGGLE_SERVICES],
    )
    @pytest.mark.asyncio
    async def test_calls_try_command_with_correct_device_method(
        self,
        host_all_features: ConcreteServiceHost,
        method_name: str,
        feature_flag: int,
        device_method: str,
        args: tuple,
    ) -> None:
        """При включенном флаге вызывается _try_command с правильным методом устройства."""
        method = getattr(host_all_features, method_name)
        await method()

        host_all_features._try_command.assert_awaited_once()
        call_args = host_all_features._try_command.call_args
        # arg[0] — сообщение об ошибке (str), arg[1] — метод устройства, arg[2+] — аргументы
        assert call_args[0][1] == getattr(host_all_features.coordinator.device, device_method)
        # Проверяем передаваемые аргументы (True/False для toggle)
        actual_extra_args = call_args[0][2:]
        assert actual_extra_args == args

    @pytest.mark.parametrize(
        "method_name,feature_flag,device_method,args",
        TOGGLE_SERVICES,
        ids=[t[0] for t in TOGGLE_SERVICES],
    )
    @pytest.mark.asyncio
    async def test_calls_async_request_refresh(
        self,
        host_all_features: ConcreteServiceHost,
        method_name: str,
        feature_flag: int,
        device_method: str,
        args: tuple,
    ) -> None:
        """После выполнения команды вызывается async_request_refresh."""
        method = getattr(host_all_features, method_name)
        await method()

        host_all_features.coordinator.async_request_refresh.assert_awaited_once()


class TestToggleServicesWithFeatureDisabled:
    """Тесты toggle-сервисов при выключенном feature-флаге."""

    @pytest.mark.parametrize(
        "method_name,feature_flag,device_method,args",
        TOGGLE_SERVICES,
        ids=[t[0] for t in TOGGLE_SERVICES],
    )
    @pytest.mark.asyncio
    async def test_returns_early_without_calling_try_command(
        self,
        host_no_features: ConcreteServiceHost,
        method_name: str,
        feature_flag: int,
        device_method: str,
        args: tuple,
    ) -> None:
        """При выключенном флаге метод возвращается сразу, не вызывая _try_command."""
        method = getattr(host_no_features, method_name)
        await method()

        host_no_features._try_command.assert_not_awaited()
        host_no_features.coordinator.async_request_refresh.assert_not_awaited()


# ===========================================================================
# Тесты: параметризованные сервисы (с аргументами)
# ===========================================================================


class TestParameterizedServicesWithFeatureEnabled:
    """Тесты сервисов с параметрами при включенном feature-флаге."""

    @pytest.mark.parametrize(
        "method_name,feature_flag,device_method,kwargs",
        PARAMETERIZED_SERVICES,
        ids=[t[0] for t in PARAMETERIZED_SERVICES],
    )
    @pytest.mark.asyncio
    async def test_calls_try_command_with_correct_args(
        self,
        host_all_features: ConcreteServiceHost,
        method_name: str,
        feature_flag: int,
        device_method: str,
        kwargs: dict,
    ) -> None:
        """При включенном флаге вызывается _try_command с правильными аргументами."""
        method = getattr(host_all_features, method_name)
        await method(**kwargs)

        host_all_features._try_command.assert_awaited_once()
        call_args = host_all_features._try_command.call_args
        assert call_args[0][1] == getattr(host_all_features.coordinator.device, device_method)
        # Значение аргумента передается третьим позиционным аргументом
        expected_value = list(kwargs.values())[0]
        assert call_args[0][2] == expected_value

    @pytest.mark.parametrize(
        "method_name,feature_flag,device_method,kwargs",
        PARAMETERIZED_SERVICES,
        ids=[t[0] for t in PARAMETERIZED_SERVICES],
    )
    @pytest.mark.asyncio
    async def test_calls_async_request_refresh(
        self,
        host_all_features: ConcreteServiceHost,
        method_name: str,
        feature_flag: int,
        device_method: str,
        kwargs: dict,
    ) -> None:
        """После выполнения команды вызывается async_request_refresh."""
        method = getattr(host_all_features, method_name)
        await method(**kwargs)

        host_all_features.coordinator.async_request_refresh.assert_awaited_once()


class TestParameterizedServicesWithFeatureDisabled:
    """Тесты сервисов с параметрами при выключенном feature-флаге."""

    @pytest.mark.parametrize(
        "method_name,feature_flag,device_method,kwargs",
        PARAMETERIZED_SERVICES,
        ids=[t[0] for t in PARAMETERIZED_SERVICES],
    )
    @pytest.mark.asyncio
    async def test_returns_early_without_calling_try_command(
        self,
        host_no_features: ConcreteServiceHost,
        method_name: str,
        feature_flag: int,
        device_method: str,
        kwargs: dict,
    ) -> None:
        """При выключенном флаге метод возвращается сразу."""
        method = getattr(host_no_features, method_name)
        await method(**kwargs)

        host_no_features._try_command.assert_not_awaited()
        host_no_features.coordinator.async_request_refresh.assert_not_awaited()


# ===========================================================================
# Тесты: reset_filter (с feature-guard, но без дополнительных аргументов)
# ===========================================================================


class TestResetFilter:
    """Тесты для async_reset_filter."""

    @pytest.mark.asyncio
    async def test_with_feature_enabled_calls_reset_filter(
        self, host_all_features: ConcreteServiceHost
    ) -> None:
        """При включенном FEATURE_RESET_FILTER вызывается reset_filter без аргументов."""
        await host_all_features.async_reset_filter()

        host_all_features._try_command.assert_awaited_once()
        call_args = host_all_features._try_command.call_args
        assert call_args[0][1] == host_all_features.coordinator.device.reset_filter
        # reset_filter не принимает дополнительных аргументов
        assert len(call_args[0]) == 2
        host_all_features.coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_with_feature_disabled_returns_early(
        self, host_no_features: ConcreteServiceHost
    ) -> None:
        """При выключенном FEATURE_RESET_FILTER метод возвращается сразу."""
        await host_no_features.async_reset_filter()

        host_no_features._try_command.assert_not_awaited()
        host_no_features.coordinator.async_request_refresh.assert_not_awaited()


# ===========================================================================
# Тесты: сервисы без feature-guard
# ===========================================================================


class TestNoGuardServices:
    """Тесты для сервисов, которые не проверяют feature-флаги."""

    @pytest.mark.asyncio
    async def test_set_delay_off_always_calls_try_command(
        self, host_no_features: ConcreteServiceHost
    ) -> None:
        """async_set_delay_off всегда вызывается, даже без feature-флагов."""
        await host_no_features.async_set_delay_off(delay_off_countdown=120)

        host_no_features._try_command.assert_awaited_once()
        call_args = host_no_features._try_command.call_args
        assert call_args[0][1] == host_no_features.coordinator.device.delay_off
        assert call_args[0][2] == 120
        host_no_features.coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_set_display_on_always_calls_try_command(
        self, host_no_features: ConcreteServiceHost
    ) -> None:
        """async_set_display_on всегда вызывается, даже без feature-флагов."""
        await host_no_features.async_set_display_on()

        host_no_features._try_command.assert_awaited_once()
        call_args = host_no_features._try_command.call_args
        assert call_args[0][1] == host_no_features.coordinator.device.set_display
        assert call_args[0][2] is True
        host_no_features.coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_set_display_off_always_calls_try_command(
        self, host_no_features: ConcreteServiceHost
    ) -> None:
        """async_set_display_off всегда вызывается, даже без feature-флагов."""
        await host_no_features.async_set_display_off()

        host_no_features._try_command.assert_awaited_once()
        call_args = host_no_features._try_command.call_args
        assert call_args[0][1] == host_no_features.coordinator.device.set_display
        assert call_args[0][2] is False
        host_no_features.coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_set_filters_cleaned_always_calls_try_command(
        self, host_no_features: ConcreteServiceHost
    ) -> None:
        """async_set_filters_cleaned всегда вызывается, даже без feature-флагов."""
        await host_no_features.async_set_filters_cleaned()

        host_no_features._try_command.assert_awaited_once()
        call_args = host_no_features._try_command.call_args
        assert call_args[0][1] == host_no_features.coordinator.device.reset_dust_filter
        # Нет дополнительных аргументов
        assert len(call_args[0]) == 2
        host_no_features.coordinator.async_request_refresh.assert_awaited_once()


# ===========================================================================
# Тесты: проверка единичного feature-флага
# ===========================================================================


class TestSingleFeatureFlag:
    """Тесты: метод вызывается только при наличии конкретного флага."""

    @pytest.mark.asyncio
    async def test_buzzer_on_requires_only_buzzer_flag(self) -> None:
        """async_set_buzzer_on работает при наличии только FEATURE_SET_BUZZER."""
        host = ConcreteServiceHost(FEATURE_SET_BUZZER)
        await host.async_set_buzzer_on()
        host._try_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_buzzer_on_skipped_with_unrelated_flag(self) -> None:
        """async_set_buzzer_on пропускается если установлен другой, нерелевантный флаг."""
        host = ConcreteServiceHost(FEATURE_SET_LED)
        await host.async_set_buzzer_on()
        host._try_command.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_target_humidity_requires_only_its_flag(self) -> None:
        """async_set_target_humidity работает при наличии только FEATURE_SET_TARGET_HUMIDITY."""
        host = ConcreteServiceHost(FEATURE_SET_TARGET_HUMIDITY)
        await host.async_set_target_humidity(humidity=50)
        host._try_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_oscillation_angle_requires_only_its_flag(self) -> None:
        """async_set_oscillation_angle работает при наличии только соответствующего флага."""
        host = ConcreteServiceHost(FEATURE_SET_OSCILLATION_ANGLE)
        await host.async_set_oscillation_angle(angle=120)
        host._try_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_ptc_level_requires_only_its_flag(self) -> None:
        """async_set_ptc_level работает при наличии только FEATURE_SET_PTC_LEVEL."""
        host = ConcreteServiceHost(FEATURE_SET_PTC_LEVEL)
        await host.async_set_ptc_level(level="low")
        host._try_command.assert_awaited_once()


# ===========================================================================
# Тесты: сообщение об ошибке передается как первый аргумент _try_command
# ===========================================================================


class TestErrorMessagePassed:
    """Проверяем, что error message (первый аргумент _try_command) — строка с %s."""

    @pytest.mark.parametrize(
        "method_name,feature_flag,device_method,args",
        TOGGLE_SERVICES,
        ids=[t[0] for t in TOGGLE_SERVICES],
    )
    @pytest.mark.asyncio
    async def test_toggle_error_message_is_string_with_placeholder(
        self,
        host_all_features: ConcreteServiceHost,
        method_name: str,
        feature_flag: int,
        device_method: str,
        args: tuple,
    ) -> None:
        """Первый аргумент _try_command — строка-шаблон ошибки с %s."""
        method = getattr(host_all_features, method_name)
        await method()

        error_msg = host_all_features._try_command.call_args[0][0]
        assert isinstance(error_msg, str)
        assert "%s" in error_msg


# ===========================================================================
# Тесты: default-значения параметров
# ===========================================================================


class TestDefaultParameterValues:
    """Проверяем default-значения для методов с дефолтными аргументами."""

    @pytest.mark.asyncio
    async def test_led_brightness_default_is_2(
        self, host_all_features: ConcreteServiceHost
    ) -> None:
        """async_set_led_brightness без аргументов использует brightness=2."""
        await host_all_features.async_set_led_brightness()
        assert host_all_features._try_command.call_args[0][2] == 2

    @pytest.mark.asyncio
    async def test_favorite_level_default_is_1(
        self, host_all_features: ConcreteServiceHost
    ) -> None:
        """async_set_favorite_level без аргументов использует level=1."""
        await host_all_features.async_set_favorite_level()
        assert host_all_features._try_command.call_args[0][2] == 1

    @pytest.mark.asyncio
    async def test_fan_level_default_is_1(self, host_all_features: ConcreteServiceHost) -> None:
        """async_set_fan_level без аргументов использует level=1."""
        await host_all_features.async_set_fan_level()
        assert host_all_features._try_command.call_args[0][2] == 1

    @pytest.mark.asyncio
    async def test_volume_default_is_50(self, host_all_features: ConcreteServiceHost) -> None:
        """async_set_volume без аргументов использует volume=50."""
        await host_all_features.async_set_volume()
        assert host_all_features._try_command.call_args[0][2] == 50

    @pytest.mark.asyncio
    async def test_extra_features_default_is_1(
        self, host_all_features: ConcreteServiceHost
    ) -> None:
        """async_set_extra_features без аргументов использует features=1."""
        await host_all_features.async_set_extra_features()
        assert host_all_features._try_command.call_args[0][2] == 1
