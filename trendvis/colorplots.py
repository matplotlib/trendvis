import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import draw
import plot_accessory as pa

def discrete_colorplot(figsize, possible_values, value_colors, color_labels,
                       xdata, ydata, colordata, xlabel, ylabel, xticks, yticks,
                       xlim=None, ylim=None, shapedata=None, shapelabels=None,
                       markersize=20, msizemultiplier=1, tick_direction='in',
                       tick_dims=(10, 4, 5, 2), edges_on=False):
    """
    Makes a 2D plot of xdta vs ydata vs colordata.  Item shape (shapedata)
        is meant for data classification purposes, not conveying the main
        idea of the plot.  Pass shapes in order of use, one per
        x-, y-, colordata array.

    Parameters
    ----------
    figsize : tuple of ints
        The size of the figure
    possible_values : list of length N of ints, strings, floats
        List of the finite and known range of possible values of colordata.
    value_colors : list of length N of strings or of tuples of floats
        The color corresponding to each value in possible_values.
    color_labels : list of length N of strings
        The significance of each color i.e. the legend entry for each color.
    xdata : list of length M of 1D ndarrays of floats
        The x-values
    ydata : list of length M of 1D ndarrays of floats
        The y-values
    colordata : list of length M of 1D ndarrays
        Data is of the same type as contents of possible_values.
        Used to determine color of each xdata, ydata point.
    xlabel : string
        The x-axis label
    ylabel : string
        The y-axis string
    xticks : tuple of ints or floats
        The (major, minor) x-axis ticks
    yticks : tuple of ints or floats
        The (major, minor) y-axis ticks

    Keyword Arguments
    -----------------
    xlim : tuple of ints or floats
        Default None.  The (lower, upper) extent of the x-axis
    ylim : tuple of ints or floats
        Default None.  The (lower, upper) extent of the y-axis
    shapedata : list of length M of strings
        Default None.  The shape assigned to each array in xdata, ydata,
        colordata.  If None, then all markers will be 'o'.
    shapelabels : list of length M of strings
        Defaults None.  The significance of each shape provided in
        shapelabels, i.e. the legend labels.
    markersize : int or list (length M) of 1D data arrays
        Default 20.  The markersize of all points or each point.
    msizemultiplier : int or float
        Default 1.  The factor by which to multiply markersize.
    tick_direction : string
        Default 'in'.  ['in'|'out'|'inout']
    tick_dims : tuple of ints
        Default (10, 4, 5, 2).  The (major length, width, minor length, width)
        dimensions of the x and y-axis tick marks

    """

    # Create figure
    fig, ax = plt.subplots(1,1, figsize=figsize)

    # Dictionary of possible values for colordata and the corresponding colors
    colordict = dict(zip(possible_values, value_colors))

    # Handle markers
    try:
        markersize[0]
    except TypeError:
        mslist = []
        for xd in xdata:
            # Make and fill arrays the same size as data arrays w/markersize
            ms = np.empty(xd.size)
            ms.fill(markersize)
            mslist.append(ms)

        markersize = mslist
    else:
        for i in range(0, len(markersize)):
            markersize[i] = markersize[i] * msizemultiplier

    # Handle shapes
    if shapedata is None:
        shapedata = ['o'] * len(xdata)

    if edges_on:
        mec = 'black'
    else:
        mec = 'none'

    for xd, yd, cd, shp, ms in zip(xdata, ydata, colordata, shapedata, markersize):
        # Step through each data array and shape
        # for x, y, c, m in zip(xd, yd, cd, ms):
        for i in range(0, xd.size):
            # Step through individual points
            # ax.plot(x, y, marker=shp, linestyle='none', color=colordict[c],
            #         markeredgecolor=mec, markersize=m, zorder=10)
            ax.plot(xd[i], yd[i], marker=shp, linestyle='none', color=colordict[cd[i]],
                    markeredgecolor=mec, markersize=ms[i], zorder=10)


    # Set tick parameters
    pa.set_ticks(ax, xticks, yticks, 'black', 'black',
                 (tick_dims[0], tick_dims[1]), (tick_dims[2], tick_dims[3]),
                 (tick_direction, tick_direction), 14, 10)

    # # Set tick parameters
    # xmajor = MultipleLocator(xticks[0])
    # xminor = MultipleLocator(xticks[1])
    # ymajor = MultipleLocator(yticks[0])
    # yminor = MultipleLocator(yticks[1])

    # ax.xaxis.set_major_locator(xmajor)
    # ax.xaxis.set_minor_locator(xminor)
    # ax.yaxis.set_major_locator(ymajor)
    # ax.yaxis.set_minor_locator(yminor)

    # ax.tick_params(labelsize=14, pad=10)

    # ax.xaxis.set_tick_params(which='major', length=tick_dims[0],
    #                          width=tick_dims[1], direction=tick_direction)
    # ax.xaxis.set_tick_params(which='minor', length=tick_dims[2],
    #                          width=tick_dims[3], direction=tick_direction)

    # ax.yaxis.set_tick_params(which='major', length=tick_dims[0],
    #                          width=tick_dims[1], direction=tick_direction)
    # ax.yaxis.set_tick_params(which='minor', length=tick_dims[2],
    #                          width=tick_dims[3], direction=tick_direction)

    # Make shape legend if we have the data
    if shapedata is not None and shapelabels is not None:
        shapeartists = []
        labels = []

        # Get unique shapes and their labels
        unique_shapes = set(zip(shapedata, shapelabels))

        for shp in unique_shapes:
            artist = Line2D((0,1),(0,0), color='k', marker=shp[0],
                            linestyle='')

            shapeartists.append(artist)
            labels.append(shp[1])

        lshp = ax.legend(shapeartists, labels, loc=4, numpoints=1)

    colorartists = []

    # Make and add color legend
    for c in value_colors:
        artist = Line2D((0,1), (0,0), color=c, linewidth=10)
        colorartists.append(artist)

    lc = ax.legend(colorartists, color_labels, loc=1)

    # Try to add shape legend
    try:
        ax.add_artist(lshp)
    except:
        pass

    # Set the x, y axis labels
    ax.set_ylabel(ylabel, fontsize=16, labelpad=12)
    ax.set_xlabel(xlabel, fontsize=16, labelpad=12)

    # Set x, y limits if provided
    if xlim is not None:
        ax.set_xlim(xlim[0], xlim[1])
    if ylim is not None:
        ax.set_ylim(ylim[0], ylim[1])

    return fig, ax


# def continuous_colorplot(figsize, xdata, ydata, colordata, sizedata=20,
#                        colormap, edges_on=False, xlim, ylim, xticks, yticks,
#                        color_scale):