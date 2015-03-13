import numpy as np
import matplotlib.pyplot as plt
from gridclass import Grid

class Y_Grid(Grid):
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
            to yratios.
        yratios : int or list of ints
            The relative sizes of the rows.  Not directly comparable to xratios.
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

        for ind in cols_to_twin:

            twin_col = []

            for ax in self.axes[ind]:
                twin = ax.twiny()
                ax.set_zorder(twin.get_zorder()+1)
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

        self.grid_isclean = True