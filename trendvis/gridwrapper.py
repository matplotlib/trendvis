from xgrid_ystack import XGrid
from ygrid_xstack import YGrid


def make_grid(xratios, yratios, figsize, xticks, yticks, main_axis,
              plotdata=None, xlim=None, ylim=None, to_twin=None,
              axis_shift=None, twinax_shift=None, tick_fontsize=10, **kwargs):

    """
    Build a plot with a stack of multiple y (x) axes against a main x (y) axis

    This is an easy grid and grid formatting set-up, but not all options are
    accessible via this interface.

    Parameters
    ----------
    xratios : int or list of ints
        The relative sizes of the columns.  Not directly comparable
        to yratios
    yratios : int or list of ints
        The relative sizes of the rows.  Not directly comparable to xratios
    figsize : tuple of ints or floats
        The figure dimensions in inches
    xticks : list of tuples
        List of (major, minor) tick mark multiples.  Used to set major and
        minor locators.  One tuple per x axis
    yticks : list of tuples
        List of (major, minor) tick mark multiples.  Used to set major and
        minor locators.  One tuple per y axis
    main_axis : string
        ['x'|'y'].  The common axis that all plots will share.

    Keyword Arguments
    -----------------
    plotdata : list of lists of tuples
        Default None. Tuple format: (x, y, color, {}, [ax inds within row/col])
        One sublist per row or column (including twins).  To skip plotting on a
        row or column, insert empty sublist at position corresponding to
        the index of the row or column.
    xlim : list of tuples of ints and/or floats
        Default None.  List of (column, min, max).
        If xdim is 1, then column is ignored.
        Also, if only one x axis needs xlim, can just pass the tuple
    ylim : List of tuples of ints and/or flaots
        Default None.  List of (row, min, max).
        If ydim is 1, then row is ignored.
        Also, if only one y axis needs ylim, can just pass a tuple.
    to_twin : list of ints
        Default None.  The indices of the rows (columns) to twin
    axis_shift : float or list of floats
        Default None.  Universal (float) or individual (list of floats)
        original axis spine relative shift.  Units are fraction of figure
    twinax_shift : float or list of floats
        Default None.  Universal (float) or individual (list of floats)
        twinned axis spine relative shift.  Units are fraction of figure
    tick_fontsize : int
        Default 10.  The fontsize of tick labels.

    Other Parameters
    ----------------
    kwargs : passed to ``plot_data()``, then to ``axes.plot()``

    Returns
    -------
    grid : YGrid or XGrid instance

    """

    mainax = main_axis.lower()[0]

    startside_dict = {'x': 'left',
                      'y': 'top'}

    startside = startside_dict[mainax]

    if mainax is 'y':
        # Set up grid, grid formatting
        grid = XGrid(xratios, yratios, figsize, startside=startside,
                     alternate_sides=True, onespine_forboth=False)

    elif mainax is 'x':
        grid = YGrid(xratios, yratios, figsize, startside=startside,
                     alternate_sides=True, onespine_forboth=False)

    else:
        raise ValueError('main_axis arg, ' + main_axis + ' is not recognized')

    if to_twin is not None:
        grid.make_twins(to_twin)

    grid.set_ticknums(xticks, yticks)

    grid.set_ticks(labelsize=tick_fontsize)

    if xlim is not None:
        grid.set_xlim(xlim)

    if ylim is not None:
        grid.set_ylim(ylim)

    if axis_shift is not None or twinax_shift is not None:
        grid.set_relative_axshift(axis_shift=axis_shift,
                                  twin_shift=twinax_shift)
        grid.set_absolute_axshift()
        grid.move_spines()

    grid.set_spinewidth(2)

    grid.cleanup_grid()

    if plotdata is not None:
        plot_data(grid, plotdata, **kwargs)

    return grid


def plot_data(grid, plotdata, auto_spinecolor=True, marker='o', ls='-',
              zorder=10, lw=1, **kwargs):
    """
    Easy way to plot a lot of line data at once.  Other plotting calls
    can be made by accessing individual axes in ``grid.axes``.

    Parameters
    ----------
    grid : XGrid or YGrid instance
        The Grid of axes on which to plot.
    plotdata : list of lists of tuples
        Default None. Tuple format: (x, y, color, {}, [ax inds within row/col])
        One sublist per row or column (including twins).  To skip plotting on a
        row or column, insert empty sublist at position corresponding to
        the index of the row or column.

    Keyword Arguments
    -----------------
    auto_spinecolor : Boolean
        If True, will color each stacked axis spines and ticks with the color
        of the first plot on the axis.
    marker : string
        Default 'o'.  Any matplotlib marker.
    ls : string
        Default '-'. Any matplotlib linestyle.
    zorder : int
        Default 10.  The zorder of the plot.
    lw : string
        Default 1.  Linewidth in points.

    Other Parameters
    ----------------
    kwargs : passed to axes.plot()

    """

    for subgrid, subgrid_data in zip(grid.axes, plotdata):
        for ax_ind in range(0, grid.mainax_dim):
            for dataset in subgrid_data:
                try:
                    if ax_ind in dataset[4]:
                        subgrid[ax_ind].plot(dataset[0], dataset[1], lw=lw,
                                             color=dataset[2], marker=marker,
                                             ls=ls, zorder=zorder, **kwargs)
                except:
                    subgrid[ax_ind].plot(dataset[0], dataset[1],
                                         color=dataset[2], marker=marker,
                                         zorder=zorder, lw=lw, ls=ls, **kwargs)
        if auto_spinecolor:
            grid.autocolor_spines(0)
