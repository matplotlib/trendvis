from matplotlib.ticker import MultipleLocator


class Grid(object):
    """
    Superlass for Y_Grid, X_Grid.

    """

    def __init__(self, xratios, yratios, mainax_x):
        """
        Initialize grid attributes

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

        if mainax_x:
            self.mainax_id = 'x'
            self.stackedax_id = 'y'
            self.stackdim = self.numrows
            self.mainax_dim = self.numcols

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

                if dataside is 'bottom' or dataside is 'left':
                    self.stack_shifts.append(0 - shift)
                else:
                    self.stack_shifts.append(1 + shift)

        if self.reltwin_shifts is not None:
            self.twin_shifts = []

            for shift, dataside in zip(self.reltwin_shifts,
                                       self.dataside_list[self.stackdim:]):
                if dataside is 'bottom' or dataside is 'left':
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

        spinelist = ['top', 'bottom', 'left', 'right']

        for row in self.axes:
            for ax in row:
                for sp in spinelist:
                    ax.spines[sp].set_visible(True)

        self.grid_isclean = False

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

    def xaxis_ticknum(self, axis, scale, xticks):
        """
        Set x tick scale and, if linear, major and minor tick locators.

        Parameters
        ----------
        axis : Axes instance
            Axes instance to set x-axis scale and potentially
            major and minor tick locators
        scale : string
            ['log'|'linear'].  X axis scale.
        xticks : tuple
            Tuple of (major, minor) x axis tick multiples.

        """

        axis.set_xscale(scale)

        if scale is not 'log':

            xmajor_loc = MultipleLocator(xticks[0])
            xminor_loc = MultipleLocator(xticks[1])

            axis.xaxis.set_major_locator(xmajor_loc)
            axis.xaxis.set_minor_locator(xminor_loc)

    def yaxis_ticknum(self, axis, scale, yticks):
        """
        Set y tick scale and, if linear, major and minor tick locators.

        Parameters
        ----------
        axis : Axes instance
            Axes instance to set y-axis scale and potentially
            major and minor tick locators
        scale : string
            ['log'|'linear'].  Y axis scale.
        xticks : tuple
            Tuple of (major, minor) y axis tick multiples.

        """

        axis.set_yscale(scale)

        if scale is not 'log':
            ymajor_loc = MultipleLocator(yticks[0])
            yminor_loc = MultipleLocator(yticks[1])

            axis.yaxis.set_major_locator(ymajor_loc)
            axis.yaxis.set_minor_locator(yminor_loc)


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
