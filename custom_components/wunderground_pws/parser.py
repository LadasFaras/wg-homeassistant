"""Pure-python parser for the Wunderground PWS dashboard HTML (no HA imports)."""
from __future__ import annotations

import re
from typing import Any

# <xxx-widget-view data-a="1" data-b="2" ...>  (quotes-aware so a '>' inside style="" is fine)
_WIDGET_RE = re.compile(r"<([a-z0-9]+(?:-[a-z0-9]+)*-widget-view)\b((?:[^>\"']|\"[^\"]*\"|'[^']*')*)>", re.I)
_ATTR_RE = re.compile(r"data-([\w-]+)=\"([^\"]*)\"")
_STATUS_RE = re.compile(r'id="pws-status-text"[^>]*>\s*([^<]*?)\s*<', re.I)
_TITLE_RE = re.compile(r"<title[^>]*>\s*([^<]*?)\s*</title>", re.I)

# key -> (widget tag, data attribute)
FIELDS: dict[str, tuple[str, str]] = {
    "temperature": ("temp-widget-view", "temp"),
    "feels_like": ("temp-widget-view", "feels-like"),
    "humidity": ("humidity-widget-view", "humidity"),
    "dew_point": ("humidity-widget-view", "dew-point"),
    "wind_speed": ("wind-widget-view", "wind-speed"),
    "wind_gust": ("wind-widget-view", "wind-gust"),
    "wind_direction": ("wind-widget-view", "wind-dir"),
    "precip_rate": ("rain-widget-view", "precip-rate"),
    "precip_total": ("rain-widget-view", "precip-total"),
    "pressure": ("pressure-widget-view", "pressure"),
    "uv_index": ("uv-widget-view", "uv"),
    "solar_radiation": ("solar-radiation-widget-view", "solar-radiation"),
}


def _to_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip()
    if value in ("", "-", "--", "N/A", "null", "None"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_dashboard(html: str) -> dict[str, Any]:
    """Return {"values": {key: float|None}, "unit": "m|e|h", "status": str|None, "title": str|None}.

    Raises ValueError when the page contains no recognizable widgets.
    """
    widgets: dict[str, dict[str, str]] = {}
    for match in _WIDGET_RE.finditer(html):
        tag = match.group(1).lower()
        widgets[tag] = dict(_ATTR_RE.findall(match.group(2)))

    if not widgets:
        raise ValueError("No *-widget-view elements found (station missing or page layout changed)")

    values: dict[str, float | None] = {}
    for key, (tag, attr) in FIELDS.items():
        values[key] = _to_float(widgets.get(tag, {}).get(attr))

    if all(v is None for v in values.values()):
        raise ValueError("Widgets found but they contain no values")

    unit = "m"
    for attrs in widgets.values():
        if attrs.get("unit"):
            unit = attrs["unit"]
            break

    status_match = _STATUS_RE.search(html)
    title_match = _TITLE_RE.search(html)
    return {
        "values": values,
        "unit": unit,
        "status": status_match.group(1) if status_match else None,
        "title": title_match.group(1) if title_match else None,
    }
