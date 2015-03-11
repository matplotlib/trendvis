import numpy as np
import matplotlib.pyplot as plt
import draw
import plot_accessory as pa

class Grid(object):
    """
    Mother class to help set up grid.

    """

    def __init__(self, xratios, yratios, mainax_x):

        self.gridrows, self.yratios = _ratios_arelists(yratios)
        self.gridcols, self.xratios = _ratios_arelists(xratios)

        self.numrows = len(self.yratios)
        self.numcols = len(self.xratios)

        self.axes = []

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
                                           'none' : ['right', 'left']}})}
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


    def set_mainax_relshift(self, axis_shift=None):
        """
        Set universal main axis spine shift by providing a float
        Set individual axis spine shift by providing a list of floats where
            len(axis_shift) = 2

        """

        if axis_shift is None:
            self.mainax_relshifts = None
            self.main_shifts = None
        elif 'both' in stackpos_list:
            self.mainax_relshifts = None
            self.main_shifts = None

        else:
            try:
                # Check if iterable
                axis_shift[0]
            except:
                # if not a list, apply same shift to both
                self.mainax_relshifts = [axis_shift] * 2
            else:
                if len(axis_shift) != 2:
                    print 'Warning:  len(axis_shift) != 2'
                    self.mainax_relshifts = [axis_shift[0]] * 2
                else:
                    self.mainax_relshifts = axis_shift

            self.main_shifts = []



    def set_stackedax_relshift(self, axis_shift=None):
        """
        Set universal stacked axis spine shift by providing a float
        Set individual axis spine shift by providing a list of floats where
            len(axis_shift) = stackdim
        """


        if axis_shift is None:
            self.stackax_relshifts = None
            self.stack_shifts = None

        else:
            try:
                # Check if iterable
                axis_shift[0]
            except:
                # if not a list, apply same shift to both
                self.stackax_relshifts = [axis_shift] * stackdim
            else:
                if len(axis_shift) != stackdim:
                    print 'Warning:  len(axis_shift) != ' + stackdim
                    self.stackax_relshifts = [axis_shift[0]] * stackdim
                else:
                    self.stackax_relshifts = axis_shift

            self.stack_shifts = []


    def set_stackedax_abshift(self):
        """
        Set the stacked axes shifts for realz

        """

        if self.stack_shifts is not None:
            for shift, dataside in zip(self.stackax_relshifts,
                                       self.dataside_list):
                if dataside is 'bottom' or dataside is 'left':
                    self.stack_shifts.append(0 - shift)
                else:
                    self.stack_shifts.append(1 + shift)


    def set_mainax_abshift(self):
        """
        Set the main axis shift for realz

        """

        if self.main_shifts is not None:
            if self.mainax_id is 'x':
                # in top to bottom
                self.main_shifts.append(1 + self.mainax_relshifts)
                self.main_shifts.append(0 - self.mainax_relshifts)
            else:
                # left to right
                self.main_shifts.append(0 - self.mainax_relshifts)
                self.main_shifts.append(1 + self.mainax_relshifts)


    def set_dataside(self, startside, alternate_sides):
        """
        Set the dataside_list that indicates which stacked ax spine will be
            the data spine
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
        set the stackpos_list that indicates where the row or col is
            in the stack

        """

        alt_pos = {'left' : 'right',
                   'top' : 'bottom'}

        if self.stackdim == 1:
            if onespine_forboth:
                self.stackpos_list = [self.startpos]
            else:
                self.stackpos_list = ['both']

        else:
            num_nones = self.stackdim - 2
            self.stackpos_list = ([startpos] +['none']*num_nones +
                                  [alt_pos[startpos]])

