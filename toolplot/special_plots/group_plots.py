from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import polars as pl
    import plotly.graph_objects as go  # type: ignore

    PlotGroupsMode = typing.Literal['line', 'area', 'area_%']


def plot_groups(
    data: pl.DataFrame,
    *,
    mode: PlotGroupsMode = 'line',
    group_column: str,
    groups: list[str] | None = None,
    n_groups: int | None = None,
    colors: dict[str, str] | None = None,
    metric_column: str,
    metric_name: str,
    metric_format: dict[str, typing.Any] | None = None,
    title: str | None = None,
    xlim: tuple[float | int | None, float | int | None] | None = None,
    ylim: tuple[float | int | None, float | int | None] | None = None,
    include_total: bool = False,
    total_visible: typing.Literal['legendonly', True, False] = True,
    set_ylim: bool = False,
    xaxis_hoverformat: str | None = None,
    show: bool = True,
) -> go.Figure:
    import polars as pl
    import plotly.graph_objects as go

    # process inputs
    if groups is None:
        groups = (
            data.group_by(group_column)
            .agg(metric=pl.sum(metric_column))
            .sort('metric', descending=True)[group_column]
            .to_list()
        )
    if n_groups is not None:
        groups = groups[:n_groups]
    if colors is None:
        colors = {}

    # initialize figure
    fig = go.Figure()

    # add total
    total: pl.DataFrame | None = None
    if include_total:
        total = data.group_by('timestamp', maintain_order=True).agg(
            pl.sum(metric_column)
        )
        total_scatter = create_scatter_object(
            x=total['timestamp'],
            y=total[metric_column],
            group='TOTAL',
            color='black',
            metric_format=metric_format,
            visible=total_visible,
            width=5,
            mode=mode,
            g=None,
        )
        fig.add_trace(total_scatter)

    all_timestamps = data.select(pl.col.timestamp.unique()).sort('timestamp')
    for g, group in enumerate(groups):
        x, y = get_group_data(
            data=data,
            group=group,
            group_column=group_column,
            metric_column=metric_column,
            all_timestamps=all_timestamps,
            mode=mode,
        )
        group_scatter = create_scatter_object(
            x=x,
            y=y,
            group=group,
            g=g,
            color=colors.get(group),
            metric_format=metric_format,
            mode=mode,
        )
        fig.add_trace(group_scatter)

    # update layouts
    fig.update_layout(
        template='plotly_white',
        height=600,
        hovermode='x unified',
        margin=dict(t=55 if title != '' else 0, b=0, l=0, r=0, pad=0),
        title=get_title_params(title),
        xaxis=get_xaxis_params(
            data=data,
            xlim=xlim,
            xaxis_hoverformat=xaxis_hoverformat,
            label_style=get_label_params(),
            grid_style=get_grid_params(mode=mode),
            mode=mode,
        ),
        yaxis=get_yaxis_params(
            mode=mode,
            metric_name=metric_name,
            metric_column=metric_column,
            metric_format=metric_format,
            ylim=ylim,
            include_total=include_total,
            set_ylim=set_ylim,
            label_style=get_label_params(),
            grid_style=get_grid_params(mode=mode),
            total=total,
        ),
        legend=get_legend_params(label_style=get_label_params()),
    )

    if show:
        show_figure(fig)

    return fig


def create_scatter_object(
    x: list[typing.Any] | pl.Series,
    y: list[typing.Any] | pl.Series,
    mode: PlotGroupsMode,
    *,
    group: str,
    g: int | None = None,
    color: str | None = None,
    metric_format: dict[str, typing.Any] | None = None,
    visible: typing.Literal['legendonly', True, False] = True,
    width: int = 3,
) -> go.Scatter:
    import plotly.graph_objects as go
    import toolstr

    if metric_format is None:
        metric_format = {}
    custom: list[str | None] = []
    for value in y:
        if value is None:
            custom.append(None)
        else:
            custom.append(toolstr.format(value, **metric_format))

    if mode == 'line':
        return go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name=group,
            line=dict(color=color, width=width),
            legendgroup=group,
            customdata=custom,
            line_simplify=False,
            hovertemplate=group + ': %{customdata}<extra></extra>',
            connectgaps=False,
            visible=visible,
        )
    elif mode == 'area_%':
        return go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name=group,
            line=dict(color=color, width=0),
            stackgroup='one',
            groupnorm='percent',
            fill='tonexty' if ((g is not None) and (g > 0)) else 'tozeroy',
            fillcolor=color,
            opacity=1.0,
            hovertemplate=('%{y:.1f}%'),
            customdata=custom,
        )
    else:
        raise Exception('invalid mode: ' + str(mode))


def get_group_data(
    data: pl.DataFrame,
    group: str,
    group_column: str,
    metric_column: str,
    all_timestamps: pl.DataFrame,
    mode: PlotGroupsMode,
    add_head_pad: bool = True,
) -> tuple[pl.Series, pl.Series]:
    import polars as pl

    agg = (
        data.filter(pl.col(group_column) == group)
        .join(all_timestamps, on='timestamp', how='right')
        .group_by('timestamp')
        .agg(
            pl.when(pl.col(metric_column).count() > 0)
            .then(pl.sum(metric_column))
            .alias(metric_column)
        )
        .sort('timestamp')
    )
    if mode == 'line':
        if add_head_pad:
            non_null = agg.filter(pl.col(metric_column).is_not_null())
            head_null = agg.filter(pl.col.timestamp < non_null['timestamp'][0])
            if len(head_null) > 0:
                head_pad = head_null[-1].fill_null(0)
                agg = pl.concat([agg, head_pad]).sort('timestamp')
    elif mode == 'area_%':
        pass
    else:
        raise Exception()

    return agg['timestamp'], agg[metric_column]


