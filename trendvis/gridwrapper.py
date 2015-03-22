from xgrid_ystack import XGrid
from ygrid_xstack import YGrid


def make_grid(xratios, yratios, figsize, xticks, yticks, main_axis,
              plotdata=None, xlim=None, ylim=None, to_twin=None,
              axis_shift=None, twinax_shift=None, tick_fontsize=10, **kwargs):

    """
    Easy grid and grid formatting set-up; not all options accessible
        via this interface.

    Create a plot with a stack of multiple y (x) axes against
        the main axis, x (y).

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


    Returns
    -------
    grid : YGrid or XGrid object

    """

    mainax = main_axis.lower()[0]

    startside_dict = {'x' : 'left',
                      'y' : 'top'}

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
        plot_data(plotdata, grid, **kwargs)

    return grid


def plot_data(plotdata, grid, auto_spinecolor=True, marker='o', ls='-',
              zorder=10, lw=1, elinewidth=1, capthick=1, capsize=3, **kwargs):
    """
    Plot a lot of data at once

    Parameters
    ----------
    plotdata : list of lists of tuples

    grid

    Keyword Arguments
    -----------------
    line_kwargs : dictionary
    auto_spinecolor : Boolean

    """

    for subgrid, subgrid_data in zip(grid.axes, plotdata):
        for ax_ind in range(0, grid.mainax_dim):
            for dataset in subgrid_data:
                try:
                    if ax_ind in dataset[4]:
                        subgrid[ax_ind].errorbar(dataset[0], dataset[1],
                                                 color=dataset[2],
                                                 ecolor=dataset[2],
                                                 marker=marker, ls=ls,
                                                 zorder=zorder, lw=lw,
                                                 capsize=capsize,
                                                 capthick=capthick,
                                                 elinewidth=elinewidth,
                                                 **kwargs)
                except:
                    subgrid[ax_ind].errorbar(dataset[0], dataset[1],
                                             color=dataset[2],
                                             ecolor=dataset[2],
                                             marker=marker, zorder=zorder,
                                             capsize=capsize, lw=lw, ls=ls,
                                             capthick=capthick,
                                             elinewidth=elinewidth, **kwargs)
        if auto_spinecolor:
            grid.autocolor_spines(0)
