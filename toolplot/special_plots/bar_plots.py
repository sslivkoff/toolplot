from __future__ import annotations

import typing
import matplotlib.pyplot as plt

from .. import plot_ticks

if typing.TYPE_CHECKING:
    Series = typing.Any


def plot_bar(data: typing.Mapping[str, Series]):

    bottom = 0

    for series_name, series in data.items():

        plt.bar(
            range(len(series)),
            height=series,
            bottom=bottom,
            label=series_name,
        )
        bottom = bottom + series

    if len(data) > 1:
        plt.legend()

    plot_ticks.add_tick_grid()
    plot_ticks.format_yticks()

    xtick_labels = series.index.values
    plot_ticks.format_xticks(
        formatter=lambda tick, _: xtick_labels[int(tick)]
        if int(tick) < len(xtick_labels)
        else ''
    )
