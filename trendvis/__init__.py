"""
TrendVis package containing tools for creating complex,
publication quality figures in a few styles:  y-axes
stack against a common x-axis or a common broken x-axis
(which may be demarcated as breaks or columns), x-axes
stack against a common y-axis or a common broken y-axis
(which may be demarcated as breaks or rows), and plots of
one axis where trends are indicated by location and
discrete point colors/sizes/shapes or continuous point
colors/sizes.  Additionally, contains drawing tools
to frame subplot area(s) or highlight various columns,
bars, or rectangles of interest.

"""

__all__ = ['broken_x',
           'discrete_colorplot',
           'set_xticks',
           'set_yticks',
           'reorder_sort',
           'reorder_index',
           'multi_y',
           'multi_x',
           'frame',
           'bar',
           'cutout',
           'convert_coords']

from .ystack_brokenx import broken_x

from .colorplots import discrete_colorplot

from .plot_accessory import (set_yticks, set_xticks,
                             reorder_bysort as reorder_sort,
                             reorder_byindex as reorder_index)

from .ystack import multi_y

from .xstack import multi_x

from .draw import frame, bar, cutout, convert_coords
