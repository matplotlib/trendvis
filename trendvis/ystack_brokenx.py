import numpy as np
import matplotlib.pyplot as plt
import draw
import plot_accessory as pa

def broken_x(figsize, plotspacing, yratios, xratios, xlimits, plotdata,
             xlabels, ylabels, xticks, yticks, dpi=80, reverse_y=None,
             reverse_x=False, ylimits=None, startside='left',
             alternate_sides=True, yaxis_shift=None, spinewidth=3,
             black_spines=False, use_lastcolor=False,
             majortick_dim=(15,5), minortick_dim=(6,3),
             tick_direction=('out', 'out'), ticklabel_formatter='%d',
             rows_to_twin=None, twins_behind=True, shift_twinnedax=0.2,
             draw_frame=(False, 3), draw_cutout=(True, 0.015),
             draw_bars=None, bar_loc=None, draw_columns=None,
             col_loc=None, draw_rectangles=None):
    """
    Creates a figure with multiple y-axes stacked over a broken x-axis.

    Vertical order of plots can easily be changed by providing a `reorder`.

    Parameters
    ----------
    figsize : tuple of ints
        Sets the overall size of the figure
    plotspacing : float
        Sets the vertical spacing between rows.  -0.35 recommended.
        If all the y-axes on one side (alternate_sides=False), >= 0.0
    yratios : list of ints
        The relative sizes of the desired rows.  Each row may
        have multiple traces and/or two y-axes (twins).
    xratios : list of ints
        The relative sizes of the columns demarcated by the x-axis breaks.
    xlimits : tuple of floats or ints
        Forced limits on the x axis.
    plotdata : list of list of tuples
        (x, y, color, linewidth, linestyle, marker, optional column number)
        One sublist per y-axis (including twin axes).  Each tuple has trace
        and formatting options.  The first tuple in each sublist determines
        axis spine color, unless use_lastcolor=True or black_spines=True.
    xlabel : string
        The x-axis label
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
        Default None.  List of indices indicating y-axes to invert.
    reverse_x : Boolean
        Default False.  If reverse_x, invert x-axis.
    ylimits : list of tuples of ints and floats
        Default None.  A list of tuples of y-axis (index, min, max), if
        limits have to be forced on a particular y-axis.
    startside : string
        Default 'left'.  ['left'|'right'].  Indicates side of the first y-axis.
        After startside, y-axis will alternate if alternate_sides is True.
    alternate_sides : Boolean
        Default True.  [True|False].  If False, all y-axis labels and scales
        will be located on startside (except for twins).
    yaxis_shift : list of floats
        Default None.  The percentage of figure size to shift the original
        y-axes from the left or right of the normal position.
        len(yaxis_shift) == len(yratios)
    spinewidth : int
        Default 3.  The width of the axis spines.
    black_spines : Boolean
        Default False. [True|False].  If True, y-axis spines, ticks are black.
    use_lastcolor : Boolean
        Default False.  [True|False].  If True, y-axis spines, ticks are the
        color of the last trace plotted in the row, rather than the first.
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
    rows_to_twin : list of ints
        Default None.  List of indicies indicating original axes to twin.
    twins_behind : Boolean
        Default True.  [True|False].  Forces twinned axis, plot(s)
        behind the original axis, plot(s).
    shift_twinnedax : float
        Default 0.2.  The percentage of figure size to shift the twinned y-axes
        from the left or right of the normal position.
    reorder : list of ints
        Default None.  The new row order.  Simple way to change plot vertical
        order without editing plotdata, yratios, ylimits, yticks, etc
    draw_frame : tuple of Boolean, int
        Default (False, 3).  [True|False].  If True, draws boxes around each
        column (defined by breaks in x-axis).  Overrides draw_cutout
    draw_cutout : tuple of (Boolean, float)
        Default True.  [True|False].  draw_cutout[1] = length.
        Draw diagonal break lines at each x-axis break.
    draw_bars : list of tuples of (min, max, color, optional alpha)
        Default None.  Draw horizontal bars across a row (given in bar_loc)
    bar_loc : list of ints
        Default None.  Row locations of the bars defined in draw_bars.
        len(draw_bars) == len(bar_loc)
    draw_columns : list of tuples of (min, max, color, optional alpha)
        Default None.  Draw vertical bars across a column (given in col_loc)
    col_loc : list of ints
        Default None.  Column locations of the columns defined in draw_columns
    draw_rectangles :
        Default None.

    """

    # Create figure
    fig = plt.figure(figsize=figsize)

    spine_begone = {'top'   : {'left' : ['bottom', 'right'],
                           'right': ['bottom', 'left'],
                           'none' : ['bottom', 'left', 'right']},
                'none'  : {'left' : ['top', 'bottom', 'right'],
                           'right': ['top', 'bottom', 'left'],
                           'none' : ['top', 'bottom', 'left', 'right']},
                'bottom': {'left' : ['top', 'right'],
                           'right': ['top', 'left'],
                           'none' : ['top', 'left', 'right']},
                'both'  : {'left' : ['right'],
                           'right': ['left']}}

    xtick_labels = {'top' : ('on', 'off'),
                    'both' : ('on', 'on'),
                    'bottom' : ('off', 'on'),
                    'none' : ('off', 'off')}

    alt_sides = {'left' : 'right',
                 'right': 'left'}

    side_inds = {'left' : 0,
                 'right': -1}

    ypos = 0
    xpos = 0
    gridrows = sum(yratios)
    gridcols = sum(xratios)
    numrows = len(yratios)
    numcols = len(xratios)
    axes = []

    # Set the reorder
    if reorder is not None:
        if len(reorder) != numrows:
            raise ValueError('`reorder` length must equal `yratios` length')

        plotdata = pa.reorder_sort(reorder, plotdata)
        yratios = pa.reorder_sort(reorder, yratios)
        yticks = pa.reorder_sort(reorder, yticks)
        ylabels = pa.reorder_sort(reorder, ylabels)
        if yaxis_shift is not None:
            yaxis_shift = pa.reorder_sort(reorder, yaxis_shift)

        if rows_to_twin is not None:
            rows_to_twin = pa.reorder_index(reorder, rows_to_twin)
        if reverse_y is not None:
            reverse_y = pa.reorder_index(reorder, reverse_y)
        if bar_loc is not None:
            bar_loc = pa.reorder_index(reorder, bar_loc)

        if ylimits is not None:
            re_ylimits = []
            for y in ylimits:
                re_ylimits.append((reorder.index[y[0]], y[1], y[2]))

    if reverse_x:
        xratios = xratios[::-1]
        xlimits = [xl[::-1] for xl in xlimits][::-1]

        new_column_order = range(0, numcols)[::-1]
        for row in plotdata:
            for plot in plotdata:
                try:
                    # check if plot is a list or tuple
                    plot[6] = new_column_order[plot[6]]
                except:
                    pass
        if col_loc is not None:
            for ind, cl in enumerate(col_loc):
                col_loc[ind] = new_column_order[ind]


    # Initialize axes and put in nested lists
    for rowspan in yratios:
        row = []

        # Axis sharing depends on x and y position
        # y axes shared within row, x axes shared within column
        for c, colspan in enumerate(xratios):
            sharex = None
            sharey = None

            if xpos > 0:
                sharey = row[0]

            if ypos > 0:
                sharex = axes[0][c]

            ax = plot.subplot2grid((gridrows, gridcols), (ypos, xpos),
                                   rowspan=rowspan, colspan=colspan,
                                   sharey=sharey, sharex=sharex)
            row.append(ax)
            xpos += colspan

        axes.append(row)
        xpos = 0
        ypos += rowspan

    # Make position and side lists
    if numrows == 1:
        pos_list = ['both']
        side_list = [startside]
    else:
        nonerows = numrows - 2
        pos_list = ['top'] + ['none']*nonerows + ['bottom']

        if alternate_sides:
            side_list = [startside]
            for i in range(1, numrows):
                newside = alt_sides[side_list[i-1]]
                side_list.append(newside)
        else:
            side_list = [startside]*totalrows

    if yaxis_shift is None:
        axshifts = [0.0]*numrows
    else:
        axshifts=yaxis_shift

    # Make twins, adjust zorder if necessary
    if rows_to_twin is not None:
        for ind in rows_to_twin:

            twin_row = []

            for ax in axes[ind]:
                twin = ax.twinx()
                if twins_behind:
                    ax.set_zorder(twin.get_zorder()+1)
                twin_row.append(twin)

            twinside = alt_sides[side_list[ind]]

            side_list.append(twinside)
            pos_list.append('none')
            axes.append(twin_row)

        try:
            axshifts.extend(shift_twinnedax)
        except:
            axshifts.extend([shift_twinnedax]*len(rows_to_twin))

    for s, (shift, side) in enumerate(zip(axshifts, side_list)):
        if side is 'left'
            axshifts[s] = 0 - shift
        else:
            axshifts[s] = 1 + shift

    # Set ticks, spines, invisible background
    for i, (row, side, pos, shift, ylabel) in enumerate(zip(axes, side_list,
                                                            pos_list, axshifts,
                                                            ylabels)):
        # Based on position, find which x-axes to label (if any)
        ltop, lbottom = xtick_labels[pos]

        # Set the x-axis tick positions and labels, set background invisible
        for ax in row:
            ax.patch.set_visible(False)

            ax.xaxis.set_tick_params(labeltop=ltop, labelbottom=lbottom)
            ax.xaxis.set_ticks_position(pos)

            # Set x labels and format ticks
            if pos != 'none':
                set_xticks()
                ax.set_xlabel(xlabel, fontsize=20, labelpad=15)
                if p!= 'bottom':
                    ax.spines['top'].set_linewidth(spinewidth)
                    ax.xaxis.set_label_position('top')
                if p != 'top':
                    ax.spines['bottom'].set_linewidth(spinewidth)

        # Find the y axis color
        if black_spines:
            ycolor = 'black'
        else:
            if use_lastcolor:
                ycolor = plotdata[i][-1][2]
            else:
                ycolor = plotdata[i][0][2]

        # find whether the data y axis is row axis 0 or -1
        data_ind = side_inds[side]

        # Get that axis, set y ticks
        data_ax = row.pop(data_ind)
        data_ax.set_yticks()
        data_ax.spines[dataside].set_position(('axes', shift))
        data_ax.yaxis.set_ticks_position(dataside)

        # Set colors and linewidths
        data_ax.spines[side].set_color(ycolor)
        data_ax.spines[side].set_linewidth(spinewidth)
        data_ax.spines[side].set_label_position(side)

        if side == 'right':
            data_ax.set_ylabel(ylabel, fontsize=18, labelpad=12, rotation=270,
                               verticalalignment='bottom')
        else:
            data_ax.set_yabel(ylabel, fontsize=18, labelpad=12)

        # Set the spines of non-y side and appropriate x-sides invisible
        for sp in spine_begone[pos][side]:
            data_ax.spines[sp].set_visible(False)

        # For the other axes int he row, set the y spines
        # and necessary x spine(s) invisible, get rid of y ticks
        for ax in row:
            ax.yaxis.set_ticks_position('none')
            plt.setp(ax.get_yticklabels(), visible=False)

            for sp in spine_begone[pos]['none']:
                ax.spines[sp].set_visible(False)

        # Put the data axis back in place in the row
        row.insert(data_ind, data_ax)

    # xlimits.  Since sharedx, only first row needs to be set
    if xlimits is not None:
        for ax, xlim in zip(axes[0], xlimits):
            ax.set_xlim(xlim[0], xlim[1])

    # ylimits and reverse_y.  Since sharedy, only first column needs to be set
    if ylimits is not None:
        for ylimit in ylimits:
            axes[ylimit[0]][0].set_ylim(ylimit[1], ylimit[2])

    if reverse_y is not None:
        for rev_y in reverse_y:
            axes[rev_y][0].invert_yaxis()

    for row, data in zip(axes, plotdata):
        for d in data:
            for colnum, ax in enumerate(row):
                try:
                    # Check if a colnum is specified, and if so, if it
                    # matches the current colnum
                    if p[6] == colnum:
                        ax.plot(d[0], d[1], marker=d[5], color=d[2],
                                linewidth=d[3], linestyle=d[4],
                                zorder=10, markeredgecolor='none')
                    # else do nothing
                except:
                    # No colnum specified
                    ax.plot(d[0], d[1], marker=d[5], color=d[2],
                            linewidth=d[3], linestyle=d[4],
                            zorder=10, markeredgecolor='none')

    plt.subplots_adjust(hspace=plotspacing)

    if draw_frame[0]:
        for i in range(0, numcols):
            draw.frame(fig, axes[numrows-1][i], axes[0][i], draw_frame[1])

    elif draw_cutout[0]:
        draw.cutout(axes, draw_cutout[1], xratios, numcols, numrows)

    if draw_columns is not None:
        lowrow = numrows - 1
        for col_settings, colnum in zip(draw_columns, col_loc):
            draw.bar(fig, axes[lowrow][colnum], axes[0][colnum],
                     col_settings, True)

    if draw_bars is not None:
        for bar_settings, rownum in zip(draw_bars, bar_loc):
            draw.bar(fig, axes[rownum][0], axes[rownum][-1],
                     bar_settings, False)

    return fig, axes