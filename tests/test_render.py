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
