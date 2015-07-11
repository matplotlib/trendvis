from __future__ import division, print_function, absolute_import
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from .gridclass import Grid


class XGrid(Grid):
    """
    Construct a plot with the x axis as the main axis and a stack of y axes.

    """

    def __init__(self, ystack_ratios, xratios=1, figsize=(10, 10),
                 startside='left', alternate_sides=True,
                 onespine_forboth=False, **kwargs):
        """
        Initialize X_Grid

        Parameters
        ----------
        ystack_ratiosratios : int or list of ints
            The relative sizes of the rows.  Not directly comparable
            to ``xratios``
        xratios : int or list of ints
            Default 1. The relative sizes of the main axis column(s).
            Not directly comparable to ``ystack_ratios``
        figsize : tuple of ints or floats
            Default (10,10).  The figure dimensions in inches
        startside : string
            Default 'left'.  ['left'|'right'].  The side the topmost y axis
            will be on.
        alternate_sides : Boolean
            Default ``True``.  [True|False].
            Stacked axis spines alternate sides or are all on ``startside``.
        onespine_forboth : Boolean
            Default ``False``.  [True|False].  If the plot stack is only 1 row,
            then both main axis spines can be visible (``False``),
            or only the bottom spine (``True``).
        **kwargs
            Any plt.figure arguments.  Passed to Grid.__init__(),
            plt.figure()

        """

        # Initialize parent class
        # Last arg is True because mainax_x
        Grid.__init__(self, xratios, ystack_ratios, True, figsize, **kwargs)

        # Set initial x and y grid positions (top left)
        xpos = 0
        ypos = 0

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

        for ax in self.axes[0]:
            ax.xaxis.set_label_position('top')

        self.set_dataside(startside, alternate_sides)
        self.set_stackposition(onespine_forboth)

    def make_twins(self, rows_to_twin):
        """
        Twin rows

        Parameters
        ----------
        rows_to_twin : int or list of ints
            Indices of the row or rows to twin

        """

        try:
            new_twin_dim = len(rows_to_twin)
        except TypeError:
            new_twin_dim = 1
            rows_to_twin = [rows_to_twin]

        if self.twinds is None:
            self.twinds = rows_to_twin
            self.twin_dim = new_twin_dim
        else:
            self.twinds.extend(rows_to_twin)
            self.twin_dim += new_twin_dim

        self._update_total_stackdim()

        for ind in rows_to_twin:

            twin_row = []

            for ax in self.axes[ind]:
                twin = ax.twinx()
                ax.set_zorder(twin.get_zorder() + 1)
                twin_row.append(twin)

            twinside = self.alt_sides[self.dataside_list[ind]]
            self.dataside_list.append(twinside)
            self.stackpos_list.append('none')

            # Make the y-axes shared
            if len(twin_row) > 1:
                twin_row[0].get_shared_y_axes().join(*twin_row)

            self.axes.append(twin_row)

        self.grid_isclean = False

    def adjust_spacing(self, hspace, adjust_bar_frame=True):
        """
        Adjust the vertical spacing between rows.

        Parameters
        ----------
        hspace : float
            Spacing between rows
        adjust_bar_frame : Boolean
            Default True.  Realign ``matplotlib Rectangle patches``
            made via ``self.draw_bar`` and ``self.draw_frame``.

        """

        self.fig.subplots_adjust(hspace=hspace)

        if adjust_bar_frame:
            self.adjust_bar_frame()

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

                data_ind, data_ax = self._pop_data_ax(row, dataside)

                # Set tick marks and label position, spines
                data_ax.yaxis.set_ticks_position(dataside)

                for sp in self.spine_begone[stackpos][dataside]:
                    data_ax.spines[sp].set_visible(False)

                for ax in row:
                    # Remove tick marks, tick labels
                    ax.yaxis.set_ticks_position('none')
                    ax.yaxis.set_tick_params(labelright='off', labelleft='off')

                    # Remove spines
                    for sp in self.spine_begone[stackpos]['none']:
                        ax.spines[sp].set_visible(False)

                self._replace_data_ax(row, data_ind, data_ax)

        self.grid_isclean = True

    def get_axis(self, ypos, xpos=0, is_twin=False, twinstance=0):
        """
        Get axis at a particular x, y location.

        If a twin is desired, then there are two options:
          1.  Set ``ypos`` to actual storage position in ``self.axes``
              Can find twin ``ypos`` via ``self.get_twin_rownum()``
          2.  Set ``ypos`` to the physical position in ``XGrid``, set
              ``is_twin``=``True``, and if there is more than one twin at that
              location, set ``twinstance`` to indicate desired twin (e.g.
              0 indicates the first twin to be created in that row position).

        For original axes, storage position and physical position are the same,
            except if twins exist and negative ``ypos`` indices are used.

        Parameters
        ----------
        ypos : int
            The row that the axis is located in
        xpos : int
            Default 0.  The column the axis is in
        is_twin : Boolean
            Default ``False``.  If ``is_twin``, ``self.get_axis()`` will grab
            the twin at the given physical ``xpos``, ``ypos`` rather than the
            original axis.
        twinstance : int
            Default 0. If there is more than one twin at ``xpos``, ``ypos``,
            then this will indicate which twin to grab

        Returns
        -------
        ax : ``Axes`` instance
            ``matplotlib Axes`` instance at the given ``xpos``, ``ypos``,
            (``twinstance``)

        """

        if is_twin:
            # ypos corresponds to twind(s), which are in a particular order
            # Get indices of where ypos appears in the list of twins
            twindices = [i for i, tw in enumerate(self.twinds) if tw == ypos]

            # Get position of desired instance of ypos
            which_twin = twindices[twinstance]

            # New ypos is the original axis count, plus the location of twin
            ypos = self.stackdim + which_twin

        # Subgrid (row, y), ax (col, x)
        ax = self.axes[ypos][xpos]

        return ax

    def get_twin_rownum(self, ypos, twinstance=None):
        """
        Original axes are easily located by row number in ``self.axes``.
        If there are multiple twins, finding those in ``self.axes`` may be
        difficult, esp. if twins were created haphazardly.

        This prints the index required by ``self.axes`` to fetch the
        twin row.

        Parameters
        ----------
        ypos : int
            The row that was twinned
        twinstance : int
            Default ``None``, print all twin row indices at ``ypos``.
            Indicates which twin row index to print

        """

        twindices = [i for i, tw in enumerate(self.twinds) if tw == ypos]

        if twinstance is None and len(twindices) > 1:
            newypos = [i + self.stackdim for i in twindices]
        elif twinstance is None:
            newypos = [self.stackdim + twindices[0]]
        else:
            newypos = [self.stackdim + twindices[twinstance]]

        print('The twin(s) of row ' + str(ypos) + ' are stored in ' +
              '`self.axes` as row(s):')

        for ny in newypos:
            print(ny)

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
            minor locators.  One tuple per main axis.
            Use ``None`` to skip setting a major, minor ``MultipleLocator``
            for an axis
        yticks : list of tuples
            List of (major, minor) tick mark multiples.  Used to set major and
            minor locators.  One tuple per y axis (original stack + twins).
            Use ``None`` to skip setting a major, minor ``MultipleLocator``
            for an axis
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

        xscale = self._make_lists(self.mainax_dim, logxscale, 'linear', 'log')
        yscale = self._make_lists(self.total_stackdim, logyscale,
                                  'linear', 'log')

        for row, yt, ysc in zip(self.axes, yticks, yscale):
            for ax, xt, xsc in zip(row, xticks, xscale):

                if yt is not None or ysc is 'log':
                    self.set_yaxis_ticknum(ax, yt, scale=ysc)
                if xt is not None or xsc is 'log':
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
            Can use ``None`` to skip setting ``xformatter``
        yformatter : string or list of strings
            Default '%d'.  String formatting magic to apply to all y axes
            (string) or individual y axes (list of strings,
            length = ``self.total_stackdim``).  Can use ``None`` to
            skip setting ``yformatter``, or insert ``None`` into list to
            skip setting formatter for a particular axis row

        """

        if ax is not 'all':
            if xformatter is not None:
                xfrmttr = FormatStrFormatter(xformatter)
                ax.xaxis.set_major_formatter(xfrmttr)
            if yformatter is not None:
                yfrmttr = FormatStrFormatter(yformatter)
                ax.yaxis.set_major_formatter(xfrmttr)

        else:
            if yformatter is not None:
                if type(yformatter) is str:
                    yfrmttr = FormatStrFormatter(yformatter)
                    for row in self.axes:
                        for ax in row:
                            ax.yaxis.set_major_formatter(yfrmttr)
                else:
                    for yf, row in zip(yformatter, self.axes):
                        if yf is not None:
                            yfrmttr = FormatStrFormatter(yf)
                            for ax in row:
                                ax.yaxis.set_major_formatter(yfrmttr)

            if xformatter is not None:
                xfrmttr = FormatStrFormatter(xformatter)
                for row in self.axes:
                    for ax in row:
                        ax.xaxis.set_major_formatter(xfrmttr)

    def reverse_yaxis(self, reverse_y='all', adjust_bar_frame=True):
        """
        Reverse all or any y axis.

        Parameters
        ----------
        reverse_y : string or list of ints
            Default 'all'.  'all' or list of indices of the y axes to be
            reversed accepted.  If unsure of index for a twin y axis in
            ``self.axes``, find using ``self.get_twin_rownum()``
        adjust_bar_frame : Boolean
            Default True.  Realign ``matplotlib Rectangle patches``
            made via ``self.draw_bar`` and ``self.draw_frame``.

        """

        if reverse_y is 'all':
            reverse_y = range(0, self.total_stackdim)

        # Invert yaxis of first axis in each row
        for r in reverse_y:
            self.axes[r][0].invert_yaxis()

        if adjust_bar_frame:
            self.adjust_bar_frame()

    def reverse_xaxis(self, reverse_x='all', adjust_bar_frame=True):
        """
        Reverse all or any x axis.

        Parameters
        ----------
        reverse_x : string or list of ints
            Default 'all'.  'all' or list of indices of the x axes to be
            reversed accepted.  If unsure of index for a twin y axis in
            ``self.axes``, find using ``self.get_twin_rownum()``
        adjust_bar_frame : Boolean
            Default True.  Realign ``matplotlib Rectangle patches``
            made via ``self.draw_bar`` and ``self.draw_frame``.

        """

        if reverse_x is 'all':
            reverse_x = range(0, self.mainax_dim)

        # Invert x axis of each axis in first row
        for r in reverse_x:
            self.axes[0][r].invert_xaxis()

        if adjust_bar_frame:
            self.adjust_bar_frame()

    def set_ylim(self, ylim, adjust_bar_frame=True):
        """
        Set y limits.

        Parameters
        ----------
        ylim : list of tuples of ints and/or floats
            List of (row, min, max).  If ydim is 1, then row is ignored.
            Also, if only one y axis needs ``ylim``, can just pass the tuple.
            If unsure of row index for a twin y axis in ``self.axes``,
            find using ``self.get_twin_rownum()``
        adjust_bar_frame : Boolean
            Default True.  Realign ``matplotlib Rectangle patches``
            made via ``self.draw_bar`` and ``self.draw_frame``.

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

        if adjust_bar_frame:
            self.adjust_bar_frame()

    def set_xlim(self, xlim, adjust_bar_frame=True):
        """
        Set x limits.

        Parameters
        ----------
        xlim : List of tuples of ints and/or flaots
            List of (column, min, max).  If xdim is 1, then column is ignored.
            Also, if only one x axis needs ``xlim``, can just pass a tuple.
        adjust_bar_frame : Boolean
            Default True.  Realign ``matplotlib Rectangle patches``
            made via ``self.draw_bar`` and ``self.draw_frame``.

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
                    row[xl[0]].set_xlim(xl[1], xl[2])

        if adjust_bar_frame:
            self.adjust_bar_frame()

    def set_ticks(self, row='all', column='all', xy_axis='both', which='both',
                  major_dim=(6, 2), minor_dim=(4, 1), labelsize=10, pad=10,
                  major_dir='out', minor_dir='out'):
        """
        Set x and/or y axis ticks for all or specified axes.

        Does not set axis color.

        Parameters
        ----------
        row : string or list of ints
            Default 'all'.  The rows containing the axes that need tick
            parameters adjusted, 'all' or list of indices.  If unsure of row
            index for a twin y axis in ``self.axes``, find using
            ``self.get_twin_rownum()``
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
            Grid._set_ticks(self, row, column, xy_axis, 'minor', minor_dim,
                            labelsize, pad, minor_dir)

        if which is not 'minor':
            Grid._set_ticks(self, row, column, xy_axis, 'major', major_dim,
                            labelsize, pad, major_dir)

    def draw_cutout(self, di=0.025, lw='default', **kwargs):
        """
        Draw cut marks to signify broken x axes.

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
            minx = min(self.xratios)
            x = [di * (minx / x) for x in self.xratios]

            miny = min(self.yratios)
            y0 = di * (miny / self.yratios[0])
            y1 = di * (miny / self.yratios[-1])

            # Upper and lower y position
            upper_y = (1 - (2 * y0), 1 + (2 * y0))
            lower_y = (-(2 * y1), (2 * y1))

            low_ind = self.stackdim - 1

            if lw is 'default':
                lw = self.spinewidth

            top_ax = self.axes[0][0]
            low_ax = self.axes[low_ind][0]
            right = (1 - x[0], 1 + x[0])

            # first axes in rows, right only
            kwargs = dict(transform=top_ax.transAxes, clip_on=False,
                          color='black', lw=lw, **kwargs)
            top_ax.plot(right, upper_y, **kwargs)

            kwargs.update(transform=low_ax.transAxes)
            low_ax.plot(right, lower_y, **kwargs)

            # Middle axes
            for i in range(1, self.mainax_dim - 1):
                top_ax = self.axes[0][i]
                low_ax = self.axes[low_ind][i]
                left = (-x[i], x[i])
                right = (1 - x[i], 1 + x[i])

                kwargs.update(transform=top_ax.transAxes)
                top_ax.plot(left, upper_y, **kwargs)
                top_ax.plot(right, upper_y, **kwargs)

                kwargs.update(transform=low_ax.transAxes)
                low_ax.plot(left, lower_y, **kwargs)
                low_ax.plot(right, lower_y, **kwargs)

            # Last axes in rows, left only
            top_ax = self.axes[0][-1]
            low_ax = self.axes[low_ind][-1]
            left = (-x[-1], x[-1])

            kwargs.update(transform=top_ax.transAxes)
            top_ax.plot(left, upper_y, **kwargs)

            kwargs.update(transform=low_ax.transAxes)
            low_ax.plot(left, lower_y, **kwargs)

    def set_ylabels(self, ylabels, fontsize=14, labelpad=12, **kwargs):
        """
        Tool for setting all y axis labels at once.  Can skip labelling an axis
        by providing a ``None`` in corresponding position in list.

        Parameters
        ----------
        ylabels : list of strings
            The list of labels, one per y-axis.  Insert ``None`` in list to
            skip an axis.
        fontsize : int
            Default 14.  The font size of ``ylabels``
        labelpad : int
            Default 12.  The spacing between the tick labels and the axis
            labels.
        **kwargs
            Passed to ``axes.set_ylabel()``.
            Any ``matplotlib Text`` properties

        Notes
        -----
        Caution- this will set twin axis labels in the order that twins were
        created, which may not correspond to physical position in grid.

        """

        for row, side, yl in zip(self.axes, self.dataside_list, ylabels):
            if yl is not None:
                if side == 'right':
                    row[-1].yaxis.set_label_position('right')
                    row[-1].set_ylabel(yl, fontsize=fontsize,
                                       labelpad=labelpad, rotation=270,
                                       verticalalignment='bottom', **kwargs)
                else:
                    row[0].yaxis.set_label_position('left')
                    row[0].set_ylabel(yl, fontsize=fontsize, labelpad=labelpad,
                                      **kwargs)
