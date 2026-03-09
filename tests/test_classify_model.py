"""Tests for classify_model() function in const.py."""

from __future__ import annotations

import pytest

from custom_components.xiaomi_miio_airpurifier_ng.const import (
    HUMIDIFIER_MIOT,
    MODEL_AIRDEHUMIDIFIER_V1,
    MODEL_AIRFRESH_A1,
    MODEL_AIRFRESH_T2017,
    MODEL_AIRFRESH_VA2,
    MODEL_AIRFRESH_VA4,
    MODEL_AIRHUMIDIFIER_CA4,
    MODEL_AIRHUMIDIFIER_CB1,
    MODEL_AIRHUMIDIFIER_JSQ001,
    MODEL_AIRHUMIDIFIER_MJJSQ,
    MODEL_AIRHUMIDIFIER_V1,
    MODEL_AIRPURIFIER_2S,
    MODEL_AIRPURIFIER_3,
    MODEL_AIRPURIFIER_3H,
    MODEL_AIRPURIFIER_AIRDOG_X3,
    MODEL_AIRPURIFIER_AIRDOG_X5,
    MODEL_AIRPURIFIER_AIRDOG_X7SM,
    MODEL_AIRPURIFIER_M1,
    MODEL_AIRPURIFIER_PRO,
    MODEL_AIRPURIFIER_V1,
    MODEL_AIRPURIFIER_ZA1,
    MODEL_FAN_1C,
    MODEL_FAN_LESHOW_SS4,
    MODEL_FAN_P5,
    MODEL_FAN_V2,
    MODEL_FAN_ZA1,
    PURIFIER_MIOT,
    DeviceCategory,
    classify_model,
)


class TestClassifyModelPurifier:
    """Тесты классификации моделей очистителей воздуха."""

    @pytest.mark.parametrize(
        "model",
        [
            MODEL_AIRPURIFIER_V1,
            MODEL_AIRPURIFIER_M1,
            MODEL_AIRPURIFIER_PRO,
            MODEL_AIRPURIFIER_2S,
        ],
        ids=["v1", "m1", "pro_v6", "2s_mc1"],
    )
    def test_zhimi_airpurifier_prefix_returns_purifier(self, model: str) -> None:
        """Модели с префиксом zhimi.airpurifier классифицируются как PURIFIER."""
        assert classify_model(model) == DeviceCategory.PURIFIER

    @pytest.mark.parametrize(
        "model",
        [MODEL_AIRPURIFIER_3, MODEL_AIRPURIFIER_3H, MODEL_AIRPURIFIER_ZA1],
        ids=["ma4", "mb3", "za1"],
    )
    def test_purifier_miot_models_return_purifier(self, model: str) -> None:
        """Модели из списка PURIFIER_MIOT классифицируются как PURIFIER."""
        assert model in PURIFIER_MIOT
        assert classify_model(model) == DeviceCategory.PURIFIER

    @pytest.mark.parametrize(
        "model",
        [
            MODEL_AIRPURIFIER_AIRDOG_X3,
            MODEL_AIRPURIFIER_AIRDOG_X5,
            MODEL_AIRPURIFIER_AIRDOG_X7SM,
        ],
        ids=["x3", "x5", "x7sm"],
    )
    def test_airdog_airpurifier_prefix_returns_purifier(self, model: str) -> None:
        """Модели с префиксом airdog.airpurifier классифицируются как PURIFIER."""
        assert classify_model(model) == DeviceCategory.PURIFIER

    def test_unknown_zhimi_airpurifier_returns_purifier(self) -> None:
        """Неизвестная модель с префиксом zhimi.airpurifier все равно PURIFIER."""
        assert classify_model("zhimi.airpurifier.future99") == DeviceCategory.PURIFIER


class TestClassifyModelHumidifier:
    """Тесты классификации моделей увлажнителей."""

    @pytest.mark.parametrize(
        "model",
        [MODEL_AIRHUMIDIFIER_V1, MODEL_AIRHUMIDIFIER_CB1],
        ids=["v1", "cb1"],
    )
    def test_zhimi_humidifier_prefix_returns_humidifier(self, model: str) -> None:
        """Модели с префиксом zhimi.humidifier классифицируются как HUMIDIFIER."""
        assert classify_model(model) == DeviceCategory.HUMIDIFIER

    def test_humidifier_miot_model_returns_humidifier(self) -> None:
        """Модели из списка HUMIDIFIER_MIOT классифицируются как HUMIDIFIER."""
        assert MODEL_AIRHUMIDIFIER_CA4 in HUMIDIFIER_MIOT
        assert classify_model(MODEL_AIRHUMIDIFIER_CA4) == DeviceCategory.HUMIDIFIER

    @pytest.mark.parametrize(
        "model",
        [MODEL_AIRHUMIDIFIER_MJJSQ],
        ids=["mjjsq"],
    )
    def test_deerma_humidifier_prefix_returns_humidifier(self, model: str) -> None:
        """Модели с префиксом deerma.humidifier классифицируются как HUMIDIFIER."""
        assert classify_model(model) == DeviceCategory.HUMIDIFIER

    def test_shuii_humidifier_prefix_returns_humidifier(self) -> None:
        """Модели с префиксом shuii.humidifier классифицируются как HUMIDIFIER."""
        assert classify_model(MODEL_AIRHUMIDIFIER_JSQ001) == DeviceCategory.HUMIDIFIER

    def test_unknown_deerma_humidifier_returns_humidifier(self) -> None:
        """Неизвестная модель с префиксом deerma.humidifier все равно HUMIDIFIER."""
        assert classify_model("deerma.humidifier.newmodel") == DeviceCategory.HUMIDIFIER


