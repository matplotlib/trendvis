import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

def set_yticks(axis, yticks, ycolor, majordim, minordim, tick_direction,
              labelsize, pad, formatter):

    """
    Set y ticks.

    Parameters
    ----------
    axis : matplotlib axis object
        The axis
    yticks : tuple of ints or floats
        The (major, minor) tick divisions
    ycolor : string or float
        The y-axis spine, tick color
    majordim : tuple of ints
        The (length, width) of the major ticks
    minordim : tuple of ints
        The (length, width) of the minor ticks
    tick_direction : tuple of strings
        The (major, minor) tick directions
    labelsize : int
        Font size of tick labels
    pad : int
        Spacing between ticks and tick labels.
    formatter : string
        Formatting magic.

    """

    # Initialize and set major and minor tick locators, formatters
    ymajorLocator = MultipleLocator(yticks[0])
    yminorLocator = MultipleLocator(yticks[1])

    axis.yaxis.set_major_locator(ymajorLocator)
    axis.yaxis.set_minor_locator(yminorLocator)

    frmttr = FormatStrFormatter(formatter)
    axis.yaxis.set_major_formatter(frmttr)

    # Set the size and direction of major and minor ticks
    axis.yaxis.set_tick_params(which='major', direction=tick_direction[0],
                               length=majordim[0], width=majordim[1],
                               color=ycolor)
    axis.yaxis.set_tick_params(which='minor', direction=tick_direction[1],
                               length=minordim[0], width=minordim[1],
                               color=ycolor)

    # Set the tick label size and position
    axis.tick_params(labelsize=labelsize, pad=pad)


def set_xticks(axis, xticks, xcolor, majordim, minordim, tick_direction,
               tick_params_kw, formatter):
    """
    Set x ticks

    Parameters
    ----------
    axis : matplotlib axis object
        The axis
    xticks : tuple of ints or floats
        The (major, minor) tick divisions
    xcolor : string or float
        The x-axis spine, tick color
    majordim : tuple of ints
        The (length, width) of the major ticks
    minordim : tuple of ints
        The (length, width) of the minor ticks
    tick_direction : tuple of strings
        The (major, minor) tick directions
    labelsize : int
        Font size of tick labels
    pad : int
        Spacing between ticks and tick labels.
    formatter : string
        Formatting magic.

    """

    # Initialize and set major and minor tick locators, formatters
    xmajorLocator = MultipleLocator(xticks[0])
    xminorLocator = MultipleLocator(xticks[1])

    axis.xaxis.set_major_locator(xmajorLocator)
    axis.xaxis.set_minor_locator(xminorLocator)

    frmttr = FormatStrFormatter(formatter)
    axis.xaxis.set_major_formatter(frmttr)

    # Set the size and direction of major and minor ticks
    axis.xaxis.set_tick_params(which='major', direction=tick_direction[0],
                               length=majordim[0], width=majordim[1],
                               color=xcolor)
    axis.xaxis.set_tick_params(which='minor', direction=tick_direction[1],
                               length=minordim[0], width=minordim[1],
                               color=xcolor)

    # Set the tick label size and position
    axis.tick_params(**tick_params_kw)


def yposition_datasides(numrows, alternate_sides, altsides_dict, startside):
    """
    """
    if numrows == 1:
        pos_list = ['both']
        side_list = [startside]
    else:
        nonerows = numrows - 2
        pos_list = ['top'] + ['none']*nonerows + ['bottom']

        if alternate_sides:
            side_list = [startside]
            for i in range(1, numrows):
                newside = altsides_dict[side_list[i-1]]
                side_list.append(newside)
        else:
            side_list = [startside]*numrows

    return pos_list, side_list

def xposition_datasides(numcols, alternate_sides, altsides_dict, startside):
    """
    """


def shift_list(shift_by, num):
    if shift_by is None:
        shift_degrees = [0.0]*num
    else:
        shift_degrees = shift_by


