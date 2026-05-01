from __future__ import annotations

import functools
import io
import math
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .const import (
    COLOR_BLACK,
    COLOR_GRAY,
    COLOR_LIGHT_GRAY,
    COLOR_WHITE,
    PADDING,
    Align,
    WidgetType,
)

type Widget = dict[str, Any]
type DisplayConfig = dict[str, Any]
type RendererFn = Callable[[ImageDraw.ImageDraw, Widget, DisplayConfig], None]

_FONTS_DIR = Path(__file__).parent / "fonts"


@functools.cache
def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    ttf_path = _FONTS_DIR / "DejaVuSans.ttf"
    if ttf_path.exists():
        return ImageFont.truetype(str(ttf_path), size)
    return ImageFont.load_default(size)


def render_text(
    draw: ImageDraw.ImageDraw,
    widget: Widget,
    config: DisplayConfig,
) -> None:
    x = widget.get("x", PADDING)
    y = widget.get("y", 0)
    text = widget.get("text", "")
    font_size = widget.get("font_size", 22)
    color = widget.get("color", COLOR_BLACK)
    align = widget.get("align", Align.LEFT)

    font = _load_font(font_size)
    width = config["width"]

    if align in (Align.RIGHT, Align.CENTER):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        if align == Align.RIGHT:
            x = width - PADDING - text_w
        else:
            x = (width - text_w) // 2

    draw.text((x, y), text, fill=color, font=font)


def render_line(
    draw: ImageDraw.ImageDraw,
    widget: Widget,
    _config: DisplayConfig,
) -> None:
    x = widget.get("x", PADDING)
    y = widget.get("y", 0)
    x2 = widget.get("x2", x)
    y2 = widget.get("y2", y)
    color = widget.get("color", COLOR_LIGHT_GRAY)
    width = widget.get("width", 1)
    draw.line([(x, y), (x2, y2)], fill=color, width=width)


def render_separator(
    draw: ImageDraw.ImageDraw,
    widget: Widget,
    config: DisplayConfig,
) -> None:
    y = widget.get("y", 0)
    color = widget.get("color", COLOR_LIGHT_GRAY)
    x0 = widget.get("x", PADDING)
    x1 = config["width"] - PADDING
    draw.line([(x0, y), (x1, y)], fill=color, width=1)


