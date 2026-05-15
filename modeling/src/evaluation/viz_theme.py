"""Shared visualization theme for Airbnb pricing charts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AirbnbVizColors:
    background: str = "#FBFCFE"
    panel: str = "#FFFFFF"
    text: str = "#111827"
    text_secondary: str = "#334155"
    grid: str = "#E2E8F0"
    border: str = "#CBD5E1"
    teal: str = "#0F766E"
    teal_light: str = "#D8F1EE"
    blue: str = "#2563EB"
    blue_light: str = "#DBEAFE"
    navy: str = "#1E293B"
    amber: str = "#D97706"
    amber_light: str = "#FDECC8"
    purple: str = "#7C3AED"
    grey: str = "#94A3B8"


@dataclass(frozen=True)
class AirbnbVizTypography:
    figure_title: int = 24
    subplot_title: int = 16
    axis_label: int = 13
    tick_label: int = 12
    annotation: int = 12
    legend: int = 11
    line_spacing: float = 1.28


COLORS = AirbnbVizColors()
TYPOGRAPHY = AirbnbVizTypography()

PERIOD_COLORS = [COLORS.teal, COLORS.blue, COLORS.amber, COLORS.purple]
ROOM_TYPE_COLORS = {
    "Entire home": COLORS.teal,
    "Private room": COLORS.blue,
    "Hotel room": COLORS.amber,
    "Shared room": COLORS.purple,
}


def configure_matplotlib() -> None:
    """Apply global Matplotlib defaults used by poster-ready charts."""

    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "figure.facecolor": COLORS.background,
            "axes.facecolor": COLORS.background,
            "axes.edgecolor": COLORS.border,
            "axes.labelcolor": COLORS.text,
            "axes.titlecolor": COLORS.text,
            "xtick.color": COLORS.text_secondary,
            "ytick.color": COLORS.text_secondary,
            "text.color": COLORS.text,
            "font.family": "DejaVu Sans",
            "font.size": TYPOGRAPHY.tick_label,
            "axes.titlesize": TYPOGRAPHY.subplot_title,
            "axes.titleweight": "bold",
            "axes.labelsize": TYPOGRAPHY.axis_label,
            "xtick.labelsize": TYPOGRAPHY.tick_label,
            "ytick.labelsize": TYPOGRAPHY.tick_label,
            "legend.fontsize": TYPOGRAPHY.legend,
            "grid.color": COLORS.grid,
            "grid.linewidth": 1.0,
            "grid.alpha": 0.75,
            "savefig.facecolor": COLORS.background,
        }
    )


def apply_theme(ax, grid_axis: str | None = "y") -> None:
    """Style a Matplotlib axis with the shared Airbnb pricing theme."""

    ax.set_facecolor(COLORS.background)
    ax.figure.set_facecolor(COLORS.background)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLORS.border)
    ax.spines["bottom"].set_color(COLORS.border)
    ax.tick_params(colors=COLORS.text_secondary, labelsize=TYPOGRAPHY.tick_label)
    ax.xaxis.label.set_color(COLORS.text)
    ax.yaxis.label.set_color(COLORS.text)
    if grid_axis:
        ax.grid(True, axis=grid_axis, color=COLORS.grid, linewidth=1, alpha=0.75)
        ax.set_axisbelow(True)