def reordering(reorder, ratios, ticks, labels, axis_shift, to_twin, reverse_ax,
               bar_location, limits):
    """
    """
    plotdata = reorder_bysort(reorder, plotdata)
    ratios = reorder_bysort(reorder, ratios)
    ticks = reorder_bysort(reorder, ticks)
    labels = reorder_bysort(reorder, labels)

    if axis_shift is not None:
        axis_shift = reorder_bysort(reorder, axis_shift)

    if to_twin is not None:
        to_twin = reorder_byindex(reorder, to_twin)
    if reverse_ax is not None:
        reverse_ax = reorder_byindex(reorder, reverse_ax)
    if bar_location is not None:
        bar_location = reorder_byindex(reorder, bar_location)

    if limits is not None:
        re_limits = []:
        for lim in limits:
            re_limits.append((reorder.index(lim[0]), lim[1], lim[2]))

        limits = re_limits

    return (plotdata, ratios, ticks, labels, axis_shift, to_twin, reverse_ax,
            bar_location, limits)



def reorder_bysort(reorder, to_sort):
    """
    Reorder a list of items

    Parameters
    ----------
    reorder : list of ints
        The new order
    to_sort : list of items
        The list to sort

    Return
    ------
    re_sort : list of items
        to_sort in the order supplied by reorder

    """

    rlen = len(reorder)
    re_sort = [x for (y, x) in sorted(zip(reorder, to_sort[:rlen]))]
    re_sort.extend(plotdata[rlen:])

    return re_sort


def reorder_byindex(reorder, to_sort):
    """
    Change a variable-length list of indices referencing a 0-n order
        to a list of new indices referencing a different order.

    Parameters
    ----------
    reorder : list of ints
        The new reference order
    to_sort : list of ints
        The list of indices referencing the old order

    Return
    ------
    re_index : list of ints
        The list of indices referencing the new order (reorder)

    """

    re_index = []
    for s in to_sort:
        re_index.append(reorder.index(s))

    return re_index


# def reorder_y(reorder, numrows, plotdata, rows_to_twin, reverse_y, yratios,
#               yticks, yaxis_shift, ylabels, draw_bars, bar_loc):
#     """
#     Reorder the parameters for a stacked y-axis plot

#     """

#     rlen = len(reorder)
#     if rlen != numrows:
#         raise ValueError('`reorder` length must equal `yratios` length')

#     # Edit plotdata order (except twins)
#     re_plotdata = [x for (y, x) in sorted(zip(reorder, plotdata[:rlen]))]
#     re_plotdata.extend(plotdata[rlen:])
#     plotdata = re_plotdata

#     # Edit twin axes
#     if rows_to_twin is not None:
#         reordered_rows = []
#         for r in rows_to_twin:
#             reordered_rows.append(reorder.index(r))
#         rows_to_twin = reordered_rows

#     reordered_rev_y = []
#     for r in reverse_y:
#         reordered_rev_y.append(reorder.index(r))
#     reverse_y = reordered_rev_y

#     # Edit yratio order
#     re_yratios = [x for (y, x) in sorted(zip(reorder, yratios))]
#     yratios = re_yratios

#     re_yticks = [x for (y, x) in sorted(zip(reorder, yticks))]
#     yticks = re_yticks

#     if yaxis_shift is not None:
#         re_shift = [x for (y, x) in sorted(zip(reorder, yaxis_shift))]
#         yaxis_shift = re_shift

#     re_ylabels = [x for (y, x) in sorted(zip(reorder, ylabels))]
#     ylabels = re_ylabels

#     if ylimits is not None:
#         re_ylimits = []
#         for y in ylimits:
#             re_ylimits.append((reorder.index[y[0]], y[1], y[2]))

#     if draw_bars is not None:
#         re_bars = []
#         for ind in bar_loc:
#             re_bars.append(reorder.index[ind])

#     return (plotdata, rows_to_twin, reverse_y, yratios, yticks, yaxis_shift,
#             ylabels, ylimits, bar_loc)

