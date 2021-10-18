import matplotlib
import matplotlib.pyplot as plt
import toolstr


def format_xticks(
    rotation=-20, timestamps=False, toolstr_kwargs=None, xticks_kwargs=None, tickmap=None,
):

    # set defaults
    if toolstr_kwargs is None:
        toolstr_kwargs = {}

    if timestamps:
        toolstr_kwargs.setdefault('format_type', 'timestamp')
        toolstr_kwargs.setdefault('representation', 'TimestampISO')

    # set formatter
    tick_locations, tick_texts = plt.xticks()
    if max(tick_locations) > 10:
        if tickmap is not None:
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


def format_yticks(toolstr_kwargs=None, yticks_kwargs=None):

    # set defaults
    if toolstr_kwargs is None:
        toolstr_kwargs = {}

    # set formatter
    tick_locations, tick_texts = plt.yticks()
    if max(tick_locations) > 10:
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
            )

    if ytick_grid:
        for ytick in plt.yticks()[0]:
            plt.axhline(
                ytick,
                linestyle=linestyle,
                color=color,
                alpha=alpha,
                zorder=-999,
            )

    plt.xlim(xlim)
    plt.ylim(ylim)