class X_Grid(Grid):
    """
    Class for making grid with x as the main axis

    """

    def __init__(self, xratios, yratios, figsize, to_twin=None):
        """
        Initialize an X_Grid object

        Parameters
        ----------
        xratios : int or iterable of ints
        yratios : int or iterable of ints
        figsize : tuple of ints

        Keyword Arguments
        -----------------
        to_twin : iterable of ints
            The indices of the rows to twin

        """

        # Initialize parent class
        # Last arg is True because mainax_x
        Grid.__init__(self, xratios, yratios, True)

        # Set initial x and y grid positions (top left)
        xpos = 0
        ypos = 0

        fig = plt.figure(figsize=figsize)

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

        """
        plt.subplots_adjust(hspace=hspace)


    def cleanup_grid(self):
        """
        Removes spines so that only one on each axis is visible

        """

        for row, dataside, stackpos in zip(self.axes, self.dataside_list,
                                           self.stackpos_list):

            # Set the tick labels for the main axis
            ltop, lbottom = self.mainax_ticks[stackpos]

            # Set main axis tick parameters
            for ax in row:
                ax.xaxis.set_tick_params(labeltop=ltop, labelbottom=lbottom)
                ax.xaxis.set_ticks_position(stackpos)

            # Figure out which axis in row is supposed to have stackedax spine
            data_ind = self.side_inds[dataside]

            # Get the one axis in the row that will have spine, set ticks
            data_ax = row.pop(data_ind)
            data_ax.yaxis.set_ticks_position(dataside)

            # Based on position in the stack and side of plot it's on,
            # get rid of extra spines
            for sp in self.spine_begone[pos][dataside]:
                data_ax.spines[sp].set_visible(False)

            # For all other axes, get rid of unnecessary spines, tick(label)s
            for ax in row:
                ax.yaxis.set_ticks_position('none')
                plt.setp(ax.get_yticklabels(), visible=False)

                for sp in self.spine_begone[pos]['none']:
                    ax.spines[sp].set_visible(False)

            # Put data axis back in row
            if data_ind == 0:
                row.insert(dat_ind, data_ax)
            else:
                row.append(data_ax)

            # row[data_ind].plot([0.5], [0.5], marker='s', markersize=25)


    def shift_mainspines(self):
        """
        Move the main spines around

        """
        if self.main_shifts is not None:

            for row, stackpos, shift in zip([self.axes[0], self.axes[-1]],
                                            [self.stackpos_list[0],
                                             self.stackpos_list[-1],
                                            self.main_shifts):
                for ax in row:
                    ax.spines[stackpos].set_position(('axes', shift))


    def shfit_stackedspines(self):
        """
        Move the stacked spines around

        """

        if self.stack_shifts is not None:

            for row, dataside, shift, in zip(self.axes, self.dataside_list,
                                             self.stack_shifts):

                data_ind = self.side_inds[dataside]
                data_ax = row.pop(data_ind)
                data_ax.spines[dataside].set_position(('axes', shift))


class Y_Grid(Grid):
    """
    Class for making a plot with the Y axis as the main axis

    """
    def __init__(self, xratios, yratios, figsize, to_twin=None):
        """
        Initialize grid with the y-axis as main axis

        """
        # Initialize parent class
        # Last arg is False because mainax_x
        Grid.__init__(self, xratios, yratios, False)

        # Set initial x and y grid positions (top left)
        xpos = 0
        ypos = 0

        fig = plt.figure(figsize=figsize)

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
            ypos = 0
            xpos += colspan


    def adjust_spacing(self, wspace):
        """
        Adjust the horizontal spacing between columns

        """

        plt.subplots_adjust(wspace=wspace)


    def cleanup_grid(self):
        """
        Removes extra spines from axes

        """

        for col, dataside, stackpos in zip(self.axes, self.dataside_list,
                                           self.stackpos_list):

            # Get mainax tick labelling settings
            lleft, lright = self.mainax_ticks[stackpos]

            for ax in col:
                ax.yaxis.set_tick_params(labelleft=lleft, labelright=lright)
                ax.yaxis.set_ticks_position(stackpos)

            data_ind = self.side_inds[dataside]

            data_ax - col.pop(data_ind)
            data_ax.xaxis.set_ticks_position