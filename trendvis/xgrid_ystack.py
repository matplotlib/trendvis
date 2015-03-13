import numpy as np
import matplotlib.pyplot as plt
from gridclass import Grid


class X_Grid(Grid):
    """
    Class for making a plot with the x axis as the main axis
        and a stack of y axes

    """

    def __init__(self, xratios, yratios, figsize, startside='left',
                 alternate_sides=True, onespine_forboth=False):
        """
        Initialize X_Grid

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
            Default 'left'.  ['left'|'right'].  The side the topmost y axis
            will be on.
        alternate_sides : Boolean
            Default True.  [True|False].
            Stacked axis spines alternate sides or are all on startside.
        onespine_forboth : Boolean
            Default False.  [True|False].  If the plot stack is only 1 row,
            then both main axis spines can be visible,
            or only the bottom spine.

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
                xpos += colspan

            self.axes.append(row)

            # Reset x position to left side, move to next y position
            xpos = 0
            ypos += rowspan

        self.set_dataside(startside, alternate_sides)
        self.set_stackposition(onespine_forboth)

    def make_twins(self, rows_to_twin):
        """
        Twin rows

        Parameters
        ----------
        rows_to_twin : list of ints
            Indices of the rows to twin

        """

        if self.twinds is None:
            self.twinds = rows_to_twin
            self.twin_dim = len(rows_to_twin)
        else:
            self.twinds.extend(rows_to_twin)
            self.twin_dim += len(rows_to_twin)

        for ind in rows_to_twin:

            twin_row = []

            for ax in self.axes[ind]:
                twin = ax.twinx()
                ax.set_zorder(twin.get_zorder() + 1)
                twin_row.append(twin)

            twinside = self.alt_sides[self.dataside_list[ind]]
            self.dataside_list.append(twinside)
            self.stackpos_list.append('none')
            self.axes.append(twin_row)

        self.grid_isclean = False

    def adjust_spacing(self, hspace):
        """
        Adjust the vertical spacing between rows.

        Parameters
        ----------
        hspace : float

        """

        plt.subplots_adjust(hspace=hspace)

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

                    # Remove spines
                    for sp in self.spine_begone[stackpos]['none']:
                        ax.spines[sp].set_visible(False)

                self.replace_data_ax(row, data_ind, data_ax)

        self.grid_isclean = True
