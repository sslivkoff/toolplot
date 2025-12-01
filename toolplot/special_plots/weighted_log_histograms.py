from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import polars as pl


def plot_weighted_histogram(
    df: pl.DataFrame | pl.LazyFrame,
    metric_column: str,
    *,
    metric_name: str | None = None,
    rows_are: str | None = None,
    bins: typing.Sequence[int | float] | None = None,
    metric_format: dict[str, typing.Any] = {},
    count_format: dict[str, typing.Any] | None = None,
    left_closed: bool = True,
    bin_style: typing.Literal['upper', 'lower', 'both'] = 'both',
    show: bool = True,
) -> dict[str, typing.Any]:
    import numpy as np
    import polars as pl
    import toolstr
    import matplotlib.pyplot as plt
    import toolplot

    if bins is None:
        col = pl.col(metric_column)
        if isinstance(df, pl.LazyFrame):
            min_log10 = np.log10(
                df.select(col.filter(col > 0).min()).collect().item()
            )
            max_log10 = np.log10(
                df.select(col.filter(col > 0).max()).collect().item()
            )
        elif isinstance(df, pl.DataFrame):
            min_log10 = np.log10(df.select(col.filter(col > 0).min()).item())
            max_log10 = np.log10(df.select(col.filter(col > 0).max()).item())
        else:
            raise Exception()

        floor_log10 = int(np.floor(min_log10))
        ceil_log10 = int(np.ceil(max_log10))
        orders = ceil_log10 - floor_log10

        if left_closed:
            bins = np.logspace(floor_log10, ceil_log10, orders)
        else:
            bins = np.logspace(floor_log10, ceil_log10, orders)

    # bin sizes
    raw_sizes = (
        df.select(metric_column)
        .with_columns(
            bin=pl.col(metric_column).cut(
                bins,
                left_closed=left_closed,
                include_breaks=True,
            )
        )
        .group_by('bin')
        .agg(n_events=pl.len(), total=pl.col(metric_column).cast(float).sum())
        .sort('bin')
        .unnest('bin')
    )
    if isinstance(raw_sizes, pl.LazyFrame):
        total_size_per_bin = raw_sizes.collect()
    elif isinstance(raw_sizes, pl.DataFrame):
        total_size_per_bin = raw_sizes
    else:
        raise Exception()

    # formatting
    plt_metric_format = metric_format.copy()
    if 'prefix' in plt_metric_format and '$' in plt_metric_format['prefix']:
        plt_metric_format['prefix'] = plt_metric_format['prefix'].replace(
            '$', '\\$'
        )
    bin_strs = []
    for lower, upper in zip(
        [float('-inf')] + list(bins),
        list(bins) + [float('inf')],
    ):
        if lower == float('-inf'):
            lower_str = '-inf'
        else:
            lower_str = toolstr.format(
                lower, order_of_magnitude=True, decimals=0, **plt_metric_format
            )
        if upper == float('inf'):
            upper_str = 'inf'
        else:
            upper_str = toolstr.format(
                upper, order_of_magnitude=True, decimals=0, **plt_metric_format
            )
        if bin_style == 'upper':
            as_str = upper_str
        elif bin_style == 'lower':
            as_str = lower_str
        elif bin_style == 'both':
            as_str = lower_str + ', ' + upper_str
            if left_closed:
                if lower == float('-inf'):
                    as_str = '< ' + upper_str
                elif upper == float('inf'):
                    as_str = '>= ' + lower_str
                else:
                    as_str = '[' + lower_str + ', ' + upper_str + ')'
            else:
                if lower == float('-inf'):
                    as_str = '<= ' + upper_str
                elif upper == float('inf'):
                    as_str = '> ' + lower_str
                else:
                    as_str = '(' + lower_str + ', ' + upper_str + ']'
        else:
            raise Exception()
        bin_strs.append(as_str)
    if metric_name is None:
        metric_name = metric_column
    xlabel = '\n' + metric_name
    if count_format is None:
        count_format = {'order_of_magnitude': True, 'decimals': 0}

    # unweighted plot
    unweighted_figure = plt.figure()
    bin_heights = []
    for breakpoint in list(bins) + [float('inf')]:
        breakpoint_size = total_size_per_bin.filter(breakpoint=breakpoint)
        if len(breakpoint_size) == 0:
            bin_heights.append(0)
        else:
            bin_heights.append(breakpoint_size['n_events'][0])
    plt.bar(range(len(bin_heights)), bin_heights, color='grey')

    # unweighted plot formatting
    toolplot.format_yticks(toolstr_kwargs=count_format)
    if rows_are is None:
        plt.ylabel('count\n')
    else:
        plt.ylabel('number of ' + rows_are + '\n')
    plt.xlabel(xlabel)
    plt.xticks(range(len(bins) + 1), bin_strs, rotation=270)
    toolplot.add_tick_grid()
    title = 'Distribution of ' + metric_name.title()
    if rows_are is not None:
        title += ' across ' + rows_are.title()
    plt.title(title)
    if show:
        plt.show()
        print()

    # weighted plot
    weighted_figure = plt.figure()
    bin_heights = []
    for breakpoint in list(bins) + [float('inf')]:
        breakpoint_size = total_size_per_bin.filter(breakpoint=breakpoint)
        if len(breakpoint_size) == 0:
            bin_heights.append(0)
        else:
            bin_heights.append(breakpoint_size['total'][0])
    bin_heights = np.array(bin_heights)
    plt.bar(range(len(bin_heights)), bin_heights, color='grey')

    # weighted plot formatting
    toolplot.format_yticks(toolstr_kwargs=metric_format)
    plt.ylabel('total ' + metric_name + '\n')
    plt.xlabel(xlabel)
    plt.xticks(range(len(bins) + 1), bin_strs, rotation=270)
    toolplot.add_tick_grid()
    if rows_are is None:
        title = 'Total ' + metric_name.title() + ' in each bin'
    else:
        title = (
            'Total '
            + metric_name.title()
            + ' in each '
            + rows_are.title()
            + ' bin'
        )
    plt.title(title)
    if show:
        plt.show()

    return {
        'unweighted_figure': unweighted_figure,
        'weighted_figure': weighted_figure,
        'bins': bins,
        'sizes': total_size_per_bin,
    }
