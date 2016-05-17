from __future__ import division, print_function, absolute_import
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import matplotlib.lines as lines


class Grid(object):
    """
    Superclass for ``YGrid`` and ``XGrid``.

    """

    def __init__(self, xratios, yratios, mainax_x, figsize, **kwargs):
        """
        Initialize grid attributes.  Should only be called through
        ``XGrid`` or ``YGrid`` subclasses.

        Parameters
        ----------
        xratios : int or list of ints
            The relative sizes of the columns.  Not directly comparable
            to ``yratios``
        yratios : int or list of ints
            The relative sizes of the rows.  Not directly comparable to
            ``xratios``
        mainax_x : Boolean
            [True|False].  Indicates if x is the main axis.  Determines
            some attributes
        figsize : tuple of ints or floats
            The figure dimensions in inches. If None, defaults to matplotlib
            rc figure.figsize.
        **kwargs
            Any plt.figure arguments

        """
        figsize = figsize or plt.rcParams['figure.figsize']
        self.fig = plt.figure(figsize=figsize)

        self.gridrows, self.yratios = self._ratios_arelists(yratios)
        self.gridcols, self.xratios = self._ratios_arelists(xratios)

        self.numrows = len(self.yratios)
        self.numcols = len(self.xratios)

        self.axes = []

        self.bf_urcorners = []
        self.bf_llcorners = []
        self.bf_patchinds = []
        self.bf_uraxis = []
        self.bf_llaxis = []

        self.relative_shifts = None
        self.stack_shifts = None

        self.twinds = None
        self.twin_dim = 0
        self.reltwin_shifts = None
        self.twin_shifts = None

        self.grid_isclean = False

        self.spinelist = ['top', 'bottom', 'left', 'right']
        self.spinewidth = 1

        if mainax_x:
            self.mainax_id = 'x'
            self.stackax_id = 'y'
            self.stackdim = self.numrows
            self.mainax_dim = self.numcols
            self.sp1 = 'right'
            self.sp2 = 'left'

            self.startpos = 'top'

            self.mainax_ticks = {'top'   : ('on', 'off'),
                                 'both'  : ('on', 'on'),
                                 'bottom': ('off', 'on'),
                                 'none'  : ('off', 'off')}

            self.alt_sides = {'left' : 'right',
                              'right': 'left'}

            self.side_inds = {'left' : 0,
                              'right': -1}

            self.spine_begone = {'top' : {'left' : ['bottom', 'right'],
                                          'right': ['bottom', 'left'],
                                          'none' : ['bottom', 'left',
                                                    'right']},
                                 'none' : {'left' : ['top', 'bottom', 'right'],
                                           'right': ['top', 'bottom', 'left'],
                                           'none' : ['top', 'bottom', 'left',
                                                     'right']},
                                 'bottom': {'left' : ['top', 'right'],
                                            'right': ['top', 'left'],
                                            'none' : ['top', 'left',
                                                      'right']},
                                 'both' : {'left' : ['right'],
                                           'right': ['left'],
                                           'none' : ['right', 'left']}}
        else:
            self.mainax_id = 'y'
            self.stackax_id = 'x'
            self.stackdim = self.numcols
            self.mainax_dim = self.numrows
            self.sp1 = 'top'
            self.sp2 = 'bottom'

            self.startpos = 'left'

            self.mainax_ticks = {'left' : ('on', 'off'),
                                 'both' : ('on', 'on'),
                                 'right': ('off', 'on'),
                                 'none' : ('off', 'off')}

            self.alt_sides = {'top'   : 'bottom',
                              'bottom': 'top'}

            self.side_inds = {'top'   : 0,
                              'bottom': -1}

            self.spine_begone = {'left' : {'top'   : ['bottom', 'right'],
                                           'bottom': ['top', 'right'],
                                           'none'  : ['bottom', 'top',
                                                      'right']},
                                 'none' : {'top'   : ['bottom', 'left',
                                                      'right'],
                                           'bottom': ['top', 'left', 'right'],
                                           'none'  : ['top', 'bottom', 'left',
                                                      'right']},
                                 'right': {'top'   : ['bottom', 'left'],
                                           'bottom': ['top', 'left'],
                                           'none'  : ['top', 'bottom',
                                                      'left']},
                                 'both' : {'top'   : ['bottom'],
                                           'bottom': ['top'],
                                           'none'  : ['top', 'bottom']}}

        self._update_total_stackdim()

    def set_dataside(self, startside, alternate_sides):
        """
        Set the ``dataside_list`` that indicates which stacked ax spine will be
        the visible data spine.

        Parameters
        ----------
        startside : string
            ['left'|'right'] or ['top'|'bottom'].  The side the first row
            (column) in ``self.axes`` will have its y (x) axis spine on.
        alternate_sides : Boolean
            [True|False].  Stacked axis spines alternate sides or are all on
            ``startside``.

        """

        self.dataside_list = [startside]

        if alternate_sides:
            for i in range(1, self.stackdim):
                newside = self.alt_sides[self.dataside_list[i - 1]]
                self.dataside_list.append(newside)

        else:
            self.dataside_list = self.dataside_list * self.stackdim

        self._update_twinsides()

    def set_stackposition(self, onespine_forboth):
        """
        Set ``self.stackpos_list`` indicating which non-stacked axes are shown.

        Parameters
        ----------
        onespine_forboth : Boolean
            [True|False].  If the plot stack is only 1 row (column), then
            both main axis spines may be visible (False), or only the bottom
            (left) spine.

        """

        alt_pos = {'left': 'right',
                   'top' : 'bottom'}

        # Position list in the case of a stack of 1
        if self.stackdim == 1:
            if onespine_forboth:
                if self.mainax_id is 'x':
                    self.startpos = 'bottom'
                self.stackpos_list = [self.startpos]
            else:
                self.stackpos_list = ['both']

        else:
            num_nones = self.stackdim - 2
            self.stackpos_list = ([self.startpos] + ['none'] * num_nones +
                                  [alt_pos[self.startpos]])

    def move_spines(self, axis_shift=None, twin_shift=None):
        """
        Wrapper around self.set_relative_axshift(),
        self.set_absolute_axshift(), self.excecute_spineshift()

        Parameters
        -----------------
        axis_shift : float or list of floats
            Default None.  Set universal (float) or individual (list of
            floats where len(``axis_shift``) = ``self.stackdim``)
            axis spine shift
        twin_shift : float or list of floats
            Default None.  Set universal (float) or individual (list of
            floats where len(``twin_shift``) = ``self.twin_dim``)
            twinned axis spine shift.
        """

        self.set_relative_axshift(axis_shift=axis_shift, twin_shift=twin_shift)
        self.set_absolute_axshift()
        self.excecute_spineshift()

    def set_relative_axshift(self, axis_shift=None, twin_shift=None):
        """
        Set relative shift of stacked axis spines.

        Parameters
        -----------------
        axis_shift : float or list of floats
            Default None.  Set universal (float) or individual (list of
            floats where len(``axis_shift``) = ``self.stackdim``)
            axis spine shift
        twin_shift : float or list of floats
            Default None.  Set universal (float) or individual (list of
            floats where len(``twin_shift``) = ``self.twin_dim``)
            twinned axis spine shift.

        """

        if axis_shift is not None:
            try:
                # Check if iterable
                axis_shift[0]
            except:
                # if not a list, apply same shift to both
                self.relative_shifts = [axis_shift] * self.stackdim
            else:
                if len(axis_shift) != self.stackdim:
                    print('Warning:  len(axis_shift) != ' + str(self.stackdim))
                    self.relative_shifts = [axis_shift[0]] * self.stackdim
                else:
                    self.relative_shifts = axis_shift

        if twin_shift is not None and self.twinds is not None:
            try:
                twin_shift[0]
            except:
                self.reltwin_shifts = [twin_shift] * self.twin_dim
            else:
                if len(twin_shift) != self.twin_dim:
                    print('Warning:  len(twin_shift) != number of twinned ax!')
                    self.reltwin_shifts = [twin_shift[0]] * self.twin_dim
                else:
                    self.reltwin_shifts = twin_shift

    def set_absolute_axshift(self):
        """
        Translate ``self.relative_shifts`` to absolute values.  Absolute values
        are based on which side the axis to be moved appears.

        """

        if self.relative_shifts is not None:

            # Reset aboslute shifts
            self.stack_shifts = []

            for shift, dataside in zip(self.relative_shifts,
                                       self.dataside_list):

                if dataside == self.sp2:
                    self.stack_shifts.append(0 - shift)
                else:
                    self.stack_shifts.append(1 + shift)

        if self.reltwin_shifts is not None:
            self.twin_shifts = []

            for shift, dataside in zip(self.reltwin_shifts,
                                       self.dataside_list[self.stackdim:]):
                if dataside == self.sp2:
                    self.twin_shifts.append(0 - shift)
                else:
                    self.twin_shifts.append(1 + shift)

    def excecute_spineshift(self):
        """
        Move the stacked spines around.

        """

        if self.stack_shifts is not None:

            for subgrid, ds, sh in zip(self.axes, self.dataside_list,
                                       self.stack_shifts):

                for ax in subgrid:
                    ax.spines[ds].set_position(('axes', sh))

        if self.twin_shifts is not None:

            for subgrid, ds, sh in zip(self.axes[self.stackdim:],
                                       self.dataside_list[self.stackdim:],
                                       self.twin_shifts):
                for ax in subgrid:
                    ax.spines[ds].set_position(('axes', sh))

    def move_one_spine(self, ax, which, shift):
        """
        Move ``which`` stacked ``ax`` spine by relative ``shift``.

        Parameters
        ----------
        ax : axes instance
            The axes instance which needs a spine moved.
            Can be obtained via ``self.get_axis()``
        which : string
            If ``XGrid``, ['left'|'right'], ``YGrid`` ['top'|'bottom'].
            Used to indentify spine and to calculate outward shift
            from ``shift``.
        shift : float
            Change in position relative to figure size.

        """

        if which is self.sp1:
            shift = 1 + shift
        elif which is self.sp2:
            shift = 0 - shift
        else:
            raise ValueError('Not a stacked ax spine')

        ax.spines[which].set_position(('axes', shift))

    def reset_spineshift(self):
        """
        Reset all spines to normal position.

        """

        shifts = {'x': {'left'   : 0.0,
                        'right'  : 1.0},
                  'y': {'bottom' : 0.0,
                        'top'    : 1.0}}

        sd = shifts[self.mainax_id]

        for subgrid in self.axes:
            for ax in subgrid:
                for key in sd:
                    ax.spines[key].set_position(('axes', sd[key]))

        self.relative_shifts = None
        self.stack_shifts = None
        self.reltwin_shifts = None
        self.twin_shifts = None

    def reveal_spines(self):
        """
        Undo the spine-hiding actions of ``self.cleanup_grid()``.

        """

        for subgrid in self.axes:
            for ax in subgrid:
                for sp in self.spinelist:
                    ax.spines[sp].set_visible(True)

        self.grid_isclean = False

    def set_ax_visibility(self, ax, which, visible):
        """
        Hide (``visible``=``False``) or show (``visible``=``True``) an axis
        side (``which``).  Will hide/show spine, ticks, and ticklabels.

        Parameters
        ----------
        ax : axes instance
            The axes instance to set spine, tick visibility for.
            Can be obtained via ``self.get_axis()``
        which : string
            The axis spine, ticks, ticklabels to hide/show.
            ['left'|'right'|'top'|'bottom']
        visible : Boolean
            Set visible or invisible

        """

        ax.spines[which].set_visible(visible)

        if which is 'left' or which is 'right':
            if visible:
                ytick_dict = {'both'   : {'left' : 'both',
                                          'right': 'both'},
                              'left'   : {'left' : 'left',
                                          'right': 'both'},
                              'right'  : {'left' : 'both',
                                          'right': 'right'},
                              'unknown': {'left' : 'left',
                                          'right': 'right'},
                              'default': {'left' : 'both',
                                          'right': 'both'}}
            else:
                ytick_dict = {'both'   : {'left' : 'right',
                                          'right': 'left'},
                              'left'   : {'left' : 'none',
                                          'right': 'left'},
                              'right'  : {'left' : 'right',
                                          'right': 'none'},
                              'unknown': {'left' : 'none',
                                          'right': 'none'},
                              'default': {'left' : 'right',
                                          'right': 'left'}}
            # Key is new tick pos, value is labelright, labelleft
            ylabeldict = {'left' : ['off', 'on'],
                          'right': ['on', 'off'],
                          'both' : ['on', 'on'],
                          'none' : ['off', 'off']}

            old_tickpos = ax.yaxis.get_ticks_position()
            new_tickpos = ytick_dict[old_tickpos][which]
            ax.yaxis.set_ticks_position(new_tickpos)
            r, f = ylabeldict[new_tickpos]
            ax.yaxis.set_tick_params(labelright=r, labelleft=f)
            self.grid_isclean = False

        if which is 'top' or which is 'bottom':
            if visible:
                xtick_dict = {'both'   : {'top'   : 'both',
                                          'bottom': 'both'},
                              'top'    : {'top'   : 'top',
                                          'bottom': 'both'},
                              'bottom' : {'top'   : 'both',
                                          'bottom': 'bottom'},
                              'unknown': {'top'   : 'top',
                                          'bottom': 'bottom'},
                              'default': {'top'   : 'both',
                                          'bottom': 'both'}}
            else:
                xtick_dict = {'both'   : {'top'   : 'bottom',
                                          'bottom': 'top'},
                              'top'    : {'top'   : 'none',
                                          'bottom': 'top'},
                              'bottom' : {'top'   : 'bottom',
                                          'bottom': 'none'},
                              'unknown': {'top'   : 'none',
                                          'bottom': 'none'},
                              'default': {'top'   : 'bottom',
                                          'bottom': 'top'}}
            # Key is new tick pos, value is labeltop, labelbottom
            xlabeldict = {'bottom': ['off', 'on'],
                          'top'   : ['on', 'off'],
                          'none'  : ['off', 'off']}

            old_tickpos = ax.xaxis.get_ticks_position()
            new_tickpos = xtick_dict[old_tickpos][which]
            ax.xaxis.set_ticks_position(new_tickpos)
            t, b = xlabeldict[new_tickpos]
            ax.xaxis.set_tick_params(labeltop=t, labelbottom=b)
            self.grid_isclean = False

    def set_spinewidth(self, spinewidth):
        """
        Edit the linewidth of the axis spines. ``self.spinewidth`` used as
        default linewidths in drawing frames and cutouts.

        Parameters
        ----------
        spinewidth : int
            Linewidth in points.

        """

        for subgrid in self.axes:
            for ax in subgrid:
                for sp in self.spinelist:
                    ax.spines[sp].set_linewidth(spinewidth)

        self.spinewidth = spinewidth

    def remove_twins(self):
        """
        Get rid of all twinned axes.

        """

        for subgrid in self.axes[self.stackdim:]:
            for ax in subgrid:
                self.fig.delaxes(ax)

        self.twinds = None
        self.twin_dim = 0
        self.reltwin_shifts = None
        self.twin_shifts = None
        self.dataside_list = self.dataside_list[:self.stackdim]
        self.stackpos_list = self.stackpos_list[:self.stackdim]
        self.axes = self.axes[:self.stackdim]

        self._update_total_stackdim()

    def set_xaxis_ticknum(self, axis, xticks, scale='linear'):
        """
        Set x tick scale and, if linear, major and minor tick locators.

        Parameters
        ----------
        axis : ``matplotlib Axes`` instance
            ``Axes`` instance to set x-axis scale and potentially
            major and minor tick locators.  Can get with ``self.get_axis()``
        xticks : tuple
            Tuple of (major, minor) x axis tick multiples.
        scale : string
            Default 'linear'.  ['log'|'linear'].  X axis scale.

        """

        if scale is 'linear':

            xmajor_loc = MultipleLocator(xticks[0])
            xminor_loc = MultipleLocator(xticks[1])

            axis.xaxis.set_major_locator(xmajor_loc)
            axis.xaxis.set_minor_locator(xminor_loc)

        else:
            axis.set_xscale(scale)

    def set_yaxis_ticknum(self, axis, yticks, scale='linear'):
        """
        Set y tick scale and, if linear, major and minor tick locators.

        Parameters
        ----------
        axis : ``matplotlib Axes`` instance
            ``Axes`` instance to set y-axis scale and potentially
            major and minor tick locators.  Can get with ``self.get_axis()``
        xticks : tuple
            Tuple of (major, minor) y axis tick multiples.
        scale : string
            Default 'linear'.  ['log'|'linear'].  Y axis scale.

        """

        if scale is 'linear':
            ymajor_loc = MultipleLocator(yticks[0])
            yminor_loc = MultipleLocator(yticks[1])

            axis.yaxis.set_major_locator(ymajor_loc)
            axis.yaxis.set_minor_locator(yminor_loc)

        else:
            axis.set_yscale(scale)

    def autocolor_spines(self, ticks_only=False):
        """
        Set the axis stacked ax spine and/or tick color based on the color of
        the first line on the axis.

        If no line is found on an axis, then ``autocolor_spines()`` will
        default to the color of the first item in the list of axis children.

        Parameters
        ----------
        ticks_only : Boolean
            Default ``False``.  If ``True``, then the tick color will change
            and the axis color will not.  If ``False``, both will change.

        """

        for subgrid in self.axes:
            for ax in subgrid:
                # Default is first child, unless the first line is found
                # later among the children. Should account for difference
                # among recent versions of matplotlib
                child = ax.get_children()[0]
                for kid in ax.get_children():
                    if isinstance(kid, lines.Line2D):
                        child = kid
                        break
                try:
                    color = child.get_color()
                except AttributeError:
                    color = child.get_facecolor()
                    if len(color) < 3:
                        color = color[0]

                try:
                    self.set_axcolor(ax, color, ticks_only=ticks_only)
                except:
                    pass

    def set_axcolor(self, ax, color, ticks_only=False, spines_only=False):
        """
        Set the stacked ax spine and tick color of the given Axes.

        Parameters
        ----------
        ax : ``matplotlib Axes`` instance
            Can get with ``self.get_axis()``
        color : string, tuple of floats
            Any color accepted by ``matplotlib``.
        ticks_only : Boolean
            Default ``False``.  If ``True``, then the tick color will change
            and the axis color will not.  If ``False``, both will change.

        """

        if not spines_only:
            ax.tick_params(axis=self.stackax_id, color=color, which='both')

        if not ticks_only:
            ax.spines[self.sp1].set_color(color)
            ax.spines[self.sp2].set_color(color)

    def reset_spinecolor(self, spines_only=False):
        """
        Reset all spine colors to black.

        """

        for subgrid in self.axes:
            for ax in subgrid:
                self.set_axcolor(ax, 'black', spines_only=spines_only)

    def draw_frame(self, lw='default', zorder=-1, edgecolor='black',
                   facecolor='none', **kwargs):
        """
        Draw frame around each column (``XGrid``) or row (``YGrid`) of plot.

        E.g., if ``self.mainax_dim`` == 1, then a frame will be drawn around
        the whole figure, visually anchoring axes; if ``self.mainax_dim`` > 1,
        then each mainax section will have a frame drawn around it.

        Parameters
        ----------
        lw : int
            Default 'default'.  If default, then ``lw`` will be set to
            ``self.spinewidth``.
        zorder : int
            Default -1.  The zorder of the frame.
        edgecolor : string or tuple of floats
            Default 'black'.  Any ``matplotlib``-accepted color.
        facecolor : string or tuple of floats
            Default 'none'.  The background color.  Any ``matplotlib``-accepted
            color.
        **kwargs
            Passed to ``plt.Rectangle``; any valid
            ``matplotlib.patches.Patch`` kwargs

        """

        last_instack = self.stackdim - 1
        patchlist = self.fig.patches

        if lw is 'default':
            lw = self.spinewidth

        for main in range(0, self.mainax_dim):
            if self.mainax_id is 'x':
                ll_axis = self.axes[last_instack][main]
                ur_axis = self.axes[0][main]
            else:
                ll_axis = self.axes[0][main]
                ur_axis = self.axes[last_instack][main]

            lldx = ll_axis.get_xlim()[0]
            lldy = ll_axis.get_ylim()[0]

            urdx = ur_axis.get_xlim()[1]
            urdy = ur_axis.get_ylim()[1]

            self.bf_llcorners.append((lldx, lldy))
            self.bf_urcorners.append((urdx, urdy))
            self.bf_llaxis.append(ll_axis)
            self.bf_uraxis.append(ur_axis)

            ll_corner = self._convert_coords(ll_axis, (lldx, lldy))
            ur_corner = self._convert_coords(ur_axis, (urdx, urdy))

            width, height = self._rect_dim(ur_corner, ll_corner)

            patchlist.append(plt.Rectangle(ll_corner, width, height,
                                           zorder=zorder, facecolor=facecolor,
                                           edgecolor=edgecolor, lw=lw,
                                           transform=self.fig.transFigure,
                                           **kwargs))

            self.bf_patchinds.append(len(patchlist) - 1)

    def draw_bar(self, ll_axis, ur_axis, bar_limits, orientation='vertical',
                 zorder=-1, **kwargs):
        """
        Draws vertical or horizontal bars across the ENTIRE plot space,
        anchoring them on opposite axes.

        If horizontal (vertical) bars are drawn on ``XGrid`` (``YGrid``), then
        adjusting plot spacing afterwards will appear to displace bar, because
        they are drawn on the figure and not the axes.

        Parameters
        ----------
        ll_axis : ``matplotlib Axes`` instance
            The axis that will contain the lower left corner of the bar
        ur_axis : ``matplotlib Axes`` instance
            The axis that will contain the upper right corner of the bar
        bar_limits : length 2 tuple of ints or floats,
            The lower, upper data limits of the bar
        orientation : string
            Default 'vertical'.  Indicates the orientation of the long
            axis of the bar
        zorder : int
            Default -1.  Zorder of the bar.
        **kwargs
            Passed to ``plt.Rectangle``; any valid
            ``matplotlib.patches.Patch`` kwargs

        """

        if orientation is 'vertical':
            lldx, urdx = bar_limits
            lldy = ll_axis.get_ylim()[0]
            urdy = ur_axis.get_ylim()[1]
        else:
            lldy, urdy = bar_limits
            lldx = ll_axis.get_xlim()[0]
            urdx = ur_axis.get_xlim()[1]

        self.bf_llcorners.append((lldx, lldy))
        self.bf_urcorners.append((urdx, urdy))
        self.bf_llaxis.append(ll_axis)
        self.bf_uraxis.append(ur_axis)

        ll_corner = self._convert_coords(ll_axis, (lldx, lldy))
        ur_corner = self._convert_coords(ur_axis, (urdx, urdy))

        width, height = self._rect_dim(ur_corner, ll_corner)

        self.fig.patches.append(plt.Rectangle(ll_corner, width, height,
                                              zorder=zorder,
                                              transform=self.fig.transFigure,
                                              **kwargs))

        self.bf_patchinds.append(len(self.fig.patches) - 1)

    def adjust_bar_frame(self):
        """
        Bars and frames made via ``self.draw_frame()`` and ``self.draw_bar()``
        are drawn on figure coordinates, so these patches and the axes
        move relative to each other when axis limits or subplot spacings are
        changed.

        This function realigns existing bars and frames with the original data
        coordinates.

        """
        # Check that there are any items to adjust
        if len(self.bf_llcorners) > 0:
            for ll, ur, llax, urax, ind in zip(self.bf_llcorners,
                                               self.bf_urcorners,
                                               self.bf_llaxis,
                                               self.bf_uraxis,
                                               self.bf_patchinds):
                # Grab rectangle
                rect = self.fig.patches[ind]

                # Get new figure coordinates
                new_x, new_y = self._convert_coords(llax, ll)
                ur_corner = self._convert_coords(urax, ur)

                # Get new figure dimensions
                width, height = self._rect_dim(ur_corner, (new_x, new_y))

                rect.set_bounds(new_x, new_y, width, height)

    def _update_twinsides(self):
        """
        Update the sides that twinned axes appear on in the event of a
        change to ``self.dataside_list``.

        """

        if self.twinds is not None:
            self.dataside_list = self.dataside_list[:self.stackdim]
            for ind in self.twinds:
                twinside = self.alt_sides[self.dataside_list[ind]]
                self.dataside_list.append(twinside)

    def _update_total_stackdim(self):
        """
        Update the number of combined original and twinned stacked axes.

        """

        self.total_stackdim = self.stackdim + self.twin_dim

    def _pop_data_ax(self, subgrid, side):
        """
        Pop out data axis from row or column.

        Parameters
        ----------
        subgrid : list of ``Axes`` instances
            Row or column of ``Axes``
        side : string
            The side that the visible stacked spine is on.

        """

        data_ind = self.side_inds[side]
        data_ax = subgrid.pop(data_ind)

        return data_ind, data_ax

    def _replace_data_ax(self, subgrid, data_ind, data_ax):
        """
        Put data axis back in its original place in row or column.

        Parameters
        ----------
        subgrid : list of axes
            Row or column of axes
        data_ind : int
            [0|-1].  The side that the visible stacked spine is on.
        data_ax : ``matplotlib Axes`` instance
            The ``Axes`` instance from ``subgrid`` that has the
            visible stacked spine.

        """

        if data_ind == 0:
            subgrid.insert(data_ind, data_ax)
        else:
            subgrid.append(data_ax)

    def _make_lists(self, dim, item, choice1, choice2):
        """
        Make a list of ``choice1`` and/or ``choice2`` of length dim.

        Parameters
        ----------
        dim : int
            The length of the list, usually ``self.mainax_dim`` or
            ``self.total_stackdim``
        item : string or list of ints
            ['all'|'none'|list of indices].
            Determines whether returned ``itemlist`` is all ``choice1``
             ('none'), all ``choice2`` ('all'), or is
             ``choice1`` with ``choice2`` at given indices.
        choice1 : any object instance
            One of the items to potentially make a list of
        choice2 : any object instance
            The other item to potentially create a list of

        Returns
        -------
        itemlist : list
            List of some combination of ``choice1`` and ``choice2``.

        """

        if item is 'none':
            itemlist = [choice1] * dim
        elif item is 'all':
            itemlist = [choice2] * dim
        else:
            itemlist = []
            for i in range(0, dim):
                if i in item:
                    itemlist.append(choice2)
                else:
                    itemlist.append(choice1)

        return itemlist

    def _set_ticks(self, subgrid_inds, ax_inds, xy_axis, which,
                   tick_dim, labelsize, pad, direction):
        """
        Set the x and/or y axis major and/or minor ticks at the given
        ``subgrid_inds``, ``ax_inds`` locations.

        Parameters
        ----------
        subgrid_inds : list of ints
            The indices of the rows (``XGrid``) or columns (``YGrid``)
            containing the axes that need tick parameters adjusted
        ax_inds : list of ints
            The indices of the axes within the indicated subgrids that need
            tick parameters adjusted
        xy_axis : string
            ['x'|'y'|'both']
        which : string
            The set of ticks to adjust.  ['major'|'minor']
        tick_dim : tuple of ints or floats
            The (length, width) of ``which`` ticks.
        labelsize : int
            Tick label fontsize in points.
        pad : int
            Spacing between the tick and tick label in points.
        direction : string
            Tick direction.  ['in'|'out'|'inout']

        """

        for s in subgrid_inds:
            for ax in ax_inds:
                self.axes[s][ax].tick_params(axis=xy_axis, which=which,
                                             length=tick_dim[0],
                                             width=tick_dim[1],
                                             labelsize=labelsize, pad=pad,
                                             direction=direction)

    def _convert_coords(self, axis, coordinates):
        """
        Convert data ``coordinates`` to axis coordinates.

        Parameters
        ----------
        axis : ``matplotlib Axes`` instance
            The axes instance used to convert data ``coordinates`` into axes
            and figure coordinates
        coordinates : tuple of floats
            Coordinates in the data coordinate system

        Returns
        -------
        fig_coords : tuple of floats
            ``coordinates`` translated to the figure coordinate system

        """

        # Convert to axes coordinates
        ax_coords = axis.transData.transform(coordinates)

        # Convert to figure coordinates
        fig_coords = self.fig.transFigure.inverted().transform(ax_coords)

        return fig_coords

    def _rect_dim(self, ur_corner, ll_corner):
        """
        Find w, h dimensions of rectange drawn in figure coordinates.

        """

        width, height = (ur - ll for ur, ll in zip(ur_corner, ll_corner))

        return width, height

    def _ratios_arelists(self, ratios):
        """
        Check if ``ratios`` are lists; rectify if not.

        """

        try:
            rsum = sum(ratios)
        except TypeError:
            rsum = ratios
            rlist = [ratios]
        else:
            rlist = ratios

        return rsum, rlist
