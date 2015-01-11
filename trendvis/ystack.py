import numpy as np
import matplotlib.pyplot as plt
import draw
import plot_accessory as pa

def multi_y(figsize, plotspacing, yratios, xlimits, plotdata,
            xlabel, ylabels, xticks, yticks, line_kwargs={}, reverse_y=None,
            reverse_x=False, ylimits=None, startside='left',
            alternate_sides=True, yaxis_shift=None, spinewidth=3,
            black_spines=False, use_lastcolor=False,
            majortick_dim=(15,5), minortick_dim=(6,3),
            tick_direction=('out', 'out'), ticklabel_formatter='%d',
            axes_to_twin=None, twins_behind=True, shift_twinnedax=0.2,
            reorder=None, draw_frame=(False, 3), draw_bars=None,
            bar_location=None, draw_columns=None, draw_rectangles=None):
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
    yratios : list of ints
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
        Default None.  Draw horizontal bars across a row (given in bar_location)
    bar_location : list of ints
        Default None.  Row locations of the bars defined in draw_bars.
        len(draw_bars) == len(bar_location)
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
    fig = plt.figure(figsize=figsize)

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

    xtick_labels = {'top' : ('on', 'off'),
                    'both' : ('on', 'on'),
                    'bottom' : ('off', 'on'),
                    'none' : ('off', 'off')}

    alt_sides = {'left' : 'right',
                 'right': 'left'}

    default_linekwargs = {'marker' : 'o',
                          'ls' : '-',
                          'markeredgecolor' : 'none',
                          'zorder' : 10,
                          'lw' : spinewidth-1}

    default_kwargs.update(line_kwargs)

    # Initialize subplot row position, total grid rows, and axes list
    ypos = 0
    gridrows = sum(yratios)
    numrows = len(yratios)
    axes = []

    if reorder is not None:
        if len(reorder) != numrows:
            raise ValueError('len(`reorder`) != len(`yratios`)')

        (plotdata, yratios, yticks, ylabels, yaxis_shift,
            axes_to_twin, reverse_y, bar_location,
            ylimits) = pa.reordering(reorder, plotdata, yratios, yticks,
                                     ylabels, yaxis_shift, axes_to_twin,
                                     reverse_y, bar_location, ylimits)

    # Make subplot grid and get list of axes
    for rowspan in yratios:
        sharex=None

        if ypos > 0:
            sharex = axes[0]

        ax = plt.subplot2grid((gridrows,1), (ypos,0), rowspan=rowspan,
                              sharex=sharex)
        axes.append(ax)
        ypos += rowspan

    # Make position and side lists for original axes
    if numrows == 1:
        pos_list = ['both']
        side_list = [startside]
    else:
        nonerows = numrows - 2
        post_list = ['top'] + ['none']*nonerows + ['bottom']

        if alternate_sides:
            side_list = [startside]
            for i in range(1, numrows):
                newside = alt_sides[side_list[i-1]]
                side_list.append(newside)
        else:
            side_list = [startside]*numrows

    if yaxis_shift is None:
        axshifts = [0.0]*numrows
    else:
        axshifts = yaxis_shift

    if axes_to_twin is not None:
        for ind in axes_to_twin:
            twin = axes[ind].twinx()

            if twins_behind:
                axes[ind].set_zorder(twin.get_zorder()+1)


            twinside = alt_sides[side_list[ind]]

            side_list.append(twinside)
            pos_list.append('none')
            axes.append(twin)

        try:
            axshifts.extend(shift_twinnedax)
        except:
            axshifts.extend([shift_twinnedax]*len(axes_to_twin))

    for s, (shift, side) in enumerate(zip(axshifts, side_list)):
        if side is 'left':
            axshifts[s] = 0 - shift
        else:
            axshifts[s] = 1 + shift

    for i, (ax, side, pos, shift, ylabel) in enumerate(zip(axes, side_list,
                                                           pos_list, axshifts,
                                                           ylabels)):
        ltop, lbottom = xtick_labels[pos]
        # Take care of the x tick visibility and position
        ax.xaxis.set_tick_params(labeltop=ltop, labelbottom=lbottom)
        ax.xaxis.set_ticks_position(pos)

        ax.patch.set_visible(False)

        if pos != 'none':
            pa.set_xticks(ax, xticks, 'black', majortick_dim, minortick_dim,
                          tick_direction, 16, 10)
            ax.set_xlabel(xlabel, fontsize=20, labelpad=15)

            if pos != 'bottom':
                ax.spines['top'].set_linewidth(spinewidth)
                ax.xaxis.set_label_position('top')
            if pos != 'top':
                ax.spines['bottom'].set_linewidth(spinewidth)

        if black_spines:
            ycolor = 'black'
        else:
            if use_lastcolor:
                ycolor = plotdata[i][-1][2]
            else:
                ycolor = plotdata[i][0][2]

        # Set ytick parameters and position
        # Set y-axis position
        ax.set_yticks(ax, yticks, ycolor, majortick_dim, minortick_dim,
                      tick_direction, 16, 10)
        ax.spines[side].set_position(('axes', shift))
        ax.yaxis.set_ticks_position(side)

        # Set colors and linewidths
        ax.spines[side].set_color(ycolor)
        ax.spines[side].set_linewidth(spinewidth)
        ax.spines[side].set_label_position(side)

        # Set ylabel parameters
        if side == 'right':
            ax.set_ylabel(ylabel, fontsize=18, labelpad=12, rotation=270,
                          verticalalignment='bottom')
        else:
            ax.set_ylabel(ylabel, fontsize=18, labelpad=12)

        # Get rid of remaining spines
        for sp in spine_begone[pos][side]:
            ax.spines[sp].set_visible(False)

    if xlimits is not None:
        axes[0].set_xlim(xlimits[0], xlimits[1])

    if reverse_x:
        axes[0].invert_xaxis()

    if ylimits is not None:
        for ylimit in ylimits:
            axes[ylimit[0]].set_ylim(ylimit[1], ylimit[2])

    if reverse_y is not None:
        for rev_y in reverse_y:
            axes[rev_y].invert_yaxis()

    # Plot data
    for ax, pd in zip(axes, plotdata):

        # Tuples are (x, y, color, kwargs)
        for p in pd:

            kwargs = default_linekwargs.copy()
            kwargs.update(p[3])

            x.errorbar(p[0], p[1], color=p[2], **kwargs)

    # Alter the spacing between subplots (to pretend this is one giant plot)
    # Must be done before drawing the horizontal bars
    plt.subplots_adjust(hspace=plotspacing)

    if draw_frame[0]:
        lowax = numrows-1
        draw.frame(fig, axes[lowax], axes[0], draw_frame[1])

    if draw_columns is not None:
        lowax = numrows-1
        for dc in draw_columns:
            draw.bar(fig, axes[lowax], axes[0], dc, True)

    # Draw horizontal bars
    if draw_bars is not None:
        for bar_set, bar_ax in zip(draw_bars, bar_location):
            draw_ax = axes[bar_ax]
            draw.bar(fig, draw_ax, draw_ax, bar_set, False)

    return fig, axes