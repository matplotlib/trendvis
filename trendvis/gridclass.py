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


    def set_relative_axshift(self, axis_shift=None):
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


    def move_spines(self):
        """
        Move the stacked spines around

        """

        if self.stack_shifts is not None:

            for subgrid, dataside, shift in zip(self.axes, self.dataside_list,
                                                 self.stack_shifts):

                for ax in subgrid:
                    ax.spines[dataside].set_position(('axes', shift))


    def reset_spineshift(self):
        """
        Reset the spines to normal position

        """
        shifts = {'x' : {'left' : 0.0,
                         'right' : 1.0},
                  'y' : {'bottom' : 0.0,
                          'top' : 1.0}}

        sd = shifts[self.mainax_id]

        for subgrid, dataside in zip(self.axes, self.dataside_list):

            for ax in subgrid:
                ax.spines[dataside].set_position(('axes', sd[dataside]))

        self.relative_shifts = None
        self.stack_shifts = None


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


class X_Grid(Grid):
    """
    Class for making grid with x as the main axis

    """

    def __init__(self, xratios, yratios, figsize, to_twin=None):
        """
        Initialize an X_Grid object

        Parameters
        ----------
        xratios : int or list of ints
            The relative sizes of the columns.  Not directly comparable
            to yratios.
        yratios : int or list of ints
            The relative sizes of the rows.  Not directly comparable to xratios.
        figsize : tuple of ints or floats
            The figure dimensions in inches

        Keyword Arguments
        -----------------
        to_twin : list of ints
            The indices of the rows to twin

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

                # Move to next x position
                xpos += colspan

            self.axes.append(row)

            # Reset x position to left side, move to next y position
            xpos = 0
            ypos += rowspan


    def adjust_spacing(self, hspace):
        """
        Adjust vertical spacing between rows.

        Parameters
        ----------
        hspace : float

        """
        plt.subplots_adjust(hspace=hspace)


    def cleanup_grid(self):
        """
        Remove unnecessary spines from grid

        """

        for row, dataside, stackpos in zip(self.axes, self.dataside_list,
                                           self.stackpos_list):

            # Get mainax tick labelling settings
            ltop, lbottom = self.mainax_ticks[stackpos]

            # Set mainax tick parameters and positions
            for ax in row:
                ax.xaxis.set_tick_params(labeltop=ltop, labelbottom=lbottom)
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

                for sp in self.spine_begone[stackpos]['none']:
                    ax.spines[sp].set_visible(False)

            self.replace_data_ax(row, data_ind, data_ax)



class Y_Grid(Grid):
    """
    Class for making a plot with the Y axis as the main axis

    """
    def __init__(self, xratios, yratios, figsize, to_twin=None):
        """
        Initialize a Y_Grid object

        Parameters
        ----------
        xratios : int or list of ints
            The relative sizes of the columns.  Not directly comparable
            to yratios.
        yratios : int or list of ints
            The relative sizes of the rows.  Not directly comparable to xratios.
        figsize : tuple of ints or floats
            The figure dimensions in inches

        Keyword Arguments
        -----------------
        to_twin : list of ints
            The indices of the columns to twin

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


    def adjust_spacing(self, wspace):
        """
        Adjust the horizontal spacing between columns

        Parameters
        ----------
        wspace : float

        """

        plt.subplots_adjust(wspace=wspace)


    def cleanup_grid(self):
        """
        Removes unnecessary spines from grid

        """

        for col, dataside, stackpos in zip(self.axes, self.dataside_list,
                                           self.stackpos_list):

            # Get mainax tick labelling settings
            lleft, lright = self.mainax_ticks[stackpos]

            # Set mainax tick parameters and positions
            for ax in col:
                ax.yaxis.set_tick_params(labelleft=lleft, labelright=lright)
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
