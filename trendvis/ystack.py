import numpy as np
import matplotlib.pyplot as plt
import draw
import plot_accessory as pa

def multi_y(figsize, plotspacing, plot_sizeratios, xlimits,
            plotdata, xlabel, ylabels, xticks, yticks, dpi=80, reverse_y=None,
            reverse_x=False, ylimits=None, startside='left',
            alternate_sides=True, spinewidth=3, black_spines=False,
            use_lastcolor=False, majortick_dim=(15,5), minortick_dim=(6,3),
            tick_direction=('out', 'out'), ticklabel_formatter='%d',
            axes_to_twin=None, twins_behind=True, shift_twinnedax=0.2,
            remove_extraspines=True, reorder=None, draw_frame=(False, 3),
            draw_bars=None, bar_loc=None, draw_columns=None,
            draw_rectangles=None):
    """
    Creates a figure with multiple y-axes stacked over one x-axis such that
        the data all appears to be in one plotspace.

    Parameters
    ----------
    figsize : tuple of ints
        Sets the overall size of the figure
    plotspacing
        Sets the vertical spacing between rows.  -0.35 recommended.
        If all the y-axes on one side (alternate_sides=False), >= 0.0
    plot_sizeratios : list of ints
        The relative sizes of the desired subplots.  Each subplot box may
        have multiple traces and/or two y-axes (twins).
    xlimits : tuple of floats or ints
        Forced limits on the x axis.
    plotdata : list of list of tuples
        (x, y, color, linewidth, linestyle, marker)
        One sublist per y-axis (including twin axes).  Each tuple is a trace
        and formatting options.  The first tuple in each sublist determines
        axis spine color, unless use_lastcolor=True or black_spines=True.
    xlabel : string
        The label of the x axis.
    ylabels : list of strings
        The labels of each of the y-axes, including twins.
    xticks : tuple of floats or ints
        The values of the (major, minor) tick divisions on the x-axis
    yticks : list of tuple of floats or ints
        The value of the (major, minor) tick divisions for each y-axis,
        including twins.

    Keyword Arguments
    -----------------
    dpi : int
        Default 80.  Resolution of the figure
    reverse_y : list of ints
        Default None.  A list of indices indicating which y-axes to invert.
    reverse_x : Boolean
        Default False.  If True, invert x-axis.
    ylimits : list of tuples of ints and floats
        Default None.  A list of tuples of y-axis (index, minimum, maximum) if
        limits have to be forced on a particular y-axis.
    startside : string
        Default 'left'.  ['left'|'right'].  Indicates side of the first y-axis.
        After startside, y-axis will alternate if alternate_sides is True.
    alternate_sides : Boolean
        Default True.  [True|False].  If False, all y-axis labels and scales
        will be located on startside (except for twins).
    spinewidth : int
        Default 3.  The width of the axis spines, also the linewidth of the
        frame if draw_frame is True.
    black_spines : Boolean
        Default False.  [True|False].  If True, y-axis spines, ticks are black.
    use_lastcolor : Boolean
        Default False.  [True|False].  If true, the y-axis spines are the color
        of the last plotted trace, rather than the first.
    majortick_dim : tuple of ints
        Default (15, 5).  A tuple of majortick dimensions (length, width).
    minortick_dim : tuple of ints
        Default (6, 3).  A tuple of minortick dimensions (length, width).
    tick_direction : tuple of strings
        Default ('out', 'out').  Tuple of (major, minor) tick directions.
    ticklabel_formatter : string magic
        Default '%d'.  ['%d'|'%i'|'%.1f'|'%.2f'].  Formatting magic for
        tick labels.  Decimal, integer, float (precision = 1), float
        (precision = 2).
    axes_to_twin : list of ints
        Default None.  List of indicies indicating which original axes to twin.
    twins_behind : Boolean
        Default True.  [True|False].  Forces twinned axis and its plot(s)
        behind the original axis and its plot(s).
    shift_twinnedax : float
        Default 0.2.  The percentage of figure size to shift the twinned y-axes
        from the left or right of the normal position.
    reorder : list of ints
        Default None.  The new order of the data.
    draw_frame : tuple of Boolean, int
        Default (False, 3).  [True|False].  If True, draws a box around the
        axes, visually anchoring the spines to a frame.  If False,
        the spines will appear to be floating.  linewidth=draw_frame[1]
    draw_bars : list of tuples of (min, max, color, optional alpha)
        Default None.  Draw horizontal bars across a row (given in bar_loc)
    bar_loc : list of ints
        Default None.  Row locations of the bars defined in draw_bars.
        len(draw_bars) == len(bar_loc)
    draw_columns : list of tuples of (min, max, color, optional alpha)
        Default None.  Draw vertical bars across the plot space.
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
    fig = plt.figure(figsize=figsize, dpi=dpi)

    # Initialize subplot row position, total grid rows, and axes list
    i = 0
    totalrows = sum(plot_sizeratios)
    axes = []

    # Make subplot grid and get list of axes
    for r in plot_sizeratios:

        ax = plt.subplot2grid((totalrows,1), (i,0), rowspan=r)
        axes.append(ax)

        i += r

    # Initialize starting y-axis side, number of subplots, lists
    side = startside
    subplotnum = len(plot_sizeratios)
    pos_list = []
    side_list = []

    # Initialize dictionary of the spines to remove
    # Based on axis position in subplot grid and y-axis location
    spine_begone = {'top'   : {'left'  : ['bottom', 'right'],
                               'right' : ['bottom', 'left']},
                    'none'  : {'left'  : ['top', 'bottom', 'right'],
                               'right' : ['top', 'bottom', 'left']},
                    'bottom': {'left'  : ['top', 'right'],
                               'right' : ['top', 'left']},
                    'both'  : {'left'  : ['right'],
                               'right' : ['left'] }}

    # Set ticks positions and get rid of extraneous spines
    # (remove_extraspines=True)
    for j in range (0, subplotnum):

        # Find subplot position- plots are top to bottom.
        if j == 0 and subplotnum > 1:
            pos = 'top'
        elif j == 0 and subplotnum == 1:
            pos = 'both'
        elif j == subplotnum - 1:
            pos = 'bottom'
        else:
            pos = 'none'

        # Put subplot position and side of y-axis into a plot
        pos_list.append(pos)
        side_list.append(side)

        # Set the x and y axis ticks, set the background invisible
        axes[j].xaxis.set_ticks_position(pos)
        axes[j].yaxis.set_ticks_position(side)

        axes[j].patch.set_visible(False)

        # Switch labels of top subplot to top x axis
        if pos == 'top':
            axes[j].xaxis.set_tick_params(labeltop='on', labelbottom='off')
        elif pos == 'both':
            axes[j].xaxis.set_tick_params(labeltop='on', labelbottom='on')

        # Get rid of extraneous spines unless remove_extraspines=True
        for sp in spine_begone[pos][side]:
            if remove_extraspines:
                axes[j].spines[sp].set_visible(False)

            # Remove ticklabels from extra bottom spines
            if sp == 'bottom' and j != 0:
                plt.setp(axes[j].get_xticklabels(), visible=False)

        if alternate_sides:
            # Switch sides
            if side == 'left':
                side = 'right'
            else:
                side = 'left'

    # Check for y-axis twinning
    if axes_to_twin is not None:
        # Twinned axes creation
        for x in axes_to_twin:

            # Get the side of the original y-axis
            side = axes[x].yaxis.get_ticks_position()

            # Twin, turn on box around new axes, set the background invisible
            # axes[x].invert_xaxis()
            ax = axes[x].twinx()
            ax.set_frame_on(True)
            ax.patch.set_visible(False)

            # Set the side of the new twin, if necessary shifting ticks position
            # Set the amount to shift the new y axis relative to the figure
            if side == 'left':
                side = 'right'
                shift = 1 + shift_twinnedax
            else:
                axes[x].yaxis.set_ticks_position(side)
                side = 'left'
                shift = 0 - shift_twinnedax
                ax.yaxis.set_ticks_position(side)

            twin_pos = 'none'

            # Get rid of extraneous spines, remove x tick labels from view
            for sp in spine_begone[twin_pos][side]:
                if remove_extraspines:
                    ax.spines[sp].set_visible(False)

            plt.setp(ax.get_xticklabels(), visible=False)

            # Move the spine of the y axis
            ax.spines[side].set_position(('axes', shift))

            # Put the new axes instance and position information into lists
            axes.append(ax)
            side_list.append(side)
            pos_list.append(twin_pos)

            if twins_behind:
                axes[x].set_zorder(ax.get_zorder()+1)

    # Order of plots is determined by order of plotdata.
    # Easily shuffle plots using reorder
    # If reorder is None, then reorder will be set to the original order
    if reorder is None:
        reorder = range(0, len(plotdata))

    # Given list of lists of records
    # One sublist per axis

    # Format axes and ticks
    for m, x, p, s in zip(reorder, axes, pos_list, side_list):

        # Set xlimits
        if reverse_x:
            x.set_xlim(xlimits[1], xlimits[0])
        else:
            x.set_xlim(xlimits[0], xlimits[1])

        # Get the axis color info
        if black_spines:
            ycolor ='black'
        else:
            if use_lastcolor:
                ycolor = plotdata[m][-1][2]
            else:
                ycolor = plotdata[m][0][2]

        # Set tick parameters
        pa.set_ticks(x, xticks, yticks[m], 'black', ycolor,
                     majortick_dim, minortick_dim, tick_direction, 16, 10,
                     ticklabel_formatter)

        # Set the color, linewidth, label position, and label of each y axis
        x.spines[s].set_color(ycolor)
        x.spines[s].set_linewidth(spinewidth)
        x.yaxis.set_label_position(s)

        if s == 'right':
            x.set_ylabel(ylabels[m], fontsize=18, labelpad=12,
                         rotation=270, verticalalignment='bottom')
        else:
            x.set_ylabel(ylabels[m], fontsize=18, labelpad=12)

        # If the axis belongs to the top or bottom subplot, set the x axis
        # linewidth, label, and label position
        if p != 'none':
            x.set_xlabel(xlabel, fontsize=20, labelpad=15)

            if p != 'bottom':
                x.spines['top'].set_linewidth(spinewidth)
                x.xaxis.set_label_position('top')
            if p != 'top':
                x.spines['bottom'].set_linewidth(spinewidth)
                x.xaxis.set_label_position('bottom')


    # Set ylimits for axes that have specified ylimits
    if ylimits is not None:
        for ylimit in ylimits:
            axes[reorder.index(ylimit[0])].set_ylim(ylimit[1], ylimit[2])

    # Plot data
    # Later- add functionality for errorbars
    for x, m in zip(axes, reorder):

        pd = plotdata[m]

        # Tuples are (x, y, color, lw, ls, marker)
        for p in pd:
            x.plot(p[0], p[1], marker=p[5], color=p[2], linewidth=p[3],
                   linestyle=p[4], zorder=10, markeredgecolor='none')

    if reverse_y is not None:
        for rev in reverse_y:
            axes[reorder.index(rev)].invert_yaxis()

    if draw_frame[0]:
        lowax = subplotnum-1
        draw.frame(fig, axes[lowax], axes[0], draw_frame[1])

    if draw_columns is not None:
        lowax = subplotnum-1
        for dc in draw_columns:
            draw.bar(fig, axes[lowax], axes[0], dc, True)

    # Alter the spacing between subplots (to pretend this is one giant plot)
    plt.subplots_adjust(hspace=plotspacing)

    # Draw horizontal bars and all rectangles, which will not move with hspace
    if draw_bars is not None:
        for bar_set, bar_ax in zip(draw_bars, bar_loc):
            draw_ax = axes[reorder.index(bar_ax)]
        # draw.bar(fig, axes[0], axes[rightax], draw_bars, False)
            draw.bar(fig, draw_ax, draw_ax, bar_set, False)


    return fig, axes