def get_label_params() -> dict[str, typing.Any]:
    return {'size': 18, 'color': '#000000'}


def get_grid_params(mode: PlotGroupsMode) -> dict[str, typing.Any]:
    if mode == 'area_%':
        return dict(showgrid=False)
    else:
        return dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            griddash='5 3',
        )


def get_title_params(title: str | None) -> dict[str, typing.Any]:
    return {
        'text': title,
        'x': 0.5,  # Centers the title
        'xanchor': 'center',
        'font': {'size': 24, 'color': '#000000'},
    }


def get_xaxis_params(
    *,
    data: pl.DataFrame,
    xaxis_hoverformat: str | None = None,
    label_style: dict[str, typing.Any] | None = None,
    xlim: tuple[float | int | None, float | int | None] | None = None,
    grid_style: dict[str, typing.Any] | None = None,
    mode: PlotGroupsMode,
) -> dict[str, typing.Any]:
    if xaxis_hoverformat is None:
        xaxis_hoverformat = '%Y-%m-%d'
    if xlim is not None:
        xmin, xmax = xlim
        if xmin is None:
            xmin = data['timestamp'].min()  # type: ignore
        if xmax is None:
            xmax = data['timestamp'].max()  # type: ignore
        xlim = (xmin, xmax)
    params = dict(
        range=xlim,
        title={'font': label_style},
        tickfont=label_style,
        tickformatstops=[
            dict(dtickrange=['M12', None], value='%Y'),
            dict(dtickrange=['M1', 'M12'], value='%Y-%m'),
            dict(dtickrange=[None, 'M1'], value='%Y-%m-%d'),
        ],
        rangeslider=dict(visible=True, thickness=0.1),
        type='date',
        hoverformat=xaxis_hoverformat,
        **grid_style,  # type: ignore
    )

    if mode == 'area_%':
        params['showspikes'] = True
        params['spikemode'] = 'across'
        params['spikesnap'] = 'cursor'
        params['spikethickness'] = 1
        params['spikedash'] = 'solid'

    return params


def get_yaxis_params(
    *,
    metric_name: str,
    mode: PlotGroupsMode,
    label_style: dict[str, typing.Any],
    ylim: tuple[float | int | None, float | int | None] | None = None,
    include_total: bool = False,
    set_ylim: bool = False,
    metric_format: dict[str, typing.Any] | None = None,
    grid_style: dict[str, typing.Any] | None = None,
    total: pl.DataFrame | None = None,
    metric_column: str,
) -> dict[str, typing.Any]:
    if mode == 'area_%':
        return dict(
            title={
                'text': 'Share of ' + metric_name,
                'font': label_style,
                'standoff': 24,
            },
            range=[-2, 103],
            fixedrange=False,
            tickfont=label_style,
            ticksuffix='%',
            dtick=20,
            showspikes=True,
            spikemode='across',  # draws full-width horizontal line
            spikesnap='cursor',
            spikethickness=1,
            spikedash='solid',
        )
    else:
        if metric_format is None:
            metric_format = {}
        if include_total and set_ylim:
            ylim = [
                -total[metric_column][-7:].max() * 0.07,  # type: ignore
                total[metric_column][-7:].max() * 1.1,  # type: ignore
            ]
        else:
            ylim = None
        return dict(
            title={'text': metric_name, 'font': label_style, 'standoff': 24},
            range=ylim,
            fixedrange=False,
            tickfont=label_style,
            tickprefix=('$' if metric_format.get('prefix') == '$' else None),
            **grid_style,  # type: ignore
        )


def get_legend_params(
    *,
    label_style: dict[str, typing.Any],
) -> dict[str, typing.Any]:
    return dict(
        orientation='v',
        yanchor='top',
        y=0.9,
        xanchor='left',
        x=1.02,
        font=label_style,
    )


def show_figure(fig: go.Figure) -> None:
    hires_config = {
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'kalshi-volume',
            'height': 600,
            'width': 1000,
            'scale': 2,
        },
        'displayModeBar': False,
    }
    fig.show(config=hires_config)


# def _project():
#     fig.add_trace(
#         go.Scatter(
#             x=x[:-1],
#             y=y[:-1],
#             mode='lines',
#             name=category,
#             line=dict(color=color, width=3),
#             legendgroup=category,
#             customdata=[
#                 toolstr.format(value, **metric_format)
#                 for value in y[:-1]
#             ],
#             line_simplify=False,
#             hovertemplate=category + ': %{customdata}<extra></extra>',
#         )
#     )
#     fig.add_trace(
#         go.Scatter(
#             x=x[-2:],
#             y=y[-2:],
#             mode='lines',
#             line=dict(color=color, width=3, dash='5 3'),
#             marker=dict(size=6),
#             hoverinfo='skip',
#             showlegend=False,
#             legendgroup=category,
#         )
#     )
#     fig.add_trace(
#         go.Scatter(
#             x=x[-1:],
#             y=y[-1:],
#             mode='markers',
#             line=dict(color=color, width=3, dash='dot'),
#             marker=dict(size=6),
#             name=category,
#             showlegend=False,
#             legendgroup=category,
#         )
#     )
