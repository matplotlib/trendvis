from __future__ import division, print_function, absolute_import
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from .gridclass import Grid


class YGrid(Grid):
    """
    Construct a plot with the y axis as the main axis and a stack of x axes.

    """

    def __init__(self, xstack_ratios, yratios=1, figsize=None,
                 startside='top', alternate_sides=True,
                 onespine_forboth=False, **kwargs):
        """
        Initialize Y_Grid

        Parameters
        ----------
        xstack_ratios : int or list of ints
            The relative sizes of the columns.  Not directly comparable
            to ``yratios``
        yratios : int or list of ints
            Default 1.  The relative sizes of the main axis row(s).
            Not directly comparable to ``xstack_ratios``
        figsize : tuple of ints or floats
            Default None. The figure dimensions in inches.
            If not provided, defaults to matplotlib rc figure.figsize.
        startside : string
            Default 'top'.  ['top'|'bottom'].  The side the leftmost x axis
            will be on.
        alternate_sides : Boolean
            Default ``True``.  [True|False].
            Stacked axis spines alternate sides or are all on ``startside``.
        onespine_forboth : Boolean
            Default ``False``.  [True|False].  If the plot stack is only 1
            column, then both main axis spines can be visible (``False``),
            or only the left spine is visible (``True``).
        **kwargs
            Any plt.figure arguments.  Passed to Grid.__init__(),
            plt.figure().

        """

        # Initialize parent class
        # Last arg is False because mainax_x
        Grid.__init__(self, xstack_ratios, yratios, False, figsize, **kwargs)

        # Set initial x and y grid positions (top left)
        xpos = 0
        ypos = 0

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

        for ax in self.axes[-1]:
            ax.yaxis.set_label_position('right')

        self.set_dataside(startside, alternate_sides)
        self.set_stackposition(onespine_forboth)

    def make_twins(self, cols_to_twin):
        """
        Twin columns

        Parameters
        ----------
        cols_to_twin : int or list of ints
            Indices of the column or columns to twin

        """

        try:
            new_twin_dim = len(cols_to_twin)
        except TypeError:
            new_twin_dim = 1
            cols_to_twin = [cols_to_twin]

        if self.twinds is None:
            self.twinds = cols_to_twin
            self.twin_dim = new_twin_dim
        else:
            self.twinds.extend(cols_to_twin)
            self.twin_dim += new_twin_dim

        self._update_total_stackdim()

        for ind in cols_to_twin:

            twin_col = []

            for ax in self.axes[ind]:
                twin = ax.twiny()
                ax.set_zorder(twin.get_zorder() + 1)
                twin_col.append(twin)

            twinside = self.alt_sides[self.dataside_list[ind]]
            self.dataside_list.append(twinside)
            self.stackpos_list.append('none')

            # Make the x axes shared
            if len(twin_col) > 1:
                twin_col[0].get_shared_x_axes().join(*twin_col)

            self.axes.append(twin_col)

        self.grid_isclean = False

    def adjust_spacing(self, wspace, adjust_bar_frame=True):
        """
        Adjust the horizontal spacing between columns.

        Parameters
        ----------
        wspace : float
            Spacing between columns
        adjust_bar_frame : Boolean
            Default True.  Realign ``matplotlib Rectangle patches``
            made via ``self.draw_bar`` and ``self.draw_frame``.

        """

        self.fig.subplots_adjust(wspace=wspace)

        if adjust_bar_frame:
            self.adjust_bar_frame()

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

                data_ind, data_ax = self._pop_data_ax(col, dataside)

                # Set tick marks and label position, spines
                data_ax.xaxis.set_ticks_position(dataside)

                for sp in self.spine_begone[stackpos][dataside]:
                    data_ax.spines[sp].set_visible(False)

                for ax in col:
                    # Remove tick marks, tick labels
                    ax.xaxis.set_ticks_position('none')
                    ax.xaxis.set_tick_params(labeltop='off', labelbottom='off')

                    # Remove spines
                    for sp in self.spine_begone[stackpos]['none']:
                        ax.spines[sp].set_visible(False)

                self._replace_data_ax(col, data_ind, data_ax)

        self.grid_isclean = True

    def get_axis(self, xpos, ypos=0, is_twin=False, twinstance=0):
        """
        Get axis at a particular x, y position.

        If a twin is desired, then there are two options:
          1.  Set ``xpos`` to actual storage position in ``self.axes``
              Can find twin ``xpos`` via ``self.get_twin_colnum()``
          2.  Set ``xpos`` to the physical position in ``YGrid``, set
              ``is_twin``=``True``, and if there is more than one twin at that
              location, set ``twinstance`` to indicate desired twin (e.g.
              0 indicates the first twin to be created in that col position).

        For original axes, storage position and physical position are the same,
        except if twins exist and negative ``xpos`` indices are used.

        Parameters
        ----------
        xpos : int
            The column that the axis is located in.
        ypos : int
            Default 0.  The row the axis is in.
        is_twin : Boolean
            Default ``False``. If ``is_twin``, ``self.get_axis()`` will grab
            the twin at the given ``xpos``, ``ypos`` rather than the
            original axis.
        twinstance : int
            Default 0.  If there is more than one twin at ``xpos``, ``ypos``,
            then this will indicate which twin to grab.

        Returns
        -------
        ax : ``Axes`` instance
            ``matplotlib Axes`` instance at the given ``xpos``, ``ypos``,
            (``twinstance``)

        """

        if is_twin:
            # xpos corresponds to twind(s), which are in a particular order
            # Get indices of where xpos appears in the list of twins
            twindices = [i for i, tw in enumerate(self.twinds) if tw == xpos]

            # Get position of desired instance of xpos
            which_twin = twindices[twinstance]

            # New xpos is the original axis count, plus the location of twin
            xpos = self.stackdim + which_twin

        # Subgrid (col, x), ax (row, y)
        ax = self.axes[xpos][ypos]

        return ax

    def get_twin_colnum(self, xpos, twinstance=None):
        """
        Original axes are easily located by column number in ``self.axes``.
        If there are are multiple twins, finding those in ``self.axes``
        may be difficult, esp. if twins were created haphazardly

        This prints the index required by ``self.axes`` to fetch the
        twin column.

        Parameters
        ----------
        xpos : int
            The column that was twinned
        twinstance : int
            Default ``None``, print all twin column indices at ``xpos``.
            Indicates which twin column index to print

        """

        twindices = [i for i, tw in enumerate(self.twinds) if tw == xpos]

        if twinstance is None and len(twindices) > 1:
            newxpos = [i + self.stackdim for i in twindices]
        elif twinstance is None:
            newxpos = [self.stackdim + twindices[0]]
        else:
            newxpos = [self.stackdim + twindices[twinstance]]

        print('The twin(s) of column ' + str(xpos) + ' are stored in ' +
              '`self.axes` as column(s):')

        for nx in newxpos:
            print(nx)

    def set_all_ticknums(self, xticks, yticks, logxscale='none',
                         logyscale='none'):
        """
        Set the y and x axis scales, the y and x axis ticks (if linear), and
        the tick number format.  Wrapper around ``Grid.set_yaxis_ticknum()``,
        ``Grid.set_xaxis_ticknum()``.

        Parameters
        ----------
        xticks : list of tuples
            List of (major, minor) tick mark multiples.  Used to set major and
            minor locators.  One tuple per x axis (original stack + twins).
            Use ``None`` to skip setting a major, minor ``MultipleLocator``
            for an axis
        yticks : list of tuples
            List of (major, minor) tick mark multiples.  Used to set major and
            minor locators.  One tuple per main axis.
            Use ``None`` to skip setting a major, minor ``MultipleLocator``
            for an axis
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

        xscale = self._make_lists(self.total_stackdim, logxscale,
                                  'linear', 'log')
        yscale = self._make_lists(self.mainax_dim, logyscale, 'linear', 'log')

        for col, xt, xsc in zip(self.axes, xticks, xscale):
            for ax, yt, ysc in zip(col, yticks, yscale):

                if yt is not None or ysc == 'log':
                    self.set_yaxis_ticknum(ax, yt, scale=ysc)
                if xt is not None or xsc == 'log':
                    self.set_xaxis_ticknum(ax, xt, scale=xsc)

    def ticknum_format(self, ax='all', xformatter='%d', yformatter='%d'):
        """
        Set tick number formatters for x and/or y axes.

        Parameters
        ----------
        ax : string or axes instance
            Default 'all', cycle through axes and set formatters.
            If axes instance, will only set x and/or y formatter of that axes
            instance.  Can acquire axis using ``self.get_axis()``
        xformatter : string or list of strings
            Default '%d'.  String formatting magic to apply to all x axes
            (string) or individual x axes (list of strings,
            length = ``self.total_stackdim``).  Can use ``None`` to skip
            setting ``xformatter``, or insert ``None`` into list to skip
            setting ``xformatter`` for a particular axis column
        yformatter : string
            Default '%d'.  String formatting magic to apply to all y axes.
            Can use ``None`` to skip setting ``yformatter``

        """

        if ax != 'all':
            if xformatter is not None:
                xfrmttr = FormatStrFormatter(xformatter)
                ax.xaxis.set_major_formatter(xfrmttr)
            if yformatter is not None:
                yfrmttr = FormatStrFormatter(yformatter)
                ax.yaxis.set_major_formatter(xfrmttr)

        else:
            if xformatter is not None:
                if type(xformatter) is str:
                    xfrmttr = FormatStrFormatter(xformatter)
                    for col in self.axes:
                        for ax in col:
                            ax.xaxis.set_major_formatter(xfrmttr)
                else:
                    for xf, col in zip(xformatter, self.axes):
                        if xf is not None:
                            xfrmttr = FormatStrFormatter(xf)
                            for ax in col:
                                ax.xaxis.set_major_formatter(xfrmttr)

            if yformatter is not None:
                yfrmttr = FormatStrFormatter(yformatter)
                for col in self.axes:
                    for ax in col:
                        ax.yaxis.set_major_formatter(yfrmttr)

    def reverse_yaxis(self, reverse_y='all', adjust_bar_frame=True):
        """
        Reverse any or all y axes.

        Parameters
        ----------
        reverse_y : string or list of ints
            Default 'all'.  'all' or list of indices of the y axes to be
            reversed accepted.  If unsure of index for a twin x axis in
            ``self.axes``, find using ``self.get_twin_colnum()``.
        adjust_bar_frame : Boolean
            Default True.  Realign ``matplotlib Rectangle patches``
            made via ``self.draw_bar`` and ``self.draw_frame``.

        """

        if reverse_y == 'all':
            reverse_y = range(0, self.mainax_dim)

        # Invert y axis of each axis in the first column
        for r in reverse_y:
            self.axes[0][r].invert_yaxis()

        if adjust_bar_frame:
            self.adjust_bar_frame()

    def reverse_xaxis(self, reverse_x='all', adjust_bar_frame=True):
        """
        Reverse any or all x axes.

        Parameters
        ----------
        reverse_x : string or list of ints
            Default 'all'.  'all' or list of indices of the x axes to be
            reversed accepted.  If unsure of index for a twin x axis in
            ``self.axes``, find using ``self.get_twin_colnum()``.
        adjust_bar_frame : Boolean
            Default True.  Realign ``matplotlib Rectangle patches``
            made via ``self.draw_bar`` and ``self.draw_frame``.

        """

        if reverse_x == 'all':
            reverse_x = range(0, self.total_stackdim)

        # Invert x axis of first axis in each column
        for r in reverse_x:
            self.axes[r][0].invert_xaxis()

        if adjust_bar_frame:
            self.adjust_bar_frame()

    def set_xlim(self, xlim, adjust_bar_frame=True):
        """
        Set x limits.

        Parameters
        ----------
        xlim : list of tuples of ints and/or floats
            List of (column, min, max).  If xdim is 1, then column is ignored.
            Also, if only one x axis needs ``xlim``, can just pass the tuple.
            If unsure of column index for a twin x axis in ``self.axes``,
            find using ``self.get_twin_colnum()``
        adjust_bar_frame : Boolean
            Default True.  Realign ``matplotlib Rectangle patches``
            made via ``self.draw_bar`` and ``self.draw_frame``.

        """

        if self.total_stackdim == 1:
            try:
                xlim.extend([])
            except AttributeError:
                pass
            else:
                xlim = xlim[0]

            for col in self.axes:
                for ax in col:
                    ax.set_xlim(xlim[-2], xlim[-1])

        else:
            try:
                xlim.extend([])
            except AttributeError:
                xlim = [xlim]

            for xl in xlim:
                for ax in self.axes[xl[0]]:
                    ax.set_xlim(xl[1], xl[2])

        if adjust_bar_frame:
            self.adjust_bar_frame()

    def set_ylim(self, ylim, adjust_bar_frame=True):
        """
        Set y limits.

        Parameters
        ----------
        ylim : List of tuples of ints and/or flaots
            List of (row, min, max).  If ydim is 1, then row is ignored.
            Also, if only one y axis need ``ylim``, can just pass a tuple.
        adjust_bar_frame : Boolean
            Default True.  Realign ``matplotlib Rectangle patches``
            made via ``self.draw_bar`` and ``self.draw_frame``.

        """

        if self.mainax_dim == 1:
            try:
                ylim.extend([])
            except AttributeError:
                pass
            else:
                ylim = ylim[0]

            for col in self.axes:
                for ax in col:
                    ax.set_ylim(ylim[-2], ylim[-1])

        else:
            try:
                ylim.extend([])
            except AttributeError:
                ylim = [ylim]

            for yl in ylim:
                for col in self.axes:
                    col[yl[0]].set_ylim(yl[1], yl[2])

        if adjust_bar_frame:
            self.adjust_bar_frame()

    def set_ticks(self, row='all', column='all', xy_axis='both', which='both',
                  major_dim=(6, 2), minor_dim=(4, 1), labelsize=10, pad=10,
                  major_tickdir='out', minor_tickdir='out'):
        """
        Set x and/or y axis ticks for all or specified axes.

        Does not set axis color

        Parameters
        ----------
        row : string or list of ints
            Default 'all'.  The rows containing the axes that need tick
            parameters adjusted, 'all' or list of indices
        column: string or list of ints
            Default 'all'.  The columns containing the axes that need tick
            parameters adjusted, 'all' or list of indices.  If unsure of column
            index for a twin x axis in ``self.axes``, find using
            ``self.get_twin_colnum()``
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
            Default 10.  Tick label fontsize.
        pad : int
            Default 10.  Spacing between the tick and tick label.
        major_tickdir : string
            Default 'out'.  ['out'|'in'|'inout'].  The major tick direction.
        minor_tickdir : string
            Default 'out'.  ['out'|'in'|'inout'].  The minor tick direction.

        """

        if row == 'all':
            row = range(0, self.mainax_dim)
        if column == 'all':
            column = range(0, self.total_stackdim)

        if which != 'major':
            Grid._set_ticks(self, column, row, xy_axis, 'minor', minor_dim,
                            labelsize, pad, minor_tickdir)

        if which != 'minor':
            Grid._set_ticks(self, column, row, xy_axis, 'major', major_dim,
                            labelsize, pad, major_tickdir)

    def draw_cutout(self, di=0.025, lw='default', **kwargs):
        """
        Draw cut marks to signifiy broken y axes.

        Only drawn when ``self.mainax_dim`` > 1.

        Parameters
        ----------
        di : float
            Default 0.025.  The dimensions of the cutout mark as a
            fraction of the smallest axis length.
        lw : int
            Default 'default'.  If 'default', ``lw = self.spinewidth``.
        **kwargs
            Passed to ``axes.plot()``.  Any valid ``kwargs``.

        """

        if self.mainax_dim > 1:

            # Adjust di so that cutouts will look exactly the same
            # on every axis, no matter their relative sizes
            miny = min(self.yratios)
            y = [di * (miny / y) for y in self.yratios]

            minx = min(self.xratios)
            x0 = di * (minx / self.xratios[0])
            x1 = di * (minx / self.xratios[-1])

            # Left and right x position
            left_x = (-(2 * x0), (2 * x0))
            right_x = (1 - (2 * x1), 1 + (2 * x1))

            right_ind = self.stackdim - 1

            if lw == 'default':
                lw = self.spinewidth

            l_ax = self.axes[0][0]
            r_ax = self.axes[right_ind][0]
            lower = (-y[0], y[0])

            # first axes in columns, lower only
            kwargs = dict(transform=l_ax.transAxes, clip_on=False,
                          color='black', lw=lw, **kwargs)
            l_ax.plot(left_x, lower, **kwargs)

            kwargs.update(transform=r_ax.transAxes)
            r_ax.plot(right_x, lower, **kwargs)

            # Middle axes
            for i in range(1, self.mainax_dim - 1):
                l_ax = self.axes[0][i]
                r_ax = self.axes[right_ind][i]
                upper = (1 - y[i], 1 + y[i])
                lower = (-y[i], y[i])

                kwargs.update(transform=l_ax.transAxes)
                l_ax.plot(left_x, upper, **kwargs)
                l_ax.plot(left_x, lower, **kwargs)

                kwargs.update(transform=r_ax.transAxes)
                r_ax.plot(right_x, upper, **kwargs)
                r_ax.plot(right_x, lower, **kwargs)

            # Last axes in columns, upper only
            l_ax = self.axes[0][-1]
            r_ax = self.axes[right_ind][-1]
            upper = (1 - y[-1], 1 + y[-1])

            kwargs.update(transform=l_ax.transAxes)
            l_ax.plot(left_x, upper, **kwargs)

            kwargs.update(transform=r_ax.transAxes)
            r_ax.plot(right_x, upper, **kwargs)

    def set_xlabels(self, xlabels, fontsize=None, labelpad=12, **kwargs):
        """
        Tool for setting all x axis labels at once. Can skip labelling an axis
        by providing a ``None`` in corresponding poiition in list.

        Parameters
        ----------
        xlabels : list of strings
            The list of labels, one per x-axis.  Insert ``None`` in list to
            skip an axis.
        fontsize : int
            Default None. The font size of ``xlabels``
        labelpad : int
            Default 12.  The spacing between the tick labels adn the axis
            labels.
        **kwargs
            Passed to ``axes.set_xlabel()``.
            Any ``matplotlib Text`` properties

        Notes
        -----
        Caution- this will set twin axis labels in the order that twins were
        created, which may not correspond to physical position in grid.

        """

        for col, side, xl in zip(self.axes, self.dataside_list, xlabels):
            if xl is not None:

                if side == 'top':
                    ind = 0
                else:
                    ind = -1

                col[ind].xaxis.set_label_position(side)
                col[ind].set_xlabel(xl, fontsize=fontsize,
                                    labelpad=labelpad, **kwargs)
