from xgrid_ystack import XGrid
# from ygrid_xstack import YGrid


def xplot(xratios, yratios, figsize, xticks, yticks, plotdata, line_kwargs={},
          grid_cleanup=True, startside='left', rows_to_twin=None,
          axis_shift=None, twinax_shift=None, alternate_sides=True,
          onespine_forboth=False, logxscale='none', auto_spinecolor=True,
          logyscale='none', tick_fontsize=10, spinewidth=2):

    """
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

    # Set up grid, grid formatting
    grid = XGrid(xratios, yratios, figsize, startside=startside,
                 alternate_sides=alternate_sides,
                 onespine_forboth=onespine_forboth)

    if rows_to_twin is not None:
        grid.make_twins(rows_to_twin)

    grid.set_ticknums(xticks, yticks, logyscale=logyscale, logxscale=logxscale)

    grid.set_ticks(labelsize=tick_fontsize)

    if axis_shift is not None or twinax_shift is not None:
        grid.set_relative_axshift(axis_shift=axis_shift,
                                  twin_shift=twinax_shift)
        grid.set_absolute_axshift()
        grid.move_spines()

    grid.set_spinewidth(spinewidth)

    if grid_cleanup:
        grid.cleanup_grid()

    for row, datagroup in zip(grid.axes, plotdata):
        for col in range(0, grid.mainax_dim):
            for dataset in datagroup:
                try:
                    if col in dataset[4]:
                        row[col].errorbar(dataset[0], dataset[1],
                                          color=dataset[2], ecolor=dataset[2])
                except:
                    row[col].errorbar(dataset[0], dataset[1],
                                      color=dataset[2], ecolor=dataset[2])
    if auto_spinecolor:
        grid.autocolor_spines(0)

    return grid


# def yplot():

# def change_orientation(grid):
