from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import plotly.graph_objects as go  # type: ignore


def _output_figure(
    fig: go.Figure,
    *,
    show: bool | None = None,
    html_path: str | None = None,
    png_path: str | None = None,
    height: int | None = None,
    width: int | None = None,
) -> None:
    if show is None:
        show = html_path is None and png_path is None
    if show:
        show_figure(fig, height=height, width=width)
    if html_path is not None:
        if html_path is None:
            raise Exception('set html_path to file path')
        print('writing treemap html to', html_path)
        export_figure_to_html(fig, html_path=html_path)
    if png_path is not None:
        if png_path is None:
            raise Exception('set output_path to file path')
        print('writing treemap png to', png_path)
        export_figure_to_png(fig, png_path=png_path, height=height, width=width)


def show_figure(
    fig: go.Figure,
    *,
    height: int | None = None,
    width: int | None = None,
) -> None:
    if height is None:
        height = 600
    if width is None:
        width = 1000
    hires_config = {
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'kalshi-volume',
            'height': height,
            'width': width,
            'scale': 2,
        },
        'displayModeBar': False,
    }
    fig.show(config=hires_config)


def export_figure_to_html(fig: go.Figure, html_path: str) -> None:
    import os

    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    fig.write_html(html_path, config={'displayModeBar': False})
    # fig.write_html(output_path, include_plotlyjs='cdn', full_html=True)


def export_figure_to_png(
    fig: go.Figure,
    png_path: str,
    scale: int = 4,
    height: int | None = None,
    width: int | None = None,
) -> None:
    import os

    os.makedirs(os.path.dirname(png_path), exist_ok=True)

    fig.write_image(
        png_path, format='png', scale=scale, width=width, height=height
    )
