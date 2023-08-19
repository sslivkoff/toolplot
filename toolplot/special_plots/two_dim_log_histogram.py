from __future__ import annotations

import typing


def plot_2d_log_histogram(
    x_values: typing.Sequence[int | float],
    y_values: typing.Sequence[int | float],
    bins: int
    | (int, int)
    | (typing.Sequence[int | float] | typing.Sequence[int | float]) = 10,
    cmap="nipy_spectral_r",
    colorbar: bool = True,
    log: bool = True,
    xtick_format: typing.Mapping[str, typing.Any] | None = None,
    ytick_format: typing.Mapping[str, typing.Any] | None = None,
    n_xticks: int | None = None,
    n_yticks: int | None = None,
    log_x: bool = False,
    log_y: bool = False,
    x_bin_min: float = 1e-14,
    y_bin_min: float = 1e-14,
    colorbar_label: str | None = None,
    ctick_format: typing.Mapping[str, typing.Any] | None = None,
) -> None:
    import matplotlib.colors as mcolors
    from matplotlib.ticker import FixedLocator
    import matplotlib.pyplot as plt
    import numpy as np
    import toolstr

    if log_x or log_y:
        bins = create_2d_bins(
            log_x=log_x,
            log_y=log_y,
            bins=bins,
            x_values=x_values,
            y_values=y_values,
            x_bin_min=x_bin_min,
            y_bin_min=y_bin_min,
        )
    elif isinstance(bins, (list, tuple)):
        bins = [bins[1], bins[0]]
    elif isinstance(bins, int):
        bins = [bins, bins]
    else:
        raise Exception('invalid bin format')
    hist = np.histogramdd([y_values, x_values], bins)

    if log:
        norm = mcolors.LogNorm()
    else:
        norm = None

    plt.imshow(hist[0], norm=norm, cmap=cmap, origin="lower")

    if colorbar:
        cbar = plt.colorbar()
        cbar.set_label(colorbar_label, rotation=270, va='bottom')
        cbar.outline.set_visible(False)
        if ctick_format is not None:
            ctick_locs = cbar.get_ticks()
            ctick_labels = [toolstr.format(loc, **ctick_format) for loc in ctick_locs]
            cbar.ax.yaxis.set_major_locator(FixedLocator(ctick_locs))
            cbar.ax.set_yticklabels(ctick_labels)

    # ticks
    xtick_locs, xtick_labels = get_ticks(hist[1][1], xtick_format, n_xticks)
    plt.xticks(xtick_locs, xtick_labels, rotation=270)
    ytick_locs, ytick_labels = get_ticks(hist[1][0], ytick_format, n_yticks)
    plt.yticks(ytick_locs, ytick_labels)

    return hist


def get_ticks(
    bins: typing.Sequence[float], format: typing.Any, n_ticks: int | None
) -> (typing.Sequence[float], typing.Sequence[float]):
    import numpy as np
    import toolstr

    if format is None:
        format = {}

    locs = np.arange(len(bins)) - 0.5
    labels = [toolstr.format_number(value, **format) for value in bins]
    if n_ticks is not None:
        indices = np.linspace(0, len(locs) - 1, n_ticks).astype(int)
        locs = locs[indices]
        labels = [labels[index] for index in indices]
    return locs, labels


def create_2d_bins(
    x_values: typing.Sequence[int | float],
    y_values: typing.Sequence[int | float],
    bins: int
    | (int, int)
    | (typing.Sequence[int | float] | typing.Sequence[int | float]),
    log_x: bool = False,
    log_y: bool = False,
    x_bin_min: float = 1e-14,
    y_bin_min: float = 1e-14,
) -> (typing.Sequence[float], typing.Sequence[float]):

    if isinstance(bins, int):
        n_xbins = bins
        n_ybins = bins
    elif (
        isinstance(bins, (tuple, list))
        and len(bins) == 2
        and isinstance(bins[0], int)
        and isinstance(bins[1], int)
    ):
        n_xbins, n_ybins = bins
    else:
        raise Exception('invalid bin specification')

    if log_x:
        xbins = create_log_bins(
            x_values,
            n_bins=n_xbins,
            bin_min=x_bin_min,
        )
    else:
        xbins = create_lin_bins(x_values, n_xbins)
    if log_y:
        ybins = create_log_bins(
            y_values,
            n_bins=n_ybins,
            bin_min=y_bin_min,
        )
    else:
        ybins = create_lin_bins(y_values, n_ybins)
    return [ybins, xbins]


def create_lin_bins(
    values: typing.Sequence[int | float],
    n_bins: int | None,
) -> typing.Sequence[float]:
    import numpy as np

    return np.linspace(min(values), max(values), n_bins)


def create_log_bins(
    values: typing.Sequence[int | float],
    n_bins: int | None,
    bin_min: int | float | None,
) -> typing.Sequence[float]:
    import numpy as np

    if n_bins is None:
        n_bins = 10
    if bin_min is None:
        bin_min = 1e-15
    min_value = min(values)
    if bin_min is not None:
        min_value = max(min_value, bin_min)
    max_value = max(values)
    return np.logspace(np.log10(min_value), np.log10(max_value), n_bins)
