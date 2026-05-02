from __future__ import annotations

import io

from PIL import Image

from custom_components.eink_dashboard.const import (
    PADDING,
)
from custom_components.eink_dashboard.render import (
    render_dashboard,
)

MOCK_WEATHER_STATE = {
    "weather.home": {
        "state": "sunny",
        "attributes": {
            "temperature": 22,
            "humidity": 58,
            "wind_speed": 12,
            "forecast": [
                {
                    "datetime": "2026-05-02T12:00:00",
                    "temperature": 24,
                    "templow": 16,
                    "condition": "sunny",
                },
                {
                    "datetime": "2026-05-03T12:00:00",
                    "temperature": 19,
                    "templow": 14,
                    "condition": "cloudy",
                },
                {
                    "datetime": "2026-05-04T12:00:00",
                    "temperature": 21,
                    "templow": 15,
                    "condition": "partlycloudy",
                },
            ],
        },
    },
}


def _png_to_image(png_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(png_bytes))


def _pixel(img: Image.Image, x: int, y: int) -> int:
    val = img.getpixel((x, y))
    assert isinstance(val, int)
    return val


class TestRenderDashboard:
    def test_empty_widget_list_returns_white_image(self) -> None:
        config = {"width": 100, "height": 100}
        result = render_dashboard([], config)

        img = _png_to_image(result)
        assert img.mode == "L"
        assert img.size == (100, 100)
        assert _pixel(img, 50, 50) == 255

    def test_returns_valid_png(self) -> None:
        config = {"width": 200, "height": 300}
        result = render_dashboard([], config)

        img = _png_to_image(result)
        assert img.format == "PNG"
        assert img.size == (200, 300)

    def test_rotation_90(self) -> None:
        config = {"width": 200, "height": 100, "rotation": 90}
        result = render_dashboard([], config)

        img = _png_to_image(result)
        assert img.size == (100, 200)

    def test_rotation_270(self) -> None:
        config = {"width": 200, "height": 100, "rotation": 270}
        result = render_dashboard([], config)

        img = _png_to_image(result)
        assert img.size == (100, 200)

    def test_unknown_widget_type_is_skipped(self) -> None:
        config = {"width": 100, "height": 100}
        widgets = [{"type": "nonexistent", "x": 10, "y": 10}]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        assert img.size == (100, 100)


class TestRenderText:
    def test_text_draws_pixels(self) -> None:
        config = {"width": 200, "height": 100}
        widgets = [
            {
                "type": "text",
                "x": 10,
                "y": 10,
                "text": "Hello",
                "font_size": 20,
            }
        ]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        has_dark_pixel = any(
            _pixel(img, x, y) < 128
            for x in range(10, 100)
            for y in range(10, 40)
        )
        assert has_dark_pixel

    def test_text_right_align(self) -> None:
        config = {"width": 200, "height": 100}
        widgets = [
            {
                "type": "text",
                "x": 0,
                "y": 10,
                "text": "Hi",
                "font_size": 20,
                "align": "right",
            }
        ]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        has_dark_right = any(
            _pixel(img, x, y) < 128
            for x in range(140, 200)
            for y in range(10, 40)
        )
        assert has_dark_right

    def test_text_center_align(self) -> None:
        config = {"width": 200, "height": 100}
        widgets = [
            {
                "type": "text",
                "x": 0,
                "y": 10,
                "text": "Hi",
                "font_size": 20,
                "align": "center",
            }
        ]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        has_dark_center = any(
            _pixel(img, x, y) < 128
            for x in range(80, 120)
            for y in range(10, 40)
        )
        assert has_dark_center

    def test_text_custom_color(self) -> None:
        config = {"width": 200, "height": 100}
        widgets = [
            {
                "type": "text",
                "x": 10,
                "y": 10,
                "text": "Gray",
                "font_size": 20,
                "color": 160,
            }
        ]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        has_gray_pixel = any(
            100 < _pixel(img, x, y) < 200
            for x in range(10, 80)
            for y in range(10, 40)
        )
        assert has_gray_pixel


class TestRenderLine:
    def test_horizontal_line(self) -> None:
        config = {"width": 100, "height": 100}
        widgets = [
            {
                "type": "line",
                "x": 10,
                "y": 50,
                "x2": 90,
                "y2": 50,
                "color": 0,
            }
        ]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        assert _pixel(img, 50, 50) == 0
        assert _pixel(img, 50, 10) == 255

    def test_line_custom_color(self) -> None:
        config = {"width": 100, "height": 100}
        widgets = [
            {
                "type": "line",
                "x": 0,
                "y": 50,
                "x2": 99,
                "y2": 50,
                "color": 160,
            }
        ]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        assert _pixel(img, 50, 50) == 160


