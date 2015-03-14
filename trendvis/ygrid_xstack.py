import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from gridclass import Grid


class YGrid(Grid):
    """
    Class for making a plot with the Y axis as the main axis
        and a stack of x axes

    """

    def __init__(self, xratios, yratios, figsize, startside='top',
                 alternate_sides=True, onespine_forboth=False):
        """
        Initialize Y_Grid

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
            Default 'top'.  ['top'|'bottom'].  The side the leftmost x axis
            will be on.
        alternate_sides : Boolean
            Default True.  [True|False].
            Stacked axis spines alternate sides or are all on startside.
        onespine_forboth : Boolean
            Default False.  [True|False].  If the plot stack is only 1 column,
            then both main axis spines can be visible (False),
            or only the left spine is visible (True).

        """

        # Initialize parent class
        # Last arg is False because mainax_x
        Grid.__init__(self, xratios, yratios, False)

        # Set initial x and y grid positions (top left)
        xpos = 0
        ypos = 0

        self.fig = plt.figure(figsize=figsize)

        # Create axes column by column
        for colspan in self.xratios:
            col = []

            for r, rowspan in enumerate(self.yratios):
                sharex = None
                sharey = None

                # All axes in column share x axis with first in column
                if ypos > 0:
                    sharex = col[0]

                # All axes in row share y axis with first in row
                if xpos > 0:
                    sharey = self.axes[0][r]

                ax = plt.subplot2grid((self.gridrows, self.gridcols),
                                      (ypos, xpos), rowspan=rowspan,
                                      colspan=colspan, sharex=sharex,
                                      sharey=sharey)

                ax.patch.set_visible(False)

                col.append(ax)
                ypos += rowspan

            self.axes.append(col)

            # Reset y position to top, move to next x position
            ypos = 0
            xpos += colspan

        self.set_dataside(startside, alternate_sides)
        self.set_stackposition(onespine_forboth)

    def make_twins(self, cols_to_twin):
        """
        Twin columns

        Parameters
        ----------
        cols_to_twin : list of ints
            Indices of the columns to twin

        """

        if self.twinds is None:
            self.twinds = cols_to_twin
            self.twin_dim = len(cols_to_twin)
        else:
            self.twinds.extend(cols_to_twin)
            self.twin_dim += len(cols_to_twin)

        self.update_total_stackdim()

        for ind in cols_to_twin:

            twin_col = []

            for ax in self.axes[ind]:
                twin = ax.twiny()
                ax.set_zorder(twin.get_zorder() + 1)
                twin_col.append(twin)

            twinside = self.alt_sides[self.dataside_list[ind]]
            self.dataside_list.append(twinside)
            self.stackpos_list.append('none')
            self.axes.append(twin_col)

        self.grid_isclean = False

    def adjust_spacing(self, wspace):
        """
        Adjust the horizontal spacing between columns.

        Parameters
        ----------
        wspace : float

        """

        plt.subplots_adjust(wspace=wspace)

    def cleanup_grid(self):
        """
        Remove unnecessary spines from grid

        """

        if not self.grid_isclean:

            for col, dataside, stackpos in zip(self.axes, self.dataside_list,
                                               self.stackpos_list):

                # Get mainax tick labelling settings
                lleft, lright = self.mainax_ticks[stackpos]

                # Set mainax tick parameters and positions
                for ax in col:
                    ax.yaxis.set_tick_params(labelleft=lleft,
                                             labelright=lright)
                    ax.yaxis.set_ticks_position(stackpos)

                data_ind, data_ax = self.pop_data_ax(col, dataside)

                # Set tick marks and label position, spines
                data_ax.xaxis.set_ticks_position(dataside)

                for sp in self.spine_begone[stackpos][dataside]:
                    data_ax.spines[sp].set_visible(False)

                for ax in col:
                    # Remove tick marks, tick labels
                    ax.xaxis.set_ticks_position('none')
                    plt.setp(ax.get_xticklabels(), visible=False)

                    # Remove spines
                    for sp in self.spine_begone[stackpos]['none']:
                        ax.spines[sp].set_visible(False)

                self.replace_data_ax(col, data_ind, data_ax)

        self.grid_isclean = True

    def set_ticknums(self, xticks, yticks, logxscale='none', logyscale='none'):
        """
        Set the y and x axis scales, the y and x axis ticks (if linear), and
            the tick number format.

        Parameters
        ----------
        xticks : list of tuples
            List of (major, minor) tick mark multiples.  Used to set major and
            minor locators.  One tuple per x axis (original stack + twins)
        yticks : list of tuples
            List of (major, minor) tick mark multiples.  Used to set major and
            minor locators.  One tuple per main axis.

        Keyword Arguments
        -----------------
        logxscale : string or list of ints
            Default 'none'.  ['none'|'all'|list of x-axis indices].
            Indicate which x axes should be log scaled instead of linear.
        logyscale : string or list of ints
            Default 'none'.  ['none'|'all'|list of y-axis indices].
            Indicate which y axes should be log scaled instead of linear.

        """

        if len(xticks) != self.total_stackdim:
            raise ValueError('xticks provided for ' + str(len(xticks)) + '/' +
                             str(self.total_stackdim) + ' x-axes')
        if len(yticks) != self.mainax_dim:
            raise ValueError('yticks provided for ' + str(len(yticks)) + '/' +
                             str(self.mainax_dim) + ' y-axes')

        xscale = self.make_lists(self.total_stackdim, logxscale,
                                 'linear', 'log')
        yscale = self.make_lists(self.mainax_dim, logyscale, 'linear', 'log')

        for col, xt, xsc in zip(self.axes, xticks, xscale):
            for ax, yt, ysc in zip(col, yticks, yscale):

                self.yaxis_ticknum(ax, ysc, yt)
                self.xaxis_ticknum(ax, xsc, xt)

    def ticknum_format(self, xformatter='%d', yformatter='%d'):
        """
        Set tick number formatters for x and/or y axes.

        Keyword Arguments
        -----------------
        xformatter : string or list of strings
            String formatting magic to apply to all x axes (string) or
            individual x axes (list of strings, length = self.total_stackdim)
        yformatter : string or list of strings
            String formatting magic to apply to all y axes (string) or
            individual y axes (list of strings, length = self.mainax_dim)

        """

        if xformatter is not None:
            if type(xformatter) is str:
                xfrmttr = FormatStrFormatter(xformatter)
                xfrmttr_ls = [xfrmttr] * self.total_stackdim
            else:
                xfrmttr_ls = []
                for xf in xformatter:
                    xfrmttr = FormatStrFormatter(xf)
                    xfrmttr_ls.append(xfrmttr)

            for col, xf in zip(self.axes, xfrmttr_ls):
                for ax in col:
                    ax.xaxis.set_major_formatter(xf)

        if yformatter is not None:
            if type(yformatter) is str:
                yfrmttr = FormatStrFormatter(yformatter)
                yfrmttr_ls = [yfrmttr] * self.mainax_dim
            else:
                yfrmttr_ls = []
                for yf in yformatter:
                    yfrmttr = FormatStrFormatter(yf)
                    yfrmttr_ls.append(yfrmttr)

            for col in self.axes:
                for ax, yf in zip(col, yfrmttr_ls):
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
            reverse_y = range(0, self.mainax_dim)

        # Invert y axis of each axis in the first column
        for r in reverse_y:
            self.axes[0][r].invert_yaxis()

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
            reverse_x = range(0, self.total_stackdim)

        # Invert x axis of first axis in each column
        for r in reverse_x:
            self.axes[r][0].invert_xaxis()
