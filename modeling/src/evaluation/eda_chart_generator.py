"""Chart generation for the midterm EDA slide deck."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from html import escape
import math
from pathlib import Path

import numpy as np
import pandas as pd

from .eda_summary_builder import (
    NeighbourhoodPriceExtremes,
    build_accommodates_band_median_prices,
    build_median_price_by_city,
    build_median_price_by_city_and_period,
    build_median_price_by_room_type,
    build_neighbourhood_price_extremes,
    build_nightly_price_distribution,
    build_room_type_share,
    build_rows_by_city,
    build_rows_by_city_and_period,
)


OUTPUT_SUBDIRECTORY = Path("modeling") / "reports" / "eda" / "midterm_charts"

PRIMARY_COLOR = "#1F567D"
SECONDARY_COLOR = "#2A9D8F"
ACCENT_COLOR = "#F4A261"
WARNING_COLOR = "#E76F51"
NEUTRAL_COLOR = "#6C7A89"
GRID_COLOR = "#D7DEE6"
TEXT_COLOR = "#17324D"
BACKGROUND_COLOR = "#FFFFFF"
HEATMAP_LOW_COLOR = "#F3E79B"
HEATMAP_HIGH_COLOR = "#2C7BB6"
PERIOD_COLORS = ["#1F567D", "#2A9D8F", "#F4A261", "#E76F51"]

FIGURE_DIMENSIONS = {
    "default": (1100, 650),
    "wide": (1200, 680),
    "compact": (1100, 360),
}


@dataclass(frozen=True)
class ChartArtifact:
    """Metadata for a rendered chart asset."""

    chart_id: str
    title: str
    filename: str
    slide_hint: str
    relative_path: str


def _svg_document(width: int, height: int, title: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">'
        f"<title>{escape(title)}</title>"
        "<style>"
        "text { font-family: Arial, Helvetica, sans-serif; fill: #17324D; }"
        ".title { font-size: 28px; font-weight: 700; }"
        ".axis-label { font-size: 16px; font-weight: 600; }"
        ".tick { font-size: 13px; }"
        ".value { font-size: 12px; font-weight: 600; }"
        ".legend { font-size: 13px; }"
        "</style>"
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{BACKGROUND_COLOR}" />'
        f"{body}</svg>"
    )


def _svg_rect(x: float, y: float, width: float, height: float, *, fill: str, stroke: str = "none") -> str:
    return (
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{height:.2f}" '
        f'fill="{fill}" stroke="{stroke}" />'
    )


def _svg_line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    stroke: str,
    stroke_width: float = 1.0,
    dasharray: str | None = None,
) -> str:
    dash = f' stroke-dasharray="{dasharray}"' if dasharray else ""
    return (
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
        f'stroke="{stroke}" stroke-width="{stroke_width:.2f}"{dash} />'
    )


def _svg_text(
    x: float,
    y: float,
    text: str,
    *,
    css_class: str = "tick",
    anchor: str = "middle",
    fill: str = TEXT_COLOR,
    rotate: float | None = None,
) -> str:
    transform = f' transform="rotate({rotate:.2f} {x:.2f} {y:.2f})"' if rotate is not None else ""
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" fill="{fill}" '
        f'class="{css_class}"{transform}>{escape(text)}</text>'
    )


def _write_svg(path: Path, svg: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")


def _linear_scale(value: float, domain_min: float, domain_max: float, range_min: float, range_max: float) -> float:
    if domain_max <= domain_min:
        return range_min
    ratio = (value - domain_min) / (domain_max - domain_min)
    return range_min + ratio * (range_max - range_min)


def _tick_values(max_value: float, tick_count: int = 5) -> list[float]:
    if max_value <= 0:
        return [0.0]
    return list(np.linspace(0, max_value, num=tick_count))


def _nice_axis_max(max_value: float, *, headroom: float = 0.05) -> float:
    if max_value <= 0:
        return 1.0
    padded = max_value * (1 + headroom)
    magnitude = 10 ** math.floor(math.log10(padded))
    normalized = padded / magnitude
    if normalized <= 1:
        nice = 1
    elif normalized <= 2:
        nice = 2
    elif normalized <= 2.5:
        nice = 2.5
    elif normalized <= 5:
        nice = 5
    else:
        nice = 10
    return nice * magnitude


def _format_int(value: float) -> str:
    return f"{int(round(value)):,}"


def _format_currency(value: float) -> str:
    return f"EUR {value:,.0f}"


def _wrap_neighbourhood_label(label: str) -> str:
    city_name, neighbourhood_name = label.split("\n", maxsplit=1)
    return f"{city_name} / {neighbourhood_name}"


def _interpolate_color(value: float, min_value: float, max_value: float, *, low: str, high: str) -> str:
    if max_value <= min_value:
        return high
    value = min(max(value, min_value), max_value)
    start = tuple(int(low[index : index + 2], 16) for index in (1, 3, 5))
    end = tuple(int(high[index : index + 2], 16) for index in (1, 3, 5))
    ratio = (value - min_value) / (max_value - min_value)
    blended = tuple(int(start[channel] + ratio * (end[channel] - start[channel])) for channel in range(3))
    return "#" + "".join(f"{channel:02X}" for channel in blended)


def _render_vertical_bar_chart(
    data: pd.Series,
    *,
    title: str,
    y_axis_label: str,
    destination: Path,
    fill: str,
    chart_id: str,
    slide_hint: str,
    value_formatter,
    tick_formatter,
) -> ChartArtifact:
    width, height = FIGURE_DIMENSIONS["default"]
    left, right, top, bottom = 90, 50, 100, 120
    plot_width = width - left - right
    plot_height = height - top - bottom
    max_value = _nice_axis_max(float(data.max())) if len(data) else 1.0
    ticks = _tick_values(max_value)

    body_parts = [
        _svg_text(width / 2, 45, title, css_class="title"),
        _svg_text(28, top + plot_height / 2, y_axis_label, css_class="axis-label", rotate=-90),
    ]
    for tick in ticks:
        y = top + plot_height - _linear_scale(tick, 0, max_value, 0, plot_height)
        body_parts.append(_svg_line(left, y, left + plot_width, y, stroke=GRID_COLOR, dasharray="4 4"))
        body_parts.append(_svg_text(left - 12, y + 4, tick_formatter(tick), anchor="end"))

    body_parts.append(_svg_line(left, top, left, top + plot_height, stroke=TEXT_COLOR, stroke_width=1.5))
    body_parts.append(
        _svg_line(left, top + plot_height, left + plot_width, top + plot_height, stroke=TEXT_COLOR, stroke_width=1.5)
    )

    category_width = plot_width / max(len(data), 1)
    bar_width = category_width * 0.62
    for index, (label, value) in enumerate(data.items()):
        bar_x = left + index * category_width + (category_width - bar_width) / 2
        bar_height = _linear_scale(float(value), 0, max_value, 0, plot_height)
        bar_y = top + plot_height - bar_height
        body_parts.append(_svg_rect(bar_x, bar_y, bar_width, bar_height, fill=fill))
        body_parts.append(_svg_text(bar_x + bar_width / 2, bar_y - 8, value_formatter(float(value)), css_class="value"))
        body_parts.append(_svg_text(bar_x + bar_width / 2, top + plot_height + 28, label))

    _write_svg(destination, _svg_document(width, height, title, "".join(body_parts)))
    return ChartArtifact(
        chart_id=chart_id,
        title=title,
        filename=destination.name,
        slide_hint=slide_hint,
        relative_path="",
    )


def _render_horizontal_bar_chart(
    data: pd.Series,
    *,
    title: str,
    x_axis_label: str,
    destination: Path,
    colors: list[str],
    chart_id: str,
    slide_hint: str,
    value_formatter,
    tick_formatter,
    left_margin: int = 180,
) -> ChartArtifact:
    width, height = FIGURE_DIMENSIONS["default"]
    left, right, top, bottom = left_margin, 60, 100, 80
    plot_width = width - left - right
    plot_height = height - top - bottom
    if len(data) and data.max() <= 100:
        max_value = 100.0
    else:
        max_value = _nice_axis_max(float(data.max())) if len(data) else 1.0
    ticks = _tick_values(max_value)

    body_parts = [
        _svg_text(width / 2, 45, title, css_class="title"),
        _svg_text(left + plot_width / 2, height - 18, x_axis_label, css_class="axis-label"),
    ]
    for tick in ticks:
        x = left + _linear_scale(tick, 0, max_value, 0, plot_width)
        body_parts.append(_svg_line(x, top, x, top + plot_height, stroke=GRID_COLOR, dasharray="4 4"))
        body_parts.append(_svg_text(x, top + plot_height + 24, tick_formatter(tick)))

    body_parts.append(_svg_line(left, top, left, top + plot_height, stroke=TEXT_COLOR, stroke_width=1.5))
    body_parts.append(
        _svg_line(left, top + plot_height, left + plot_width, top + plot_height, stroke=TEXT_COLOR, stroke_width=1.5)
    )

    row_height = plot_height / max(len(data), 1)
    bar_height = row_height * 0.58
    for index, (label, value) in enumerate(data.items()):
        bar_y = top + index * row_height + (row_height - bar_height) / 2
        bar_width = _linear_scale(float(value), 0, max_value, 0, plot_width)
        color = colors[index % len(colors)]
        body_parts.append(_svg_rect(left, bar_y, bar_width, bar_height, fill=color))
        body_parts.append(_svg_text(left - 12, bar_y + bar_height / 2 + 4, label, anchor="end"))
        body_parts.append(_svg_text(left + bar_width + 8, bar_y + bar_height / 2 + 4, value_formatter(float(value)), anchor="start", css_class="value"))

    _write_svg(destination, _svg_document(width, height, title, "".join(body_parts)))
    return ChartArtifact(
        chart_id=chart_id,
        title=title,
        filename=destination.name,
        slide_hint=slide_hint,
        relative_path="",
    )


def _render_rows_by_city_chart(data: pd.Series, destination: Path) -> ChartArtifact:
    return _render_vertical_bar_chart(
        data,
        title="Listing Snapshot Coverage by City",
        y_axis_label="Listing snapshot rows",
        destination=destination,
        fill=PRIMARY_COLOR,
        chart_id="rows_by_city",
        slide_hint="EDA Part 1",
        value_formatter=_format_int,
        tick_formatter=_format_int,
    )


def _render_rows_by_city_and_period_chart(data: pd.DataFrame, destination: Path) -> ChartArtifact:
    width, height = FIGURE_DIMENSIONS["wide"]
    left, right, top, bottom = 90, 50, 100, 130
    plot_width = width - left - right
    plot_height = height - top - bottom
    max_value = _nice_axis_max(float(data.to_numpy().max())) if not data.empty else 1.0
    ticks = _tick_values(max_value)
    group_width = plot_width / max(len(data.index), 1)
    inner_width = group_width * 0.8
    bar_width = inner_width / max(len(data.columns), 1)

    body_parts = [
        _svg_text(width / 2, 45, "Listing Snapshot Coverage by City and Period", css_class="title"),
        _svg_text(28, top + plot_height / 2, "Listing snapshot rows", css_class="axis-label", rotate=-90),
    ]
    for tick in ticks:
        y = top + plot_height - _linear_scale(tick, 0, max_value, 0, plot_height)
        body_parts.append(_svg_line(left, y, left + plot_width, y, stroke=GRID_COLOR, dasharray="4 4"))
        body_parts.append(_svg_text(left - 12, y + 4, _format_int(tick), anchor="end"))

    body_parts.append(_svg_line(left, top, left, top + plot_height, stroke=TEXT_COLOR, stroke_width=1.5))
    body_parts.append(
        _svg_line(left, top + plot_height, left + plot_width, top + plot_height, stroke=TEXT_COLOR, stroke_width=1.5)
    )

    legend_x = width - right - 240
    legend_y = 62
    for index, period in enumerate(data.columns):
        legend_item_x = legend_x + (index % 2) * 120
        legend_item_y = legend_y + (index // 2) * 22
        body_parts.append(_svg_rect(legend_item_x, legend_item_y, 14, 14, fill=PERIOD_COLORS[index % len(PERIOD_COLORS)]))
        body_parts.append(_svg_text(legend_item_x + 22, legend_item_y + 12, period, anchor="start", css_class="legend"))

    for city_index, city_name in enumerate(data.index):
        group_start = left + city_index * group_width + (group_width - inner_width) / 2
        for period_index, period in enumerate(data.columns):
            value = float(data.loc[city_name, period])
            bar_height = _linear_scale(value, 0, max_value, 0, plot_height)
            bar_x = group_start + period_index * bar_width
            bar_y = top + plot_height - bar_height
            body_parts.append(_svg_rect(bar_x, bar_y, bar_width - 3, bar_height, fill=PERIOD_COLORS[period_index % len(PERIOD_COLORS)]))
        body_parts.append(_svg_text(group_start + inner_width / 2, top + plot_height + 28, city_name))

    _write_svg(destination, _svg_document(width, height, "Listing Snapshot Coverage by City and Period", "".join(body_parts)))
    return ChartArtifact(
        chart_id="rows_by_city_and_period",
        title="Listing Snapshot Coverage by City and Period",
        filename=destination.name,
        slide_hint="EDA Part 1",
        relative_path="",
    )


def _render_room_type_share_chart(data: pd.Series, destination: Path) -> ChartArtifact:
    return _render_horizontal_bar_chart(
        data.mul(100),
        title="Room Type Composition",
        x_axis_label="Share of listing snapshot rows (%)",
        destination=destination,
        colors=[PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, WARNING_COLOR],
        chart_id="room_type_share",
        slide_hint="EDA Part 1",
        value_formatter=lambda value: f"{value:.1f}%",
        tick_formatter=lambda value: f"{value:.0f}%",
        left_margin=180,
    )


def _render_nightly_price_histogram(data: pd.Series, destination: Path) -> ChartArtifact:
    width, height = FIGURE_DIMENSIONS["default"]
    left, right, top, bottom = 90, 50, 100, 90
    plot_width = width - left - right
    plot_height = height - top - bottom
    clipped = data.clip(upper=float(data.quantile(0.99)))
    counts, bin_edges = np.histogram(clipped.to_numpy(dtype=float), bins=40)
    max_count = float(counts.max()) * 1.15 if len(counts) else 1.0
    ticks = _tick_values(max_count)
    max_price = float(bin_edges[-1]) if len(bin_edges) else 1.0

    body_parts = [
        _svg_text(width / 2, 45, "Nightly Price Distribution (Clipped at 99th Percentile)", css_class="title"),
        _svg_text(28, top + plot_height / 2, "Listing snapshot rows", css_class="axis-label", rotate=-90),
        _svg_text(left + plot_width / 2, height - 18, "Nightly price", css_class="axis-label"),
    ]
    for tick in ticks:
        y = top + plot_height - _linear_scale(tick, 0, max_count, 0, plot_height)
        body_parts.append(_svg_line(left, y, left + plot_width, y, stroke=GRID_COLOR, dasharray="4 4"))
        body_parts.append(_svg_text(left - 12, y + 4, _format_int(tick), anchor="end"))

    x_ticks = _tick_values(max_price)
    for tick in x_ticks:
        x = left + _linear_scale(tick, 0, max_price, 0, plot_width)
        body_parts.append(_svg_text(x, top + plot_height + 24, _format_currency(tick)))

    body_parts.append(_svg_line(left, top, left, top + plot_height, stroke=TEXT_COLOR, stroke_width=1.5))
    body_parts.append(
        _svg_line(left, top + plot_height, left + plot_width, top + plot_height, stroke=TEXT_COLOR, stroke_width=1.5)
    )

    bin_width = plot_width / max(len(counts), 1)
    for index, count in enumerate(counts):
        bar_height = _linear_scale(float(count), 0, max_count, 0, plot_height)
        bar_x = left + index * bin_width
        bar_y = top + plot_height - bar_height
        body_parts.append(_svg_rect(bar_x, bar_y, max(bin_width - 1, 1), bar_height, fill=PRIMARY_COLOR))

    _write_svg(destination, _svg_document(width, height, "Nightly Price Distribution (Clipped at 99th Percentile)", "".join(body_parts)))
    return ChartArtifact(
        chart_id="nightly_price_histogram",
        title="Nightly Price Distribution (Clipped at 99th Percentile)",
        filename=destination.name,
        slide_hint="EDA Part 2",
        relative_path="",
    )


def _render_nightly_price_boxplot(data: pd.Series, destination: Path) -> ChartArtifact:
    width, height = FIGURE_DIMENSIONS["compact"]
    left, right, top, bottom = 90, 50, 100, 70
    plot_width = width - left - right
    plot_height = height - top - bottom
    values = data.to_numpy(dtype=float)
    q1, median, q3 = np.quantile(values, [0.25, 0.5, 0.75])
    iqr = q3 - q1
    lower_whisker = max(values.min(), q1 - 1.5 * iqr)
    upper_whisker = min(values.max(), q3 + 1.5 * iqr)
    max_price = 400.0 if len(values) else 1.0
    x_ticks = _tick_values(max_price)
    center_y = top + plot_height / 2
    box_height = 46

    body_parts = [
        _svg_text(width / 2, 45, "Nightly Price Boxplot", css_class="title"),
        _svg_text(left + plot_width / 2, height - 18, "Nightly price", css_class="axis-label"),
        _svg_text(
            width - 50,
            72,
            "Axis capped at EUR 400 to keep the IQR readable",
            anchor="end",
            css_class="legend",
        ),
    ]
    for tick in x_ticks:
        x = left + _linear_scale(tick, 0, max_price, 0, plot_width)
        body_parts.append(_svg_line(x, top, x, top + plot_height, stroke=GRID_COLOR, dasharray="4 4"))
        body_parts.append(_svg_text(x, top + plot_height + 24, _format_currency(tick)))

    body_parts.append(
        _svg_line(left, top + plot_height, left + plot_width, top + plot_height, stroke=TEXT_COLOR, stroke_width=1.5)
    )

    q1_x = left + _linear_scale(float(q1), 0, max_price, 0, plot_width)
    median_x = left + _linear_scale(float(median), 0, max_price, 0, plot_width)
    q3_x = left + _linear_scale(float(q3), 0, max_price, 0, plot_width)
    lower_x = left + _linear_scale(float(lower_whisker), 0, max_price, 0, plot_width)
    upper_x = left + _linear_scale(float(upper_whisker), 0, max_price, 0, plot_width)

    body_parts.append(_svg_line(lower_x, center_y, q1_x, center_y, stroke=PRIMARY_COLOR, stroke_width=2))
    body_parts.append(_svg_line(q3_x, center_y, upper_x, center_y, stroke=PRIMARY_COLOR, stroke_width=2))
    body_parts.append(_svg_line(lower_x, center_y - 14, lower_x, center_y + 14, stroke=PRIMARY_COLOR, stroke_width=2))
    body_parts.append(_svg_line(upper_x, center_y - 14, upper_x, center_y + 14, stroke=PRIMARY_COLOR, stroke_width=2))
    body_parts.append(_svg_rect(q1_x, center_y - box_height / 2, q3_x - q1_x, box_height, fill=SECONDARY_COLOR, stroke=PRIMARY_COLOR))
    body_parts.append(_svg_line(median_x, center_y - box_height / 2, median_x, center_y + box_height / 2, stroke=WARNING_COLOR, stroke_width=3))
    body_parts.append(_svg_text(q1_x, center_y - 34, "Q1", css_class="value"))
    body_parts.append(_svg_text(median_x, center_y - 34, "Median", css_class="value"))
    body_parts.append(_svg_text(q3_x, center_y - 34, "Q3", css_class="value"))

    _write_svg(destination, _svg_document(width, height, "Nightly Price Boxplot", "".join(body_parts)))
    return ChartArtifact(
        chart_id="nightly_price_boxplot",
        title="Nightly Price Boxplot",
        filename=destination.name,
        slide_hint="EDA Part 2",
        relative_path="",
    )


def _render_median_price_by_city_chart(data: pd.Series, destination: Path) -> ChartArtifact:
    return _render_vertical_bar_chart(
        data,
        title="Median Nightly Price by City",
        y_axis_label="Median nightly price",
        destination=destination,
        fill=SECONDARY_COLOR,
        chart_id="median_price_by_city",
        slide_hint="EDA Part 3",
        value_formatter=_format_currency,
        tick_formatter=_format_currency,
    )


def _render_city_period_heatmap(data: pd.DataFrame, destination: Path) -> ChartArtifact:
    width, height = 1080, 520
    left, right, top, bottom = 180, 110, 110, 90
    plot_width = width - left - right
    plot_height = height - top - bottom
    cell_width = plot_width / max(len(data.columns), 1)
    cell_height = plot_height / max(len(data.index), 1)
    min_value = float(np.nanmin(data.to_numpy(dtype=float))) if not data.empty else 0.0
    max_value = float(np.nanmax(data.to_numpy(dtype=float))) if not data.empty else 1.0

    body_parts = [_svg_text(width / 2, 45, "Median Nightly Price by City and Period", css_class="title")]
    for row_index, city_name in enumerate(data.index):
        body_parts.append(_svg_text(left - 12, top + row_index * cell_height + cell_height / 2 + 4, city_name, anchor="end"))
    for column_index, period in enumerate(data.columns):
        body_parts.append(
            _svg_text(
                left + column_index * cell_width + cell_width / 2,
                top - 14,
                period,
                rotate=-24,
            )
        )

    for row_index, city_name in enumerate(data.index):
        for column_index, period in enumerate(data.columns):
            value = data.loc[city_name, period]
            x = left + column_index * cell_width
            y = top + row_index * cell_height
            if pd.isna(value):
                fill = "#F7F9FB"
                label = "NA"
            else:
                fill = _interpolate_color(float(value), min_value, max_value, low=HEATMAP_LOW_COLOR, high=HEATMAP_HIGH_COLOR)
                label = f"{float(value):.0f}"
            body_parts.append(_svg_rect(x, y, cell_width - 2, cell_height - 2, fill=fill))
            body_parts.append(_svg_text(x + cell_width / 2, y + cell_height / 2 + 5, label, css_class="value"))

    legend_x = width - right + 30
    legend_y = top
    legend_height = plot_height
    for index in range(12):
        step_value = min_value + (max_value - min_value) * (index / 11 if max_value > min_value else 0)
        step_y = legend_y + legend_height - (index + 1) * legend_height / 12
        fill = _interpolate_color(step_value, min_value, max_value, low=HEATMAP_LOW_COLOR, high=HEATMAP_HIGH_COLOR)
        body_parts.append(_svg_rect(legend_x, step_y, 20, legend_height / 12, fill=fill))
    body_parts.append(_svg_text(legend_x + 10, legend_y - 12, "Price", css_class="legend"))
    body_parts.append(_svg_text(legend_x + 28, legend_y + 4, _format_currency(max_value), anchor="start"))
    body_parts.append(_svg_text(legend_x + 28, legend_y + legend_height, _format_currency(min_value), anchor="start"))

    _write_svg(destination, _svg_document(width, height, "Median Nightly Price by City and Period", "".join(body_parts)))
    return ChartArtifact(
        chart_id="median_price_heatmap_city_period",
        title="Median Nightly Price by City and Period",
        filename=destination.name,
        slide_hint="EDA Part 3",
        relative_path="",
    )


def _render_median_price_by_room_type_chart(data: pd.Series, destination: Path) -> ChartArtifact:
    return _render_vertical_bar_chart(
        data,
        title="Median Nightly Price by Room Type",
        y_axis_label="Median nightly price",
        destination=destination,
        fill=ACCENT_COLOR,
        chart_id="median_price_by_room_type",
        slide_hint="EDA Part 4",
        value_formatter=_format_currency,
        tick_formatter=_format_currency,
    )


def _render_median_price_by_accommodates_band_chart(data: pd.Series, destination: Path) -> ChartArtifact:
    return _render_vertical_bar_chart(
        data,
        title="Median Nightly Price by Guest Capacity Band",
        y_axis_label="Median nightly price",
        destination=destination,
        fill=PRIMARY_COLOR,
        chart_id="median_price_by_accommodates_band",
        slide_hint="EDA Part 4",
        value_formatter=_format_currency,
        tick_formatter=_format_currency,
    )


def _render_neighbourhood_price_extremes_chart(data: NeighbourhoodPriceExtremes, destination: Path) -> ChartArtifact:
    combined = data.combined().sort_values("median_nightly_price")
    series = pd.Series(
        combined["median_nightly_price"].to_numpy(),
        index=[_wrap_neighbourhood_label(label) for label in combined["label"]],
    )
    colors = [NEUTRAL_COLOR if segment == "Lower priced" else WARNING_COLOR for segment in combined["segment"]]
    return _render_horizontal_bar_chart(
        series,
        title="Selected High-Price and Lower-Price Neighbourhoods",
        x_axis_label="Median nightly price",
        destination=destination,
        colors=colors,
        chart_id="neighbourhood_price_extremes",
        slide_hint="EDA Part 4",
        value_formatter=_format_currency,
        tick_formatter=_format_currency,
        left_margin=280,
    )


def _write_manifest(destination: Path, artifacts: list[ChartArtifact]) -> Path:
    payload = {
        "chart_group": "midterm_eda_slides",
        "charts": [asdict(artifact) for artifact in artifacts],
    }
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return destination


def generate_midterm_eda_charts(
    listing_snapshot: pd.DataFrame,
    output_root: Path,
    *,
    min_neighbourhood_rows: int = 200,
    top_n: int = 5,
    bottom_n: int = 5,
) -> list[Path]:
    """Generate all SVG charts required for the midterm EDA slides."""

    output_directory = output_root / OUTPUT_SUBDIRECTORY
    output_directory.mkdir(parents=True, exist_ok=True)

    rows_by_city = build_rows_by_city(listing_snapshot)
    rows_by_city_and_period = build_rows_by_city_and_period(listing_snapshot)
    room_type_share = build_room_type_share(listing_snapshot)
    nightly_price_distribution = build_nightly_price_distribution(listing_snapshot)
    median_price_by_city = build_median_price_by_city(listing_snapshot)
    median_price_by_city_and_period = build_median_price_by_city_and_period(listing_snapshot)
    median_price_by_room_type = build_median_price_by_room_type(listing_snapshot)
    median_price_by_accommodates_band = build_accommodates_band_median_prices(listing_snapshot)
    neighbourhood_extremes = build_neighbourhood_price_extremes(
        listing_snapshot,
        min_listing_rows=min_neighbourhood_rows,
        top_n=top_n,
        bottom_n=bottom_n,
    )

    artifacts = [
        _render_rows_by_city_chart(rows_by_city, output_directory / "listing_rows_by_city.svg"),
        _render_rows_by_city_and_period_chart(
            rows_by_city_and_period,
            output_directory / "listing_rows_by_city_and_period.svg",
        ),
        _render_room_type_share_chart(room_type_share, output_directory / "room_type_share.svg"),
        _render_nightly_price_histogram(
            nightly_price_distribution,
            output_directory / "nightly_price_histogram.svg",
        ),
        _render_nightly_price_boxplot(
            nightly_price_distribution,
            output_directory / "nightly_price_boxplot.svg",
        ),
        _render_median_price_by_city_chart(
            median_price_by_city,
            output_directory / "median_price_by_city.svg",
        ),
        _render_city_period_heatmap(
            median_price_by_city_and_period,
            output_directory / "median_price_heatmap_city_period.svg",
        ),
        _render_median_price_by_room_type_chart(
            median_price_by_room_type,
            output_directory / "median_price_by_room_type.svg",
        ),
        _render_median_price_by_accommodates_band_chart(
            median_price_by_accommodates_band,
            output_directory / "median_price_by_accommodates_band.svg",
        ),
        _render_neighbourhood_price_extremes_chart(
            neighbourhood_extremes,
            output_directory / "neighbourhood_price_extremes.svg",
        ),
    ]

    written_paths = [output_directory / artifact.filename for artifact in artifacts]
    for index, artifact in enumerate(artifacts):
        artifacts[index] = ChartArtifact(
            chart_id=artifact.chart_id,
            title=artifact.title,
            filename=artifact.filename,
            slide_hint=artifact.slide_hint,
            relative_path=str((output_directory / artifact.filename).relative_to(output_root)),
        )

    manifest_path = _write_manifest(output_directory / "midterm_eda_chart_manifest.json", artifacts)
    return [*written_paths, manifest_path]