class TestRenderSeparator:
    def test_separator_spans_width(self) -> None:
        config = {"width": 200, "height": 100}
        widgets = [{"type": "separator", "y": 50, "color": 0}]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        assert _pixel(img, PADDING, 50) == 0
        assert _pixel(img, 175, 50) == 0
        # Outside separator range should be white
        assert _pixel(img, 10, 50) == 255

    def test_separator_default_color(self) -> None:
        config = {"width": 200, "height": 100}
        widgets = [{"type": "separator", "y": 50}]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        # Default is COLOR_LIGHT_GRAY = 210
        assert _pixel(img, 100, 50) == 210


class TestRenderWeather:
    def _config(self, **overrides: object) -> dict[str, object]:
        base: dict[str, object] = {
            "width": 600,
            "height": 400,
            "states": MOCK_WEATHER_STATE,
        }
        base.update(overrides)
        return base

    def test_weather_draws_temperature(self) -> None:
        widgets = [
            {
                "type": "weather",
                "entity": "weather.home",
                "x": PADDING,
                "y": 10,
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        has_dark = any(
            _pixel(img, x, y) < 128
            for x in range(PADDING + 100, 300)
            for y in range(10, 60)
        )
        assert has_dark

    def test_weather_draws_forecast(self) -> None:
        widgets = [
            {
                "type": "weather",
                "entity": "weather.home",
                "x": PADDING,
                "y": 10,
                "forecast_days": 3,
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        has_dark_forecast = any(
            _pixel(img, x, y) < 128
            for x in range(50, 550)
            for y in range(110, 200)
        )
        assert has_dark_forecast

    def test_weather_missing_entity_is_noop(self) -> None:
        widgets = [
            {
                "type": "weather",
                "entity": "weather.nonexistent",
                "x": PADDING,
                "y": 10,
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        all_white = all(
            _pixel(img, x, y) == 255
            for x in range(0, 600, 20)
            for y in range(0, 400, 20)
        )
        assert all_white

    def test_weather_no_forecast(self) -> None:
        states = {
            "weather.home": {
                "state": "cloudy",
                "attributes": {
                    "temperature": 15,
                    "humidity": 70,
                    "wind_speed": 20,
                    "forecast": [],
                },
            }
        }
        widgets = [
            {
                "type": "weather",
                "entity": "weather.home",
                "x": PADDING,
                "y": 10,
            }
        ]
        result = render_dashboard(
            widgets,
            {"width": 600, "height": 300, "states": states},
        )
        img = _png_to_image(result)
        assert img.size == (600, 300)
        has_icon = any(
            _pixel(img, x, y) < 200
            for x in range(PADDING, PADDING + 90)
            for y in range(10, 100)
        )
        assert has_icon
        has_temp = any(
            _pixel(img, x, y) < 128
            for x in range(PADDING + 100, 300)
            for y in range(10, 60)
        )
        assert has_temp

    def test_weather_icon_sunny(self) -> None:
        widgets = [
            {
                "type": "weather",
                "entity": "weather.home",
                "x": PADDING,
                "y": 10,
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        icon_area_has_drawing = any(
            _pixel(img, x, y) < 200
            for x in range(PADDING, PADDING + 90)
            for y in range(10, 100)
        )
        assert icon_area_has_drawing

    def test_weather_rainy_condition(self) -> None:
        states = {
            "weather.home": {
                "state": "rainy",
                "attributes": {
                    "temperature": 10,
                    "humidity": 90,
                    "wind_speed": 25,
                    "forecast": [],
                },
            }
        }
        widgets = [
            {
                "type": "weather",
                "entity": "weather.home",
                "x": PADDING,
                "y": 10,
            }
        ]
        result = render_dashboard(
            widgets,
            {"width": 600, "height": 200, "states": states},
        )
        img = _png_to_image(result)
        has_drawing = any(
            _pixel(img, x, y) < 200
            for x in range(PADDING, PADDING + 90)
            for y in range(10, 100)
        )
        assert has_drawing


MOCK_SENSOR_STATES = {
    "sensor.living_room_temperature": {
        "state": "22.1",
        "attributes": {
            "unit_of_measurement": "°C",
            "friendly_name": "Living Room",
        },
    },
    "sensor.bedroom_temperature": {
        "state": "19.8",
        "attributes": {
            "unit_of_measurement": "°C",
            "friendly_name": "Bedroom",
        },
    },
    "sensor.humidity": {
        "state": "45",
        "attributes": {
            "unit_of_measurement": "%",
            "friendly_name": "Humidity",
        },
    },
}


class TestRenderSensorRows:
    def _config(self, **overrides: object) -> dict[str, object]:
        base: dict[str, object] = {
            "width": 400,
            "height": 300,
            "states": MOCK_SENSOR_STATES,
        }
        base.update(overrides)
        return base

    def test_sensor_rows_draws_labels(self) -> None:
        widgets = [
            {
                "type": "sensor_rows",
                "x": PADDING,
                "y": 10,
                "entities": [
                    "sensor.living_room_temperature",
                    "sensor.bedroom_temperature",
                ],
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        has_dark_row1 = any(
            _pixel(img, x, y) < 128
            for x in range(PADDING, 200)
            for y in range(10, 40)
        )
        has_dark_row2 = any(
            _pixel(img, x, y) < 128
            for x in range(PADDING, 200)
            for y in range(40, 70)
        )
        assert has_dark_row1
        assert has_dark_row2

    def test_sensor_rows_with_title(self) -> None:
        widgets = [
            {
                "type": "sensor_rows",
                "x": PADDING,
                "y": 10,
                "title": "Temperature",
                "entities": [
                    "sensor.living_room_temperature",
                ],
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        has_title = any(
            _pixel(img, x, y) < 128
            for x in range(PADDING, 200)
            for y in range(10, 35)
        )
        assert has_title

    def test_sensor_rows_values_right_aligned(
        self,
    ) -> None:
        widgets = [
            {
                "type": "sensor_rows",
                "x": PADDING,
                "y": 10,
                "entities": ["sensor.living_room_temperature"],
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        has_dark_right = any(
            _pixel(img, x, y) < 128
            for x in range(300, 400)
            for y in range(10, 40)
        )
        assert has_dark_right

    def test_sensor_rows_missing_entity_skipped(
        self,
    ) -> None:
        widgets = [
            {
                "type": "sensor_rows",
                "x": PADDING,
                "y": 10,
                "entities": [
                    "sensor.nonexistent",
                    "sensor.humidity",
                ],
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        has_dark_first_row = any(
            _pixel(img, x, y) < 128
            for x in range(PADDING, 200)
            for y in range(10, 40)
        )
        assert has_dark_first_row

    def test_sensor_rows_empty_entities(self) -> None:
        widgets = [
            {
                "type": "sensor_rows",
                "x": PADDING,
                "y": 10,
                "entities": [],
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        all_white = all(
            _pixel(img, x, y) == 255
            for x in range(0, 400, 20)
            for y in range(0, 300, 20)
        )
        assert all_white


MOCK_BATTERY_STATES = {
    "sensor.kindle_battery": {
        "state": "75",
        "attributes": {
            "unit_of_measurement": "%",
            "friendly_name": "Kindle Battery",
        },
    },
}


class TestRenderBatteryBar:
    def _config(self, **overrides: object) -> dict[str, object]:
        base: dict[str, object] = {
            "width": 400,
            "height": 100,
            "states": MOCK_BATTERY_STATES,
        }
        base.update(overrides)
        return base

    def test_battery_bar_draws_fill(self) -> None:
        widgets = [
            {
                "type": "battery_bar",
                "x": PADDING,
                "y": 20,
                "entity": "sensor.kindle_battery",
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        has_dark_fill = any(
            _pixel(img, x, y) < 128
            for x in range(PADDING + 1, PADDING + 100)
            for y in range(21, 36)
        )
        assert has_dark_fill

    def test_battery_bar_missing_entity_is_noop(
        self,
    ) -> None:
        widgets = [
            {
                "type": "battery_bar",
                "x": PADDING,
                "y": 20,
                "entity": "sensor.nonexistent",
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        all_white = all(
            _pixel(img, x, y) == 255
            for x in range(0, 400, 20)
            for y in range(0, 100, 20)
        )
        assert all_white

    def test_battery_bar_non_numeric_is_noop(
        self,
    ) -> None:
        states = {
            "sensor.kindle_battery": {
                "state": "unavailable",
                "attributes": {},
            },
        }
        widgets = [
            {
                "type": "battery_bar",
                "x": PADDING,
                "y": 20,
                "entity": "sensor.kindle_battery",
            }
        ]
        result = render_dashboard(
            widgets,
            {"width": 400, "height": 100, "states": states},
        )

        img = _png_to_image(result)
        all_white = all(
            _pixel(img, x, y) == 255
            for x in range(0, 400, 20)
            for y in range(0, 100, 20)
        )
        assert all_white

    def test_battery_bar_custom_size(self) -> None:
        widgets = [
            {
                "type": "battery_bar",
                "x": PADDING,
                "y": 20,
                "entity": "sensor.kindle_battery",
                "width": 300,
                "height": 24,
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        has_dark_fill = any(
            _pixel(img, x, y) < 128
            for x in range(PADDING + 1, PADDING + 220)
            for y in range(21, 43)
        )
        assert has_dark_fill


MOCK_STATUS_ICON_STATES = {
    "binary_sensor.front_door": {
        "state": "on",
        "attributes": {
            "friendly_name": "Front Door",
            "device_class": "door",
        },
    },
    "binary_sensor.kitchen_window": {
        "state": "off",
        "attributes": {
            "friendly_name": "Kitchen Window",
            "device_class": "window",
        },
    },
    "binary_sensor.water_alarm": {
        "state": "on",
        "attributes": {
            "friendly_name": "Water Alarm",
            "device_class": "moisture",
        },
    },
    "binary_sensor.motion": {
        "state": "off",
        "attributes": {
            "friendly_name": "Motion",
            "device_class": "motion",
        },
    },
}


class TestRenderStatusIcons:
    def _config(self, **overrides: object) -> dict[str, object]:
        base: dict[str, object] = {
            "width": 500,
            "height": 200,
            "states": MOCK_STATUS_ICON_STATES,
        }
        base.update(overrides)
        return base

    def test_status_icons_draws_entities(self) -> None:
        widgets = [
            {
                "type": "status_icons",
                "x": PADDING,
                "y": 10,
                "entities": [
                    "binary_sensor.front_door",
                    "binary_sensor.kitchen_window",
                ],
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        has_content = any(
            _pixel(img, x, y) < 200
            for x in range(PADDING, 300)
            for y in range(10, 36)
        )
        assert has_content

    def test_status_icons_problem_fills_square(self) -> None:
        # front_door: state=on, device_class=door → problem → filled square
        widgets = [
            {
                "type": "status_icons",
                "x": PADDING,
                "y": 10,
                "entities": ["binary_sensor.front_door"],
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        has_black = any(
            _pixel(img, x, y) < 64
            for x in range(PADDING, PADDING + 13)
            for y in range(14, 27)
        )
        assert has_black

    def test_status_icons_ok_draws_outline(self) -> None:
        # kitchen_window: state=off → not a problem → outline only
        widgets = [
            {
                "type": "status_icons",
                "x": PADDING,
                "y": 10,
                "entities": ["binary_sensor.kitchen_window"],
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        # Interior of the outline square should NOT be solid black
        interior_black = all(
            _pixel(img, x, y) < 64
            for x in range(PADDING + 2, PADDING + 11)
            for y in range(16, 25)
        )
        assert not interior_black
        # But the outline itself should have some dark pixels
        has_outline = any(
            _pixel(img, x, y) < 200
            for x in range(PADDING, PADDING + 13)
            for y in range(14, 27)
        )
        assert has_outline

    def test_status_icons_with_title(self) -> None:
        widgets = [
            {
                "type": "status_icons",
                "x": PADDING,
                "y": 10,
                "title": "Doors",
                "entities": ["binary_sensor.front_door"],
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        has_title = any(
            _pixel(img, x, y) < 128
            for x in range(PADDING, 200)
            for y in range(10, 40)
        )
        assert has_title
        has_icon = any(
            _pixel(img, x, y) < 128
            for x in range(PADDING, 200)
            for y in range(40, 70)
        )
        assert has_icon

    def test_status_icons_missing_entity_skipped(self) -> None:
        widgets = [
            {
                "type": "status_icons",
                "x": PADDING,
                "y": 10,
                "entities": [
                    "binary_sensor.nonexistent",
                    "binary_sensor.kitchen_window",
                ],
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        has_content = any(
            _pixel(img, x, y) < 200
            for x in range(PADDING, 300)
            for y in range(10, 36)
        )
        assert has_content

    def test_status_icons_empty_entities_is_noop(self) -> None:
        widgets = [
            {
                "type": "status_icons",
                "x": PADDING,
                "y": 10,
                "entities": [],
            }
        ]
        result = render_dashboard(widgets, self._config())

        img = _png_to_image(result)
        all_white = all(
            _pixel(img, x, y) == 255
            for x in range(0, 500, 20)
            for y in range(0, 200, 20)
        )
        assert all_white

    def test_status_icons_wraps_to_next_row(self) -> None:
        # Narrow canvas forces wrapping after first entity
        widgets = [
            {
                "type": "status_icons",
                "x": PADDING,
                "y": 10,
                "entities": [
                    "binary_sensor.front_door",
                    "binary_sensor.kitchen_window",
                    "binary_sensor.water_alarm",
                    "binary_sensor.motion",
                ],
            }
        ]
        result = render_dashboard(
            widgets,
            {"width": 200, "height": 200, "states": MOCK_STATUS_ICON_STATES},
        )

        img = _png_to_image(result)
        has_second_row = any(
            _pixel(img, x, y) < 200
            for x in range(PADDING, 180)
            for y in range(36, 80)
        )
        assert has_second_row
