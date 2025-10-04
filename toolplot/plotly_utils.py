from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import plotly.graph_objects as go  # type: ignore


def _output_figure(
    fig: go.Figure,
    *,
    show: bool | None = None,
    show_kwargs: dict[str, typing.Any] | None = None,
    html_path: str | None = None,
    html_kwargs: dict[str, typing.Any] | None = None,
    png_path: str | None = None,
    png_kwargs: dict[str, typing.Any] | None = None,
    height: int | None = None,
    width: int | None = None,
) -> None:
    if show is None:
        show = html_path is None and png_path is None
    if show:
        show_figure(fig, height=height, width=width, show_kwargs=show_kwargs)
    if html_path is not None:
        if html_path is None:
            raise Exception('set html_path to file path')
        print('writing html to', html_path)
        export_figure_to_html(fig, html_path=html_path, html_kwargs=html_kwargs)
    if png_path is not None:
        if png_path is None:
            raise Exception('set output_path to file path')
        print('writing png to', png_path)
        export_figure_to_png(
            fig,
            png_path=png_path,
            height=height,
            width=width,
            png_kwargs=png_kwargs,
        )


def show_figure(
    fig: go.Figure,
    *,
    height: int | None = None,
    width: int | None = None,
    show_kwargs: dict[str, typing.Any] | None = None,
) -> None:
    # build kwargs
    if show_kwargs is None:
        show_kwargs = {}
    if height is None:
        height = 600
    if width is None:
        width = 1000
    show_kwargs.setdefault(
        'config',
        {
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'kalshi-volume',
                'height': height,
                'width': width,
                'scale': 2,
            },
            'displayModeBar': False,
        },
    )

    # show figure
    fig.show(**show_kwargs)


def export_figure_to_html(
    fig: go.Figure,
    html_path: str,
    html_kwargs: dict[str, typing.Any] | None = None,
) -> None:
    import os

    # build kwargs
    if html_kwargs is None:
        html_kwargs = {}
    html_kwargs.setdefault('config', {'displayModeBar': False})

    # export html
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    fig.write_html(html_path, **html_kwargs)


def export_figure_to_png(
    fig: go.Figure,
    png_path: str,
    scale: int = 4,
    height: int | None = None,
    width: int | None = None,
    png_kwargs: dict[str, typing.Any] | None = None,
) -> None:
    import os

    # build kwargs
    if png_kwargs is None:
        png_kwargs = {}
    png_kwargs.setdefault('format', 'png')
    png_kwargs.setdefault('scale', scale)
    if height is None:
        height = 600
    png_kwargs.setdefault('height', height)
    if width is None:
        width = 1000
    png_kwargs.setdefault('width', width)

    # export png
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    fig.write_image(png_path, format='png', **png_kwargs)
