"""
TrendVis package containing tools for creating complex,
publication quality figures in a few styles:

* y-axes stacked against a common x-axis or a common broken x-axis
  (which may be demarcated as breaks or columns)
* x-axes stack3d against a common y-axis or a common broken y-axis
  (which may be demarcated as breaks or rows)

Additionally, TrendVis contains drawing tools to frame subplot area(s)
or highlight various columns, bars, or rectangles of interest.

"""

__all__ = ['XGrid',
           'YGrid',
           'make_grid',
           'plot_data']

from .xgrid_ystack import XGrid

from .ygrid_xstack import YGrid

from .gridwrapper import make_grid, plot_data
