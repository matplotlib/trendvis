.. currentmodule:: trendvis

==========
 TrendVis
==========

:py:mod:`trendvis` API
======================

.. autosummary::
   :toctree: generated/

   XGrid
   YGrid
   make_grid
   plot_data


The public API of :py:mod:`trendvis` consists of two classes, `XGrid` and `YGrid`, and two convenience functions :func:`make_grid` and :func:`plot_data`.  The preferred interface is through `XGrid` and `YGrid`, but the convenience functions are provided to quickly create and format an `XGrid` or `YGrid` and draw line plots.


Motivation
==========


When plotting multiple datasets against a common x or y axis, a figure can quickly become cluttered with overlain curves and/or unnecessary axis spines.  `TrendVis` enables construction of complex figures with data plotted in a common plot area against different y or x ('stack') axes and a common x or y (main) axis respectively.


Examples
========

Simple XGrid
------------

.. plot::
   :include-source:

   import numpy as np
   import matplotlib.pyplot as plt
   import trendvis

   # Simple XGrid with frame
   yvals = np.random.rand(10)
   nums = 10
   lw = 1.5

   ex0 = trendvis.XGrid([1,2,1], figsize=(5,5))

   trendvis.plot_data(ex0, [[(np.linspace(0, 9.5, num=nums), yvals, 'blue')],
                            [(np.linspace(1, 9, num=nums), yvals*5, 'red')],
                            [(np.linspace(0.5, 10, num=nums), yvals*10, 'green')]],
                      lw=1.5, auto_spinecolor=False, markeredgecolor='none', marker='s')

   ex0.cleanup_grid()
   ex0.autocolor_spines(ticks_only=True)

   ex0.set_spinewidth(lw)

   ex0.set_all_ticknums([(2, 1)], [(0.2, 0.1), (1, 0.5), (2, 1)])
   ex0.set_ticks(major_dim=(7, 3), minor_dim=(4, 2))

   ex0.set_ylabels(['axis 0', 'axis 1', 'axis 2'])
   ex0.axes[2][0].set_xlabel('Main Axis', fontsize=14)

   ex0.draw_frame()
   ex0.fig.subplots_adjust(hspace=-0.3)


Simple YGrid
------------
Creating a `YGrid` is essentially the same as an `XGrid`.

.. plot::
   :include-source:

   import numpy as np
   import matplotlib.pyplot as plt
   import trendvis

   # Simple YGrid without frame
   xvals = np.random.rand(10)
   nums = 10
   lw = 1.5

   ex0 = trendvis.YGrid([1,2,1], figsize=(5,5))

   trendvis.plot_data(ex0, [[(xvals, np.linspace(0, 9.5, num=nums), 'blue')],
                   [(xvals*5, np.linspace(1, 9, num=nums),  'red')],
                   [(xvals*10, np.linspace(0.5, 10, num=nums),'green')]],
             lw=1.5, auto_spinecolor=True, markeredgecolor='none', marker='s')

   ex0.cleanup_grid()
   ex0.set_spinewidth(lw)

   ex0.set_all_ticknums([(0.2, 0.1), (1, 0.5), (2, 1)], [(2, 1)])
   ex0.set_ticks(major_dim=(7, 3), minor_dim=(4, 2))

   ex0.set_xlabels(['axis 0', 'axis 1', 'axis 2'])
   ex0.axes[0][0].set_ylabel('Main Axis', fontsize=14)

   ex0.fig.subplots_adjust(wspace=-0.3)