class TestClassifyModelAirFresh:
    """Тесты классификации моделей приточной вентиляции."""

    @pytest.mark.parametrize(
        "model",
        [MODEL_AIRFRESH_VA2, MODEL_AIRFRESH_VA4],
        ids=["va2", "va4"],
    )
    def test_zhimi_airfresh_prefix_returns_air_fresh(self, model: str) -> None:
        """Модели с префиксом zhimi.airfresh классифицируются как AIR_FRESH."""
        assert classify_model(model) == DeviceCategory.AIR_FRESH

    @pytest.mark.parametrize(
        "model",
        [MODEL_AIRFRESH_A1, MODEL_AIRFRESH_T2017],
        ids=["a1", "t2017"],
    )
    def test_dmaker_airfresh_prefix_returns_air_fresh(self, model: str) -> None:
        """Модели с префиксом dmaker.airfresh классифицируются как AIR_FRESH."""
        assert classify_model(model) == DeviceCategory.AIR_FRESH


class TestClassifyModelFan:
    """Тесты классификации моделей вентиляторов."""

    @pytest.mark.parametrize(
        "model",
        [MODEL_FAN_V2, MODEL_FAN_ZA1],
        ids=["v2", "za1"],
    )
    def test_zhimi_fan_prefix_returns_fan(self, model: str) -> None:
        """Модели с префиксом zhimi.fan классифицируются как FAN."""
        assert classify_model(model) == DeviceCategory.FAN

    @pytest.mark.parametrize(
        "model",
        [MODEL_FAN_P5, MODEL_FAN_1C],
        ids=["p5", "1c"],
    )
    def test_dmaker_fan_prefix_returns_fan(self, model: str) -> None:
        """Модели с префиксом dmaker.fan классифицируются как FAN."""
        assert classify_model(model) == DeviceCategory.FAN

    def test_leshow_fan_prefix_returns_fan(self) -> None:
        """Модели с префиксом leshow.fan классифицируются как FAN."""
        assert classify_model(MODEL_FAN_LESHOW_SS4) == DeviceCategory.FAN


class TestClassifyModelDehumidifier:
    """Тесты классификации моделей осушителей."""

    def test_nwt_derh_prefix_returns_dehumidifier(self) -> None:
        """Модели с префиксом nwt.derh классифицируются как DEHUMIDIFIER."""
        assert classify_model(MODEL_AIRDEHUMIDIFIER_V1) == DeviceCategory.DEHUMIDIFIER

    def test_unknown_nwt_derh_returns_dehumidifier(self) -> None:
        """Неизвестная модель с префиксом nwt.derh все равно DEHUMIDIFIER."""
        assert classify_model("nwt.derh.newmodel") == DeviceCategory.DEHUMIDIFIER


class TestClassifyModelUnknown:
    """Тесты для неизвестных и невалидных моделей."""

    def test_none_returns_unknown(self) -> None:
        """None возвращает UNKNOWN."""
        assert classify_model(None) == DeviceCategory.UNKNOWN

    def test_empty_string_returns_unknown(self) -> None:
        """Пустая строка возвращает UNKNOWN."""
        assert classify_model("") == DeviceCategory.UNKNOWN

    def test_completely_unknown_model_returns_unknown(self) -> None:
        """Полностью неизвестная модель возвращает UNKNOWN."""
        assert classify_model("unknown.device.model") == DeviceCategory.UNKNOWN

    def test_partial_prefix_with_startswith_still_matches(self) -> None:
        """Модель с расширенным префиксом zhimi.airpurifier все равно PURIFIER (startswith)."""
        # classify_model использует startswith, поэтому "zhimi.airpurifierX" тоже подходит
        assert classify_model("zhimi.airpurifierX.v1") == DeviceCategory.PURIFIER

    def test_different_vendor_prefix_does_not_match(self) -> None:
        """Модель с другим вендором не классифицируется ошибочно."""
        assert classify_model("other.airpurifier.v1") == DeviceCategory.UNKNOWN

    def test_random_string_returns_unknown(self) -> None:
        """Произвольная строка возвращает UNKNOWN."""
        assert classify_model("foobar") == DeviceCategory.UNKNOWN
