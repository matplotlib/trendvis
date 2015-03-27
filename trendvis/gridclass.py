from matplotlib.ticker import MultipleLocator


class Grid(object):
    """
    Superlass for YGrid, XGrid.

    """

    def __init__(self, xratios, yratios, mainax_x):
        """
        Initialize grid attributes.  Should only be called through
            XGrid, YGrid subclasses.

        Parameters
        ----------
        xratios : int or list of ints
            The relative sizes of the columns.  Not directly comparable
            to yratios
        yratios : int or list of ints
            The relative sizes of the rows.  Not directly comparable to xratios
        mainax_x : Boolean
            [True|False].  Indicates if x is the main axis.  Determines
            some attributes

        """

        self.gridrows, self.yratios = _ratios_arelists(yratios)
        self.gridcols, self.xratios = _ratios_arelists(xratios)

        self.numrows = len(self.yratios)
        self.numcols = len(self.xratios)

        self.axes = []

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
                                 'bottom' : {'left' : ['top', 'right'],
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
                                 'right' : {'top'   : ['bottom', 'left'],
                                            'bottom': ['top', 'left'],
                                            'none'  : ['top', 'bottom',
                                                       'left']},
                                 'both' : {'top'   : ['bottom'],
                                           'bottom': ['top'],
                                           'none'  : ['top', 'bottom']}}

        self.update_total_stackdim()

    def set_dataside(self, startside, alternate_sides):
        """
        Set the dataside_list that indicates which stacked ax spine will be
            the data spine.

        Parameters
        ----------
        startside : string
            ['left'|'right'] or ['top'|'bottom'].  The side the first row
            (column) in self.axes will have its y (x) axis spine on.
        alternate_sides : Boolean
            [True|False].  Stacked axis spines alternate sides or are all on
            startside.

        """

        self.dataside_list = [startside]

        if alternate_sides:
            for i in range(1, self.stackdim):
                newside = self.alt_sides[self.dataside_list[i - 1]]
                self.dataside_list.append(newside)

        else:
            self.dataside_list = self.dataside_list * self.stackdim

        self.update_twinsides()

    def update_twinsides(self):
        """
        Update the sides that twinned axes appear on in the event of a
            change to self.dataside_list.

        """

        if self.twinds is not None:
            self.dataside_list = self.dataside_list[:self.stackdim]
            for ind in self.twinds:
                twinside = self.alt_sides[self.dataside_list[ind]]
                self.dataside_list.append(twinside)

    def update_total_stackdim(self):
        """
        Update the number of combined original and twinned stacked axes.

        """

        self.total_stackdim = self.stackdim + self.twin_dim

    def set_stackposition(self, onespine_forboth):
        """
        Set the stackpos_list that indicates where the row or col is
            in the grid

        Parameters
        ----------
        onespine_forboth : Boolean
            [True|False].  If the plot stack is only 1 row (column), then
            both main axis spines may be used (False), or only the bottom
            (left) spine.

        """

        alt_pos = {'left': 'right',
                   'top' : 'bottom'}

        # Position list in the case of a stack of 1
        if self.stackdim == 1:
            if onespine_forboth:
                self.stackpos_list = [self.startpos]
            else:
                self.stackpos_list = ['both']

        else:
            num_nones = self.stackdim - 2
            self.stackpos_list = ([self.startpos] + ['none'] * num_nones +
                                  [alt_pos[self.startpos]])

    def set_relative_axshift(self, axis_shift=None, twin_shift=None):
        """
        Set universal or individual stacked axis spine relative shift

        Keyword Arguments
        -----------------
        axis_shift : float or list of floats
            Default None.  Set universal (float) or individual (list of
            floats where len(axis_shift) = self.stackdim) axis spine shift
        twin_shift : float or list of floats
            Default None.  Set universal (float) or individual (list of
            floats where len(twin_shift) = self.twin_dim) twinned axis spine
            shift.

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
                    print 'Warning:  len(axis_shift) != ' + self.stackdim
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
                    print 'Warning:  len(twin_shift) != number of twinned ax!'
                    self.reltwin_shifts = [twin_shift[0]] * self.twin_dim
                else:
                    self.reltwin_shifts = twin_shift

    def set_absolute_axshift(self):
        """
        Translate self.relative_shifts to absolute values based on the
            corresponding plot side the axis will appear on

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

    def move_spines(self):
        """
        Move the stacked spines around

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

    def reset_spineshift(self):
        """
        Reset all spines to normal position

        """

        shifts = {'x' : {'left'   : 0.0,
                         'right'  : 1.0},
                  'y' : {'bottom' : 0.0,
                         'top'   : 1.0}}

        sd = shifts[self.mainax_id]

        for subgrid in self.axes:
            for ax in subgrid:
                for key in sd:
                    ax.spines[key].set_position(('axes', sd[key]))

        self.relative_shifts = None
        self.stack_shifts = None
        self.reltwin_shifts = None
        self.twin_shifts = None

    def pop_data_ax(self, subgrid, side):
        """
        Pop out data axis from row or column

        Parameters
        ----------
        subgrid : list of axes
            Row or column of axes
        side : string
            The side that the visible stacked spine is on.

        """

        data_ind = self.side_inds[side]
        data_ax = subgrid.pop(data_ind)

        return data_ind, data_ax

    def replace_data_ax(self, subgrid, data_ind, data_ax):
        """
        Put data axis back in its original place in row or column

        Parameters
        ----------
        subgrid : list of axes
            Row or column of axes
        data_ind : int
            [0|-1].  The side that the visible stacked spine is on.
        data_ax : axes instance
            The axes instance from subgrid that has the visible stacked spine.

        """

        if data_ind == 0:
            subgrid.insert(data_ind, data_ax)
        else:
            subgrid.append(data_ax)

    def replace_spines(self):
        """
        Undo the spine-hiding actions of self.cleanup_grid()

        """

        for subgrid in self.axes:
            for ax in subgrid:
                for sp in self.spinelist:
                    ax.spines[sp].set_visible(True)

        self.grid_isclean = False

    def set_ax_visibility(self, ax, which, visible):
        """
        Hide (`visible`=False) or show (`visible`=True) an axis side
            (`which`).  Will hide/show spine, ticks, and ticklabels.

        Parameters
        ----------
        subgrid_ind : int
            The index of the row (column) holding the desired ax
        ax_ind : int
            The index of the column (row) within subgrid of the desired ax
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
        Edit the linewidth of the axis spines.  Self.spinewidth also used
            as the frame linewidth.

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
        Get rid of twinned axes.

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

        self.update_total_stackdim()

    def make_lists(self, dim, item, choice1, choice2):
        """
        Make a list choice1 and/or choice2 of length dim.

        Parameters
        ----------
        dim : int
            The length of the list, usually self.mainax_dim or
            self.total_stackdim
        item : string or list of ints
            ['all'|'none'|list of indices].
            Determines whether returned item_list is all choice1 ('none'),
            all choice2 ('all'), or is choice1 with choice2 at given indices.

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

    def xaxis_ticknum(self, axis, xticks, scale='linear'):
        """
        Set x tick scale and, if linear, major and minor tick locators.

        Parameters
        ----------
        axis : Axes instance
            Axes instance to set x-axis scale and potentially
            major and minor tick locators
        xticks : tuple
            Tuple of (major, minor) x axis tick multiples.

        Keyword Arguments
        -----------------
        scale : string
            Default 'linear'.  ['log'|'linear'].  X axis scale.

        """

        axis.set_xscale(scale)

        if scale is not 'log':

            xmajor_loc = MultipleLocator(xticks[0])
            xminor_loc = MultipleLocator(xticks[1])

            axis.xaxis.set_major_locator(xmajor_loc)
            axis.xaxis.set_minor_locator(xminor_loc)

    def yaxis_ticknum(self, axis, yticks, scale='linear'):
        """
        Set y tick scale and, if linear, major and minor tick locators.

        Parameters
        ----------
        axis : Axes instance
            Axes instance to set y-axis scale and potentially
            major and minor tick locators
        xticks : tuple
            Tuple of (major, minor) y axis tick multiples.

        Keyword Arguments
        -----------------
        scale : string
            Default 'linear'.  ['log'|'linear'].  Y axis scale.

        """

        axis.set_yscale(scale)

        if scale is not 'log':
            ymajor_loc = MultipleLocator(yticks[0])
            yminor_loc = MultipleLocator(yticks[1])

            axis.yaxis.set_major_locator(ymajor_loc)
            axis.yaxis.set_minor_locator(yminor_loc)

    def set_ticks(self, subgrid_inds, ax_inds, xy_axis, which,
                  tick_dim, labelsize, pad, direction):
        """
        Set the x and/or y axis major and/or minor ticks at the given
            subgrid_inds, ax_inds locations.

        Parameters
        ----------
        subgrid_inds : list of ints
            The indices of the rows (XGrid) or columns (YGrid) containing
            the axes that need tick parameters adjusted
        ax_inds : list of ints
            The indices of the axes within the indicated subgrids that need
            tick parameters adjusted
        xy_axis : string
            ['x'|'y'|'both']
        which : string
            The set of ticks to adjust.  ['major'|'minor']
        tick_dim : tuple of ints or floats
            The (length, width) of `which` ticks.
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

    def set_axcolor(self, ax, color):
        """
        Set the stacked ax spine and tick color of the given Axes.

        Parameters
        ----------
        ax : Axes instance
            Matplotlib axes instance.
        color : string, tuple
            Any color accepted by matplotlib.

        """

        ax.tick_params(axis=self.stackax_id, color=color)
        ax.spines[self.sp1].set_color(color)
        ax.spines[self.sp2].set_color(color)

    def autocolor_spines(self, which):
        """
        Set the axis stacked ax spine and tick color based on the indicated
            set of lines.

        Parameters
        ----------
        which : int
            Index of the line in each Axess instances' list of lines that
            should be used to set the color.  Commonly 0 (stacked axes are same
                color as first data plotted on axes instance) or -1 (stacked
                axes are the same color as last data plotted on axes instance)

        """

        for subgrid in self.axes:
            for ax in subgrid:
                try:
                    color = ax.get_children()[2 + which].get_color()
                except AttributeError:
                    color = ax.get_children()[2 + which].get_facecolor()
                self.set_axcolor(ax, color)

    def reset_spinecolor(self):
        """
        Change all spine colors back to black

        """

        for subgrid in self.axes:
            for ax in subgrid:
                self.set_axcolor(ax, 'black')


def _ratios_arelists(ratios):
    """
    Check if xratios, yratios are lists; rectify if not.
        Private, only used internally in Grid class

    """

    try:
        rsum = sum(ratios)
    except TypeError:
        rsum = ratios
        rlist = [ratios]
    else:
        rlist = ratios

    return rsum, rlist
