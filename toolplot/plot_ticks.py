from __future__ import annotations

import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import toolstr


def set_labels(
    *,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    y_percentage: bool = False,
    y_decimals: int | None = None,
    x_decimals: int | None = None,
) -> None:
    if title is not None:
        plt.title(title)
    if xlabel is not None:
        plt.xlabel(xlabel)
    if ylabel is not None:
        plt.ylabel(ylabel)
    format_xticks()
    if y_percentage:
        toolstr_kwargs = {'percentage': True}
    else:
        toolstr_kwargs = {}
    format_yticks(toolstr_kwargs=toolstr_kwargs)
    add_tick_grid()


def format_xticks(
    rotation=-25,
    timestamps=False,
    dates=False,
    toolstr_kwargs=None,
    xticks_kwargs=None,
    tickmap=None,
    formatter=None
):

    # set defaults
    if toolstr_kwargs is None:
        toolstr_kwargs = {}

    if dates:
        toolstr_kwargs.setdefault('format_type', 'timestamp')
        toolstr_kwargs.setdefault('representation', 'TimestampDate')
    if timestamps:
        toolstr_kwargs.setdefault('format_type', 'timestamp')
        toolstr_kwargs.setdefault('representation', 'TimestampISO')

    # set formatter
    tick_locations, tick_texts = plt.xticks()
    if formatter is not None:
        f = formatter
    elif tickmap is not None:
        f = lambda x, p: toolstr.format(tickmap[x], **toolstr_kwargs)
    else:
        f = lambda x, p: toolstr.format(x, **toolstr_kwargs)
    plt.gca().get_xaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(f)
    )

    # set rotation
    if rotation is not None:
        if rotation < 0:
            ha = 'left'
        elif rotation > 0:
            ha = 'right'
        else:
            ha = 'center'
        plt.xticks(rotation=rotation, ha=ha)

    # set other kwargs
    if xticks_kwargs is not None:
        plt.xticks(**xticks_kwargs)


def format_yticks(toolstr_kwargs=None, yticks_kwargs=None, formatter=None):

    # set defaults
    if toolstr_kwargs is None:
        toolstr_kwargs = {}

    # set formatter
    if yticks_kwargs is None:
        yticks_kwargs = {}
    tick_locations, tick_texts = plt.yticks(**yticks_kwargs)
    if formatter is not None:
        f = formatter
    else:
        f = lambda x, p: toolstr.format(x, **toolstr_kwargs)
    plt.gca().get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(f)
    )

    # set other kwargs
    if yticks_kwargs is not None:
        plt.yticks(**yticks_kwargs)


def add_tick_grid(
    alpha=0.1,
    color='black',
    linestyle='--',
    linewidth=1,
    xtick_grid=True,
    ytick_grid=True,
):
    xlim = plt.xlim()
    ylim = plt.ylim()

    if xtick_grid:
        for xtick in plt.xticks()[0]:
            plt.axvline(
                xtick,
                linestyle=linestyle,
                color=color,
                alpha=alpha,
                zorder=-999,
                linewidth=linewidth,
            )

    if ytick_grid:
        for ytick in plt.yticks()[0]:
            plt.axhline(
                ytick,
                linestyle=linestyle,
                color=color,
                alpha=alpha,
                zorder=-999,
                linewidth=linewidth,
            )

    plt.xlim(xlim)
    plt.ylim(ylim)

