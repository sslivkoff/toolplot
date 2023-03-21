from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np


def plot_log_x_histogram(
    x,
    *bin_args,
    xlim=None,
    n_bins=30,
    bin_min=None,
    **bin_kwargs,
):
    if xlim is None:
        if bin_min is None:
            xmin = max(min(x), 0.00000000001)
        else:
            xmin = bin_min
        xlim = [xmin, max(x)]
    bins = np.logspace(np.log10(xlim[0]), np.log10(xlim[1]), n_bins)

    plt.hist(x, *bin_args, bins=bins, **bin_kwargs)

    #     counts, bins = np.histogram(x, bins)
    #     plt.hist(counts, bins=bins, **bin_kwargs)

    plt.xscale('log')

