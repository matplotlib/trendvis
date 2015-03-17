import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from gridclass import Grid


class XGrid(Grid):
    """
    Class for making a plot with the x axis as the main axis
        and a stack of y axes

    """

    def __init__(self, xratios, yratios, figsize, startside='left',
                 alternate_sides=True, onespine_forboth=False):
        """
        Initialize X_Grid

        Parameters
        ----------
        xratios : int or list of ints
            The relative sizes of the columns.  Not directly comparable
            to yratios
        yratios : int or list of ints
            The relative sizes of the rows.  Not directly comparable to xratios
        figsize : tuple of ints or floats
            The figure dimensions in inches

        Keyword Arguments
        -----------------
        startside : string
            Default 'left'.  ['left'|'right'].  The side the topmost y axis
            will be on.
        alternate_sides : Boolean
            Default True.  [True|False].
            Stacked axis spines alternate sides or are all on startside.
        onespine_forboth : Boolean
            Default False.  [True|False].  If the plot stack is only 1 row,
            then both main axis spines can be visible,
            or only the bottom spine.

        """

        # Initialize parent class
        # Last arg is True because mainax_x
        Grid.__init__(self, xratios, yratios, True)

        # Set initial x and y grid positions (top left)
        xpos = 0
        ypos = 0

        self.fig = plt.figure(figsize=figsize)

        # Create axes row by row
        for rowspan in self.yratios:
            row = []

            for c, colspan in enumerate(self.xratios):
                sharex = None
                sharey = None

                # All axes in a row share y axis with first axis in row
                if xpos > 0:
                    sharey = row[0]

                # All axes in a column share x axis with first axis in column
                if ypos > 0:
                    sharex = self.axes[0][c]

                ax = plt.subplot2grid((self.gridrows, self.gridcols),
                                      (ypos, xpos), rowspan=rowspan,
                                      colspan=colspan, sharey=sharey,
                                      sharex=sharex)

                ax.patch.set_visible(False)

                row.append(ax)
                xpos += colspan

            self.axes.append(row)

            # Reset x position to left side, move to next y position
            xpos = 0
            ypos += rowspan

        self.set_dataside(startside, alternate_sides)
        self.set_stackposition(onespine_forboth)

    def make_twins(self, rows_to_twin):
        """
        Twin rows

        Parameters
        ----------
        rows_to_twin : list of ints
            Indices of the rows to twin

        """

        if self.twinds is None:
            self.twinds = rows_to_twin
            self.twin_dim = len(rows_to_twin)
        else:
            self.twinds.extend(rows_to_twin)
            self.twin_dim += len(rows_to_twin)

        self.update_total_stackdim()

        for ind in rows_to_twin:

            twin_row = []

            for ax in self.axes[ind]:
                twin = ax.twinx()
                ax.set_zorder(twin.get_zorder() + 1)
                twin_row.append(twin)

            twinside = self.alt_sides[self.dataside_list[ind]]
            self.dataside_list.append(twinside)
            self.stackpos_list.append('none')
            self.axes.append(twin_row)

        self.grid_isclean = False

    def adjust_spacing(self, hspace):
        """
        Adjust the vertical spacing between rows.

        Parameters
        ----------
        hspace : float

        """

        plt.subplots_adjust(hspace=hspace)

    def cleanup_grid(self):
        """
        Remove unnecessary spines from grid

        """

        if not self.grid_isclean:

            for row, dataside, stackpos in zip(self.axes, self.dataside_list,
                                               self.stackpos_list):

                # Get mainax tick labelling settings
                ltop, lbottom = self.mainax_ticks[stackpos]

                # Set mainax tick parameters and positions
                for ax in row:
                    ax.xaxis.set_tick_params(labeltop=ltop,
                                             labelbottom=lbottom)
                    ax.xaxis.set_ticks_position(stackpos)

                data_ind, data_ax = self.pop_data_ax(row, dataside)

                # Set tick marks and label position, spines
                data_ax.yaxis.set_ticks_position(dataside)

                for sp in self.spine_begone[stackpos][dataside]:
                    data_ax.spines[sp].set_visible(False)

                for ax in row:
                    # Remove tick marks, tick labels
                    ax.yaxis.set_ticks_position('none')
                    plt.setp(ax.get_yticklabels(), visible=False)

                    # Remove spines
                    for sp in self.spine_begone[stackpos]['none']:
                        ax.spines[sp].set_visible(False)

                self.replace_data_ax(row, data_ind, data_ax)

        self.grid_isclean = True

    def set_ticknums(self, xticks, yticks, logxscale='none', logyscale='none'):
        """
        Set the y and x axis scales, the y and x axis ticks (if linear), and
            the tick number format.

        Parameters
        ----------
        xticks : list of tuples
            List of (major, minor) tick mark multiples.  Used to set major and
            minor locators.  One tuple per main axis
        yticks : list of tuples
            List of (major, minor) tick mark multiples.  Used to set major and
            minor locators.  One tuple per y axis (original stack + twins)

        Keyword Arguments
        -----------------
        logxscale : string or list of ints
            Default 'none'.  ['none'|'all'|list of x-axis indices].
            Indicate which x axes should be log scaled instead of linear.
        logyscale : string or list of ints
            Default 'none'.  ['none'|'all'|list of y-axis indices].
            Indicate which y axes should be log scaled instead of linear.

        """

        if len(xticks) != self.mainax_dim:
            raise ValueError('xticks provided for ' + str(len(xticks)) + '/' +
                             str(self.mainax_dim) + ' x-axes')
        if len(yticks) != self.total_stackdim:
            raise ValueError('yticks provided for ' + str(len(yticks)) + '/' +
                             str(self.total_stackdim) + ' y-axes')

        xscale = self.make_lists(self.mainax_dim, logxscale, 'linear', 'log')
        yscale = self.make_lists(self.total_stackdim, logyscale,
                                 'linear', 'log')

        for row, yt, ysc in zip(self.axes, yticks, yscale):
            for ax, xt, xsc in zip(row, xticks, xscale):

                self.yaxis_ticknum(ax, ysc, yt)
                self.xaxis_ticknum(ax, xsc, xt)

    def ticknum_format(self, xformatter='%d', yformatter='%d'):
        """
        Set tick number formatters for x and/or y axes.

        Keyword Arguments
        -----------------
        xformatter : string or list of strings
            String formatting magic to apply to all x axes (string) or
            individual x axes (list of strings, length = self.mainax_dim)
        yformatter : string or list of strings
            String formatting magic to apply to all y axes (string) or
            individual y axes (list of strings, length = self.total_stackdim)

        """

        if xformatter is not None:
            if type(xformatter) is str:
                xfrmttr = FormatStrFormatter(xformatter)
                xfrmttr_ls = [xfrmttr] * self.mainax_dim
            else:
                xfrmttr_ls = []
                for xf in xformatter:
                    xfrmttr = FormatStrFormatter(xf)
                    xfrmttr_ls.append(xfrmttr)

            for row in self.axes:
                for ax, xf in zip(row, xfrmttr_ls):
                    ax.xaxis.set_major_formatter(xf)

        if yformatter is not None:
            if type(yformatter) is str:
                yfrmttr = FormatStrFormatter(yformatter)
                yfrmttr_ls = [yfrmttr] * self.total_stackdim
            else:
                yfrmttr_ls = []
                for yf in yformatter:
                    yfrmttr = FormatStrFormatter(yf)
                    yfrmttr_ls.append(yfrmttr)

            for row, yf in zip(self.axes, yfrmttr_ls):
                for ax in row:
                    ax.yaxis.set_major_formatter(yf)

    def reverse_yaxis(self, reverse_y='all'):
        """
        Reverse all or any y axis.

        Keyword Arguments
        -----------------
        reverse_y : string or list of ints
            Default 'all'.  'all' or list of indices of the y axes to be
            reversed accepted.

        """

        if reverse_y is 'all':
            reverse_y = range(0, self.total_stackdim)

        # Invert yaxis of first axis in each row
        for r in reverse_y:
            self.axes[r][0].invert_yaxis()

    def reverse_xaxis(self, reverse_x='all'):
        """
        Reverse all or any x axis.

        Keyword Arguments
        -----------------
        reverse_x : string or list of ints
            Default 'all'.  'all' or list of indices of the x axes to be
            reversed accepted.

        """

        if reverse_x is 'all':
            reverse_x = range(0, self.mainax_dim)

        # Invert x axis of each axis in first row
        for r in reverse_x:
            self.axes[0][r].invert_xaxis()

    def set_ylim(self, ylim):
        """
        Set y limits.

        Parameters
        ----------
        ylim : list of tuples of ints and/or floats
            List of (row, min, max).  If ydim is 1, then row is ignored.
            Also, if only one y axis needs ylim, can just pass the tuple

        """

        if self.total_stackdim == 1:
            try:
                ylim.extend([])
            except AttributeError:
                pass
            else:
                ylim = ylim[0]

            for row in self.axes:
                for ax in row:
                    ax.set_ylim(ylim[-2], ylim[-1])

        else:
            try:
                ylim.extend([])
            except AttributeError:
                ylim = [ylim]

            for yl in ylim:
                for ax in self.axes[yl[0]]:
                    ax.set_ylim(yl[1], yl[2])

    def set_xlim(self, xlim):
        """
        Set x limits.

        Parameters
        ----------
        xlim : List of tuples of ints and/or flaots
            List of (column, min, max).  If xdim is 1, then column is ignored.
            Also, if only one x axis needs xlim, can just pass a tuple.

        """

        if self.mainax_dim == 1:
            try:
                xlim.extend([])
            except AttributeError:
                pass
            else:
                xlim = xlim[0]

            for row in self.axes:
                for ax in row:
                    ax.set_xlim(xlim[-2], xlim[-1])

        else:
            try:
                xlim.extend([])
            except AttributeError:
                xlim = [xlim]

            for xl in xlim:
                for row in self.axes:
                    row[xl].set_xlim(xlim[1], xlim[2])

    def set_ticks(self, row='all', column='all', xy_axis='both', which='both',
                  major_dim=(6 , 2), minor_dim=(4 , 1), labelsize=10, pad=10,
                  major_dir='out', minor_dir='out'):
        """
        Set x and/or y axis ticks for all or specified axes.

        Does not set axis color.

        Keyword Arguments
        -----------------
        row : string or list of ints
            Default 'all'.  The rows containing the axes that need tick
            parameters adjusted, 'all' or list of indices
        column: string or list of ints
            Default 'all'.  The columns containing the axes that need tick
            parameters adjusted, 'all' or list of indices
        xy_axis : string
            Default 'both'.  ['x'|'y'|'both']
        which : string
            Default 'both'.  ['major'|'minor'|'both'], the set of ticks
            to adjust.
        major_dim : tuple of ints or floats
            Default (6, 2).  The (length, width) of the major ticks.
        minor_dim : tuple of ints or floats
            Default (4, 1).  The (length, width) of the minor ticks.
        labelsize : int
            Default 10.  Tick label fontsize in points.
        pad : int
            Default 10.  Spacing between the tick and tick label in points.
        major_tickdir : string
            Default 'out'.  ['out'|'in'|'inout'].  The major tick direction.
        minor_tickdir : string
            Default 'out'.  ['out'|'in'|'inout'].  The minor tick direction.

        """

        if row is 'all':
            row = range(0, self.total_stackdim)
        if column is 'all':
            column = range(0, self.mainax_dim)

        if which is not 'major':
            Grid.set_ticks(self, row, column, xy_axis, 'minor', minor_dim,
                           labelsize, pad, minor_dir)

        if which is not 'minor':
            Grid.set_ticks(self, row, column, xy_axis, 'major', major_dim,
                           labelsize, pad, major_dir)