_DAY_ABBREV = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _draw_weather_icon(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    radius: int,
    condition: str,
) -> None:
    if condition == "sunny":
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline=COLOR_BLACK,
            width=2,
        )
        ray_len = radius + 8
        for angle_deg in range(0, 360, 45):
            rad = math.radians(angle_deg)
            x0 = cx + int((radius + 3) * math.cos(rad))
            y0 = cy + int((radius + 3) * math.sin(rad))
            x1 = cx + int(ray_len * math.cos(rad))
            y1 = cy + int(ray_len * math.sin(rad))
            draw.line(
                [(x0, y0), (x1, y1)],
                fill=COLOR_BLACK,
                width=2,
            )
    elif condition in ("cloudy", "partlycloudy"):
        draw.ellipse(
            [cx - 18, cy - 8, cx + 6, cy + 12],
            fill=COLOR_GRAY,
            outline=COLOR_BLACK,
        )
        draw.ellipse(
            [cx - 8, cy - 16, cx + 16, cy + 4],
            fill=COLOR_GRAY,
            outline=COLOR_BLACK,
        )
        draw.ellipse(
            [cx + 2, cy - 6, cx + 22, cy + 14],
            fill=COLOR_GRAY,
            outline=COLOR_BLACK,
        )
        draw.rectangle(
            [cx - 16, cy + 2, cx + 20, cy + 12],
            fill=COLOR_GRAY,
        )
        draw.line([(cx - 16, cy + 12), (cx + 20, cy + 12)], fill=COLOR_BLACK, width=1)
        if condition == "partlycloudy":
            draw.ellipse(
                [cx + 10, cy - 22, cx + 26, cy - 6],
                outline=COLOR_BLACK,
                width=2,
            )
    elif condition == "rainy":
        draw.ellipse(
            [cx - 16, cy - 12, cx + 4, cy + 4],
            fill=COLOR_GRAY,
            outline=COLOR_BLACK,
        )
        draw.ellipse(
            [cx - 6, cy - 18, cx + 14, cy - 2],
            fill=COLOR_GRAY,
            outline=COLOR_BLACK,
        )
        draw.rectangle(
            [cx - 14, cy - 2, cx + 12, cy + 4],
            fill=COLOR_GRAY,
        )
        draw.line([(cx - 14, cy + 4), (cx + 12, cy + 4)], fill=COLOR_BLACK, width=1)
        for dx in [-8, 0, 8]:
            draw.line(
                [(cx + dx, cy + 8), (cx + dx - 3, cy + 18)],
                fill=COLOR_BLACK,
                width=2,
            )
    else:
        font = _load_font(radius)
        bbox = draw.textbbox((0, 0), "?", font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((cx - tw // 2, cy - th // 2), "?", fill=COLOR_BLACK, font=font)


def render_weather(
    draw: ImageDraw.ImageDraw,
    widget: Widget,
    config: DisplayConfig,
) -> None:
    entity_id = widget.get("entity", "")
    state = config.get("states", {}).get(entity_id)
    if state is None:
        return

    x = widget.get("x", PADDING)
    y = widget.get("y", 0)
    forecast_days = widget.get("forecast_days", 3)

    condition = state.get("state", "")
    attrs = state.get("attributes", {})
    temp = attrs.get("temperature", "--")
    humidity = attrs.get("humidity", "--")
    wind = attrs.get("wind_speed", "--")

    font_xl = _load_font(48)
    font_md = _load_font(22)
    font_sm = _load_font(16)

    icon_cx = x + 45
    icon_cy = y + 45
    _draw_weather_icon(draw, icon_cx, icon_cy, 20, condition)

    draw.text(
        (x + 100, y),
        f"{temp}°C",
        fill=COLOR_BLACK,
        font=font_xl,
    )
    draw.text(
        (x + 100, y + 54),
        condition.replace("_", " ").title(),
        fill=COLOR_GRAY,
        font=font_md,
    )

    width = config["width"]
    draw.text(
        (width - PADDING - 120, y + 8),
        f"{humidity}%",
        fill=COLOR_BLACK,
        font=font_md,
    )
    draw.text(
        (width - PADDING - 120, y + 38),
        f"{wind} km/h",
        fill=COLOR_BLACK,
        font=font_md,
    )

    forecast = attrs.get("forecast", [])
    if not forecast or forecast_days <= 0:
        return

    col_width = (width - x - PADDING) // forecast_days
    forecast_y = y + 100

    draw.line(
        [(x, forecast_y - 4), (width - PADDING, forecast_y - 4)],
        fill=COLOR_LIGHT_GRAY,
        width=1,
    )

    for i, day in enumerate(forecast[:forecast_days]):
        cx = x + col_width * i + col_width // 2
        dt_str = day.get("datetime")
        day_label = _DAY_ABBREV[datetime.fromisoformat(dt_str).weekday()] if dt_str else ""
        bbox = draw.textbbox((0, 0), day_label, font=font_sm)
        text_w = bbox[2] - bbox[0]
        draw.text(
            (cx - text_w // 2, forecast_y),
            day_label,
            fill=COLOR_GRAY,
            font=font_sm,
        )
        _draw_weather_icon(
            draw, cx, forecast_y + 38, 14, day.get("condition", "")
        )
        hi = day.get("temperature", "")
        lo = day.get("templow", "")
        hi_lo = f"{hi}° / {lo}°"
        bbox = draw.textbbox((0, 0), hi_lo, font=font_sm)
        text_w = bbox[2] - bbox[0]
        draw.text(
            (cx - text_w // 2, forecast_y + 60),
            hi_lo,
            fill=COLOR_BLACK,
            font=font_sm,
        )


_RENDERERS: dict[WidgetType, RendererFn] = {
    WidgetType.TEXT: render_text,
    WidgetType.LINE: render_line,
    WidgetType.SEPARATOR: render_separator,
    WidgetType.WEATHER: render_weather,
}


def render_dashboard(
    widget_list: list[Widget],
    config: DisplayConfig,
) -> bytes:
    config = {"width": 600, "height": 800, **config}
    w = config["width"]
    h = config["height"]
    img = Image.new("L", (w, h), COLOR_WHITE)
    draw = ImageDraw.Draw(img)

    for widget in widget_list:
        widget_type = widget.get("type")
        if widget_type is None:
            continue
        renderer = _RENDERERS.get(widget_type)
        if renderer is not None:
            renderer(draw, widget, config)

    rotation = config.get("rotation", 0)
    if rotation:
        img = img.rotate(rotation, expand=True)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()
