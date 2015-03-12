import numpy as np
import matplotlib.pyplot as plt


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
            to yratios.
        yratios : int or list of ints
            The relative sizes of the rows.  Not directly comparable to xratios.
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
        self.twin_dim = None
        self.reltwin_shifts = None
        self.twin_shifts = None

        self.grid_isclean = False

        if mainax_x:
            self.mainax_id = 'x'
            self.stackedax_id = 'y'
            self.stackdim = self.numrows

            self.startpos = 'top'

            self.mainax_ticks = {'top' : ('on', 'off'),
                                 'both' : ('on', 'on'),
                                 'bottom' : ('off', 'on'),
                                 'none' : ('off', 'off')}

            self.alt_sides = {'left' : 'right',
                              'right': 'left'}

            self.side_inds = {'left' : 0,
                              'right': -1}

            self.spine_begone = {'top' : {'left' : ['bottom', 'right'],
                                          'right': ['bottom', 'left'],
                                          'none' : ['bottom', 'left', 'right']},
                                 'none' : {'left' : ['top', 'bottom', 'right'],
                                           'right': ['top', 'bottom', 'left'],
                                           'none' : ['top', 'bottom', 'left',
                                                     'right']},
                                 'bottom' : {'left' : ['top', 'right'],
                                             'right': ['top', 'left'],
                                             'none' : ['top', 'left', 'right']},
                                 'both' : {'left' : ['right'],
                                           'right': ['left'],
                                           'none' : ['right', 'left']}}
        else:
            self.mainax_id = 'y'
            self.stackax_id = 'x'
            self.stackdim = self.numcols

            self.startpos = 'left'

            self.mainax_ticks = {'left' : ('on', 'off'),
                                 'both' : ('on', 'on'),
                                 'right' : ('off', 'on'),
                                 'none' : ('off', 'off')}

            self.alt_sides = {'top' : 'bottom',
                              'bottom': 'top'}

            self.side_inds = {'top' : 0,
                              'bottom': -1}

            self.spine_begone = {'left' : {'top'   : ['bottom', 'right'],
                                           'bottom' : ['top', 'right'],
                                           'none' : ['bottom', 'top', 'right']},
                                 'none' : {'top' :  ['bottom', 'left', 'right'],
                                           'bottom' : ['top', 'left', 'right'],
                                           'none'  : ['top', 'bottom', 'left',
                                                      'right']},
                                 'right' : {'top' : ['bottom', 'left'],
                                            'bottom' : ['top', 'left'],
                                            'none' : ['top', 'bottom', 'left']},
                                 'both' : {'top' : ['bottom'],
                                           'bottom' : ['top'],
                                           'none' : ['top', 'bottom']}}


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
                newside = self.alt_sides[self.dataside_list[i-1]]
                self.dataside_list.append(newside)

        else:
            self.dataside_list = self.dataside_list * self.stackdim

        self.update_twinsides()


    def update_twinsides(self):
        """
        Update the sides that twinned axes appear on in the event of a
            change to self.dataside_list.

        """

        if self.twin_dim is not None:
            self.dataside_list = self.dataside_list[:self.stackdim]
            for ind in self.twinds:
                twinside = self.alt_sides[self.dataside_list[ind]]
                self.dataside_list.append(twinside)


    def set_stackposition(self, onespine_forboth):
        """
        Set the stackpos_list that indicates where the row or col is
            in the grid

        Parameters
        ----------
        onespine_forboth : Boolean
            [True|False].  If the plot stack is only 1 row (column), then
            both main axis spines may be used (False), or only the bottom (left)
            spine.

        """

        alt_pos = {'left' : 'right',
                   'top' : 'bottom'}

        # Position list in the case of a stack of 1
        if self.stackdim == 1:
            if onespine_forboth:
                self.stackpos_list = [self.startpos]
            else:
                self.stackpos_list = ['both']

        else:
            num_nones = self.stackdim - 2
            self.stackpos_list = ([self.startpos] +['none']*num_nones +
                                  [alt_pos[self.startpos]])


    def set_relative_axshift(self, axis_shift=None, twin_shift=None):
        """
        Set universal or individual stacked axis spine relative shift

        Keyword Arguments
        -----------------
        axis_shift : float or list of floats
            Default None.  Set universal (float) or individual (list of
                floats where len(axis_shift) = self.stackdim) axis spine shift

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
                    print 'Warning:  len(twin_shift) != number of twinned axes!'
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

            for subgrid, dataside, shift in zip(self.axes, self.dataside_list,
                                                 self.stack_shifts):

                for ax in subgrid:
                    ax.spines[dataside].set_position(('axes', shift))

        if self.twin_shifts is not None:

            for subgrid, dataside, shift in zip(self.axes[self.stackdim:],
                                                self.dataside_list[self.stackdim:],
                                                self.twin_shifts):
                for ax in subgrid:
                    ax.spines[dataside].set_position(('axes', shift))


    def reset_spineshift(self):
        """
        Reset all spines to normal position

        """
        shifts = {'x' : {'left' : 0.0,
                         'right' : 1.0},
                  'y' : {'bottom' : 0.0,
                          'top' : 1.0}}


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

        """

        data_ind = self.side_inds[side]
        data_ax = subgrid.pop(data_ind)

        return data_ind, data_ax


    def replace_data_ax(self, subgrid, data_ind, data_ax):
        """
        Put data axis back in its original place in row or column

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
        Get rid of twinned axes

        """

        for subgrid in self.axes[self.stackdim:]:
            for ax in subgrid:
                self.fig.delaxes(ax)

        self.twinds = None
        self.twin_dim = None
        self.reltwin_shifts = None
        self.twin_shifts = None
        self.dataside_list = self.dataside_list[:self.stackdim]
        self.stackpos_list = self.stackpos_list[:self.stackdim]
        self.axes = self.axes[:self.stackdim]


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