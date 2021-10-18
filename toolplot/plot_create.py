import matplotlib.pyplot as plt

from . import plot_ticks


plot_specs = {
    'PlotData': {
        'common': {
            'merge': {'key_name': 'key_content'},
            # ... PlotDatum keys and values
        },
        'plots': {'PlotID': 'PlotDatum'},
        'subplot_height': 'Number',
        'figure': 'Map',
    },
    'PlotDatum': {
        'name': 'Text',
        'x': 'Series',
        'y': 'Series',
        'y_kwargs': 'Map',
        'ys': [{'y': 'Series', 'y_kwargs': 'Map'}],
        'stacks': ['Series'],
        'stacks_kwargs': 'Map',
        'tickgrid': 'Boolean',
        'xlabel': 'Text',
        'ylabel': 'Text',
        'xlim': ['Number', 'Number'],
        'ylim': ['Number', 'Number'],
        'title': 'Text',
    }
}


def plot(plot_datum, name_position='ylabel'):

    legend = False

    # extract args
    x = plot_datum.get('x')

    if plot_datum.get('y') is not None:
        y = plot_datum['y']
        y_kwargs = plot_datum.get('y_kwargs', {})

        # plot points
        if x is not None:
            plt.plot(x, y, **y_kwargs)
        else:
            plt.plot(y, **y_kwargs)

    if plot_datum.get('ys'):
        for subplot in plot_datum['ys']:
            y = subplot.get('y')
            y_kwargs = subplot.get('y_kwargs', {})

            # plot points
            if x is not None:
                plt.plot(x, y, **y_kwargs)
            else:
                plt.plot(y, **y_kwargs)

            if y_kwargs.get('label') is not None:
                legend = True

    if plot_datum.get('stacks') is not None:
        stacks_kwargs = plot_datum.get('stacks_kwargs', {})
        plt.stackplot(x, *plot_datum['stacks'], **stacks_kwargs)
        if stacks_kwargs.get('labels') is not None:
            legend = True

    # lines
    for hline in plot_datum.get('hlines', []):
        plt.axhline(**hline)
    for vline in plot_datum.get('vlines', []):
        plt.axvline(**hline)

    name = plot_datum.get('name')
    if name is not None:
        if name_position == 'ylabel':
            plt.ylabel(name)
            plt.gca().yaxis.tick_right()
        elif name_position == 'title':
            plt.title(name)
        else:
            raise Exception('unknown position for name: ' + str(name_position))
    plot_ticks.format_yticks()

    if legend or plot_datum.get('legend_kwargs') is not None:
        legend_kwargs = plot_datum.get('legend', {})
        plt.legend(**legend_kwargs)

    if plot_datum.get('tickgrid'):
        plot_ticks.add_tick_grid()

    if plot_datum.get('xlabel') is not None:
        plt.xlabel(plot_datum['xlabel'])
    if plot_datum.get('ylabel') is not None:
        plt.ylabel(plot_datum['ylabel'])

    if plot_datum.get('xlim') is not None:
        plt.xlim(plot_datum['xlim'])
    if plot_datum.get('ylim') is not None:
        plt.ylim(plot_datum['ylim'])


def plot_subplots(plot_data):

    common = plot_data.get('common', {})
    merge = common.get('merge')
    n_subplots = len(plot_data['plots'])

    if n_subplots == 0:
        print('[no plots specified, skipping plotting]')

    figure = plot_data.get('figure', {})
    subplot_height = plot_data.get('subplot_height', 3)
    figure.setdefault('figsize', [10, subplot_height * n_subplots])
    plt.figure(**figure)
    for sp, (plot_id, plot_datum) in enumerate(plot_data['plots'].items()):

        plot_datum = dict(plot_datum)
        for key, value in common.items():
            if key == 'merge':
                for subkey, subvalue in merge.items():
                    plot_datum.setdefault(subkey, {})
                    plot_datum[subkey] = dict(subvalue, **plot_datum[subkey])
            elif key not in plot_datum:
                plot_datum[key] = value

        # create plot
        plt.subplot(n_subplots, 1, sp + 1)
        if sp == 0 and plot_data.get('title') is not None:
            plt.title(plot_data['title'])
        plot(plot_datum=plot_datum)

