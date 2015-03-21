from xgrid_ystack import XGrid
from ygrid_xstack import YGrid


def make_grid(xratios, yratios, figsize, xticks, yticks, main_axis,
              plotdata=None, xlim=None, ylim=None,
              startside='default', alternate_sides=True, line_kwargs={},
              grid_cleanup=True, to_twin=None, axis_shift=None,
              twinax_shift=None, onespine_forboth=False, logxscale='none',
              logyscale='none', auto_spinecolor=True, tick_fontsize=10,
              spinewidth=2):

    """
    Create a plot with a stack of multiple y (x) axes against
        the main axis, x (y)

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
    startside : string
        Default 'default'.  For YGrid (`main_axis` = 'y') ['top'|'bottom'].
        For XGrid (`main_axis` = 'x') ['left'|'right'].  The side that
        topmost/leftmost stacked axis' spine will appear on if `grid_cleanup`
        is True.
    alternate_sides : Boolean
        Default True.  [True|False].
        Stacked axis spines alternate sides or are all on startside.
    line_kwargs : dictionary


    Returns
    -------
    grid : YGrid or XGrid object



    """

    mainax = main_axis.lower()[0]

    startside_dict = {'x' : 'left',
                      'y' : 'top'}

    if startside is 'default':
        startside = startside_dict[mainax]

    if mainax is 'y':
        # Set up grid, grid formatting
        grid = XGrid(xratios, yratios, figsize, startside=startside,
                     alternate_sides=alternate_sides,
                     onespine_forboth=onespine_forboth)

    elif mainax is 'x':
        grid = YGrid(xratios, yratios, figsize, startside=startside,
                     alternate_sides=alternate_sides,
                     onespine_forboth=onespine_forboth)

    else:
        raise ValueError('main_axis arg, ' + main_axis + ' is not recognized')

    if to_twin is not None:
        grid.make_twins(to_twin)

    grid.set_ticknums(xticks, yticks, logyscale=logyscale, logxscale=logxscale)

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

    grid.set_spinewidth(spinewidth)

    if grid_cleanup:
        grid.cleanup_grid()

    if plotdata is not None:
        plot_data(plotdata, grid, line_kwargs={},
                  auto_spinecolor=auto_spinecolor)

    return grid


def plot_data(plotdata, grid, line_kwargs={}, auto_spinecolor=True):
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

    # Initialize line defaults, update
    default_linekwargs = {'marker' : 'o',
                          'ls' : '-',
                          'zorder' : 10,
                          'lw' : 1,
                          'elinewidth' : 1,
                          'capthick' : 1,
                          'capsize' : 3}

    default_linekwargs.update(line_kwargs)

    for subgrid, subgrid_data in zip(grid.axes, plotdata):
        for ax_ind in range(0, grid.mainax_dim):
            for dataset in subgrid_data:
                try:
                    if ax_ind in dataset[4]:
                        subgrid[ax_ind].errorbar(dataset[0], dataset[1],
                                                 color=dataset[2],
                                                 ecolor=dataset[2])
                except:
                    subgrid[ax_ind].errorbar(dataset[0], dataset[1],
                                             color=dataset[2],
                                             ecolor=dataset[2])
        if auto_spinecolor:
            grid.autocolor_spines(0)


def change_orientation(grid):
    """
    Make an XGrid given a YGrid, and vice versa.

    Parameters
    ----------
    grid : YGrid or XGrid instance
        The grid to introspect and apply properties to new grid of other
        orientation

    """

    side_position_dict = {'top'   : 'left',
                          'bottom': 'right',
                          'left'  : 'top',
                          'right' : 'bottom',
                          'none'  : 'none'}

    # Figsize is (width, height), so to change orientation give (h, w)
    if grid.mainax_id is 'x':
        newgrid = YGrid(grid.yratios, grid.xratios, (grid.fig.get_figheight,
                                                     grid.fig.get_figwidth))

    else:
        newgrid = XGrid(grid.yratios, grid.xratios, (grid.fig.get_figheight,
                                                     grid.fig.get_figwidth))

    if grid.twinds is not None:
        newgrid.make_twins(grid.twinds)

    newgrid.dataside_list = []
    newgrid.stackpos_list = []

    for side in grid.dataside_list:
        newgrid.dataside_list.append(side_position_dict[side])

    for pos in grid.stackpos_list:
        newgrid.stackpos_list.append(side_position_dict[pos])
