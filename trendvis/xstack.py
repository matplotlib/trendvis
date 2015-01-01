import numpy as np
import matplotlib.pyplot as plt
import draw
import plot_accessory as pa

def multi_x(figsize, plotspacing, plot_sizeratios, ylimits,
            plotdata, ylabel, xlabels, yticks, xticks, dpi=80, reverse_x=None,
            reverse_y=True, xlimits=None, startside='top',
            alternate_sides=True, spinewidth=3, black_spines=False,
            use_lastcolor=False, majortick_dim=(15,5), minortick_dim=(6,3),
            tick_direction=('out','out'), ticklabel_formatter='%d',
            axes_to_twin=None, twins_behind=True, shift_twinnedax=0.2,
            remove_extraspines=True, reorder=None, draw_frame=(False, 3),
            draw_bars=None, draw_columns=None, col_loc=None,
            draw_rectangles=None):
    """
    Creates a figure with multiple x-axes stacked along one y-axis such that
        the data all appears to be in one plotspace.

    Parameters
    ----------
    figsize : tuple of ints
        Sets the overall size of the figure
    plotspacing : float
        Sets the horizontal overlap between subplots. -0.35 recommended.
        If all the x-axes on one side (alternate_sides=False), >=0.0
    plot_sizeratios : list of ints
        The relative sizes of the desired subplot boxes.  Each subplot box may
        have multiple traces and/or two x-axes.
    ylimits : tuple of floats or ints
        Forced limts on the y axis.
    plotdata : list of list of tuples
        (x, y,x color, linewidth, linestyle, marker)
        One sublist per x-axis (including twin axes).  Each tuple has trace
        and formatting options.  The first tuple in each sublist determines axis
        spine color, unless use_lastcolor=True or black_spines=True.
    ylabel : string
        The label of the y-axis.
    xlabels : list of strings
        The labels of each of the x-axes, including twins.
    yticks : typle of floats or ints
        The values of the (major, minor) tick divisions on the y-axis
    xticks : list of tuple of floats or ints
        The value of the (major, minor) tick divisions for each x-axis,
        including twins.

    Keyword Arguments
    -----------------
    dpi : int
        Default 80.  Resolution of the figure
    reverse_x : list of ints
        Default None.  A list of indices indicating which x-axes to invert.
        Order automatically changes with reorder.
    reverse_y : Boolean
        Default True.  If True, invert y-axis.
    xlimits : list of tuples of ints and floats
        Default None.  A list of tuples of x-axis (index, minimum, maximum) if
        limits have to be forced on a particular x-axis.
        Indices automatically change with reorder.
    startside : string
        Default 'top'.  ['top'|'bottom'].  Indicates side of the first x-axis.
        After startside, x-axis will alternate if alternate_sides is True.
    alternate_sides : Boolean
        Default True.  [True|False].  If False, all x-axis labels and scales
        will be located on startside (except for twins).
    spinewidth : int
        Default 3.  The width of the axis spines.
    black_spines : Boolean
        Default False.  [True|False].  If True, x-axis spines, ticks are black.
    use_lastcolor : Boolean
        Default False.  [True|False].  If true, the x-axis spines are the color
        of the last plotted trace, rather than the first.
    majortick_dim : tuple of ints
        Default (15, 5).  A tuple of majortick dimensions (length, width).
    minortick_dim : tuple of ints
        Default (6,3).  A tuple of minortick dimensions (length, width).
    tick_direction : tuple of strings
        Default ('out', 'out').  Tuple of (major, minor) tick directions.
    ticklabel_formatter : string magic
        Default '%d'.  ['%d'|'%i'|'%.1f'|'%.2f'].  Formatting magic for
        tick labels.  Decimal, integer, float (precision = 1), float
        (precision = 2).
    axes_to_twin : list of ints
        Default None.  List of indicies indicating which original axes to twin.
    twins_behind : Boolean
        Default True.  [True|False].  Forces twinned axis, plot(s)
        behind the original axis, plot(s).
    shift_twinnedax : float
        Default 0.2.  The percentage of figure size to shift the twinned x-axes
        above or below the normal position.
    reorder : list of ints
        Default None.  The new order of the data.
    draw_frame : Tuple of Boolean, int
        Default (False, 3).  [True|False].  If True, draws a box around the
        axes, visually anchoring the spines to a frame.  If False,
        the spines will be floating.  linewidth = draw_frame[1].
    draw_bars : list of tuples of (min, max, color, optional alpha)
        Default None.  Draws horizontal bars across plotting area.
    draw_columns : list of tuples of (min, max, color, optional alpha)
        Default None.  Draws vertical bars across a column (given in col_loc)
    col_loc : list of ints
        Default None. Column locations of the columns defined in draw_columns.
    draw_rectangles :
        Default None.

    Returns
    -------
    fig : figure instance
        The figure
    axes : list of axes instances
        The axes of the figure `fig`

    """

    # Create figure
    fig = plt.figure(figsize=figsize)

    # Initialize subplot column position, total grid columns, and axes list
    i = 0
    totalcols = sum(plot_sizeratios)
    axes = []

    # Make subplot grid and get list of axes
    for c in plot_sizeratios:

        ax = plt.subplot2grid((1,totalcols), (0,i), colspan=c)
        axes.append(ax)

        i += c

    # Initialize starting x-axis side, number of subplots, lists
    side = startside
    subplotnum = len(plot_sizeratios)
    pos_list = []
    side_list = []

    # Initialize dictionary of the spines to remove
    # Based on axis position in subplot grid and x-axis location
    spine_begone = {'left' : {'top'    : ['bottom', 'right'],
                              'bottom' : ['top', 'right']},
                    'none' : {'top'    : ['bottom', 'left', 'right'],
                              'bottom' : ['top', 'left', 'right']},
                    'right': {'top'    : ['bottom', 'left'],
                              'bottom' : ['top', 'left']},
                    'both' : {'top'    : ['bottom'],
                              'bottom' : ['top']}}

    # Set tick positions and get rid of extraneous spines
    # (remove_extraspines=True)
    for j in range (0, subplotnum):

        # Find subplot position- plots are left to right.
        if j == 0 and subplotnum > 1:
            pos = 'left'
        elif j == 0 and subplotnum == 1:
            pos = 'both'
        elif j == subplotnum - 1:
            pos = 'right'
        else:
            pos = 'none'

        # Put subplot position and side of x-axis into a plot
        pos_list.append(pos)
        side_list.append(side)

        # Set the x and y axis ticks, set the background invisible
        axes[j].xaxis.set_ticks_position(side)
        axes[j].yaxis.set_ticks_position(pos)

        axes[j].patch.set_visible(False)

        # Switch labels of topside subplots to top x-axis
        if side == 'top':
            axes[j].xaxis.set_tick_params(labeltop='on', labelbottom='off')

        # Switch labels of rightmost subplot to rightmost y-axis
        if pos == 'right':
            axes[j].yaxis.set_tick_params(labelleft='off', labelright='on')
        elif pos == 'both':
            axes[j].yaxis.set_tick_params(labelleft='on', labelright='on')

        # Get rid of extraneous spines unless remove_extraspines=True
        for sp in spine_begone[pos][side]:
            if remove_extraspines:
                axes[j].spines[sp].set_visible(False)

            # Remove ticklabels from extra bottom spines
            # if sp == 'bottom':
            #     plt.setp(axes[j].get_xticklabels(), visible=False)

            # Remove ticklabels from extra left spines
            if sp == 'left' and pos == 'none':
                plt.setp(axes[j].get_yticklabels(), visible=False)

        if alternate_sides:
            # Switch sides
            if side == 'top':
                side = 'bottom'
            else:
                side = 'top'

    # Check for x-axis twinning
    if axes_to_twin is not None:
        # Twinned axes creation
        for x in axes_to_twin:

            # Get the side of the original x-axis
            side = axes[x].xaxis.get_ticks_position()

            # Twin, turn on box around new axes, set the background invisible
            ax = axes[x].twiny()
            ax.set_frame_on(True)
            ax.patch.set_visible(False)

            # Set the side of the new twin, if necessary shifting ticks position
            # Set the amount to shift the new x axis relative to the figure
            if side == 'bottom':
                side = 'top'
                shift = 1 + shift_twinnedax
            else:
                axes[x].xaxis.set_ticks_position(side)
                side = 'bottom'
                shift = 0 - shift_twinnedax
                ax.xaxis.set_ticks_position(side)

            twin_pos = 'none'

            # Get rid of extraneous spines, remove y tick labels from view
            for sp in spine_begone[twin_pos][side]:
                if remove_extraspines:
                    ax.spines[sp].set_visible(False)

            # plt.setp(ax.get_yticklabels(), visible=False)

            # Move the spine of the x axis
            ax.spines[side].set_position(('axes', shift))

            # Put the new axes instance and position information into lists
            axes.append(ax)
            side_list.append(side)
            pos_list.append(twin_pos)

            # Put original axis on top of twin
            if twins_behind:
                axes[x].set_zorder(ax.get_zorder()+1)

    # Order of plots is determined by order of plotdata.
    # Easily shuffle plots using reorder
    # If reorder is None, then reorder will be set to the original order
    if reorder is None:
        reorder = range(0, len(plotdata))

    # Format axes and ticks
    for m, x, p, s in zip(reorder, axes, pos_list, side_list):

        # Set xlimits
        if reverse_y:
            x.set_ylim(ylimits[1], ylimits[0])
        else:
            x.set_ylim(ylimits[0], ylimits[1])

        # Get the axis color info
        if black_spines:
            xcolor = 'black'
        else:
            if use_lastcolor:
                xcolor = plotdata[m][-1][2]
            else:
                xcolor = plotdata[m][0][2]

        # Set tick parameters
        pa.set_ticks(x, xticks[m], yticks, xcolor, 'black',
                     majortick_dim, minortick_dim, tick_direction, 16, 10,
                     formatter=ticklabel_formatter)

        # Set the color, linewidth, label postion, and label of each x-axis
        x.spines[s].set_color(xcolor)
        x.spines[s].set_linewidth(spinewidth)
        x.xaxis.set_label_position(s)

        x.set_xlabel(xlabels[m], fontsize=20, labelpad=15)
        x.xaxis.set_label_position(s)

        # if the axis belongs to the right- or leftmost subplot, set the
        # y-axis spinewidth, label, and label position
        if p == 'right' or p == 'both':
            x.set_ylabel(ylabel, fontsize=24, labelpad=35, rotation=270,
                         verticalalignment='bottom')
            x.spines['right'].set_linewidth(spinewidth)
            x.yaxis.set_label_position('right')

        if p == 'left' or p == 'both':
            x.set_ylabel(ylabel, fontsize=24, labelpad=15)
            x.spines['left'].set_linewidth(spinewidth)
            x.yaxis.set_label_position('left')


    # Set xlimits for axes that have specified xlimits
    if xlimits is not None:
        for xlimit in xlimits:
            axes[reorder.index(xlimit[0])].set_xlim(xlimit[1], xlimit[2])

    # Plot data
    # Later- add functionality for errorbars
    for x, m in zip(axes, reorder):

        pd = plotdata[m]

        # Tuples are (x, y, color, lw, ls, marker)
        for p in pd:
            if p[5] is None:
                x.plot(p[0], p[1], color=p[2], linewidth=p[3],
                       linestyle=p[4], zorder=10, markeredgecolor='none')
            else:
                x.plot(p[0], p[1], p[5], color=p[2], linewidth=p[3],
                       linestyle=p[4], zorder=10, markeredgecolor='none')

    if reverse_x is not None:
        for rev in reverse_x:
            axes[reorder.index(rev)].invert_xaxis()

    if draw_frame[0]:
        rightax = len(plot_sizeratios)-1
        draw.frame(fig, axes[0], axes[rightax], draw_frame[1])

    # Alter the spacing between subplots (to pretend this is one giant plot)
    plt.subplots_adjust(wspace=plotspacing)

    if draw_bars is not None:
        rightax = subplotnum-1
        for bar_settings in draw_bars:
            draw.bar(fig, axes[0], axes[rightax], bar_settings, False)

    if draw_columns is not None:
        for col_setting, col_num in zip(draw_columns, col_loc):
            draw.bar(fig, axes[col_loc], axes[col_loc], draw_columns, True)

    return fig, axes