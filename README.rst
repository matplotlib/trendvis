========
TrendVis
========

TrendVis is a plotting package that uses
`matplotlib <http://matplotlib.org/>`_ to create information-dense,
sparkline-like, quantitative visualizations of multiple disparate data sets in
a common plot area against a common variable.  This plot type is particularly
well-suited for time-series data. The results speak for themselves:

.. image:: https://raw.githubusercontent.com/mscross/scipy_proceedings/trendvis/papers/mellissa_cross_t/barredplot.png
    :target: https://raw.githubusercontent.com/mscross/scipy_proceedings/trendvis/papers/mellissa_cross_t/barredplot.png
    :alt: TrendVis example

For further reading on TrendVis, see the `SciPy 2015 Proceedings <http://conference.scipy.org/proceedings/scipy2015/mellissa_cross_t.html>`_.

============
Installation
============

TrendVis is pure Python, natively supports Python 2 and 3, and depends only on
`matplotlib <http://matplotlib.org/>`_ version 1.2 or greater.

Setup and installation is simple::

    pip install -U trendvis

or, if you would like to develop the package, fork and clone the repo then run::

    python setup.py develop

at package root.

==============
Quick Examples
==============

Below are several examples showing various features in TrendVis and a typical
workflow. Version >= 0.2.1 is required.

Single column ``XGrid``
-----------------------

.. code-block:: python

    import numpy as np
    import matplotlib.pyplot as plt
    import trendvis

    # Pseudorandom data and plot attributes
    random_generator = np.random.RandomState(seed=123)
    yvals = random_generator.rand(10)

    # Plot attributes
    nums = 10
    lw = 1.5

    # convenience function trendvis.gridwrapper() is available
    # to initialize XGrid and do most of the formatting shown here
    ex0 = trendvis.XGrid([1,2,1], figsize=(5,5))

    # Convenience function for plotting line data
    # Automatically colors y axis spines to
    # match line colors (auto_spinecolor=True)
    trendvis.plot_data(ex0,
        [[(np.linspace(0, 9.5, num=nums), yvals, 'blue')],
         [(np.linspace(1, 9, num=nums), yvals*5, 'red')],
         [(np.linspace(0.5, 10, num=nums), yvals*10, 'green')]],
        lw=lw, markeredgecolor='none', marker='s')

    # Get rid of extra spines
    ex0.cleanup_grid()
    ex0.set_spinewidth(lw)

    ex0.set_all_ticknums([(2, 1)], [(0.2, 0.1), (1, 0.5), (2, 1)])
    ex0.set_ticks(major_dim=(7, 3), minor_dim=(4, 2))

    ex0.set_ylabels(['stack axis 0', 'stack axis 1', 'stack axis 2'])

    # In XGrid.fig.axes, axes live in a 1 level list
    # In XGrid.axes, axes live in a nested list of [row][column]
    ex0.axes[2][0].set_xlabel('Main Axis', fontsize=14)

    # Compact the plot
    ex0.fig.subplots_adjust(hspace=-0.3)

.. image:: https://cloud.githubusercontent.com/assets/2184487/8859118/f4706b72-3140-11e5-9351-5182977a991c.png
    :target: https://cloud.githubusercontent.com/assets/2184487/8859118/f4706b72-3140-11e5-9351-5182977a991c.png
    :alt: Single column XGrid

Two-row ``YGrid`` with frame
----------------------------

.. code-block:: python

    import numpy as np
    import matplotlib.pyplot as plt
    import trendvis

    # Pseudorandom data
    random_generator = np.random.RandomState(seed=1234)
    xvals = random_generator.rand(20)

    # Plot attributes
    numpts = 20
    lw = 1.5

    # Initialize a YGrid
    ex1 = trendvis.YGrid([1, 2, 1], yratios=[1, 2], figsize=(5,5))

    # Convenience function
    trendvis.plot_data(ex1,
        [[(xvals, np.linspace(2, 18.5, num=numpts), 'blue')],
         [(xvals*5, np.linspace(1, 17, num=numpts),  'red')],
         [(xvals*10, np.linspace(0.5, 20, num=numpts), 'green')]],
        lw=lw, auto_spinecolor=True, markeredgecolor='none', marker='s')

    # Remove extra spines, color stack (y) ticks
    ex1.cleanup_grid()
    ex1.set_spinewidth(lw)

    # Tick, tick label formatting
    ex1.set_all_ticknums([(0.2, 0.1), (1, 0.5), (2, 1)], [(2, 1), (2, 1)])
    ex1.set_ticks(major_dim=(7, 3), minor_dim=(4, 2))
    ex1.set_ylim([(0, 15, 20), (1, 0, 11)])

    # Axes labels
    ex1.set_xlabels(['stack axis 0', 'stack axis 1', 'stack axis 2'])
    ex1.axes[0][0].set_ylabel('Main Axis 0', fontsize=14)
    ex1.axes[2][1].set_ylabel('Main Axis 1', fontsize=14,
                  rotation=270, labelpad=14)

    # Draw boxes around each row
    ex1.draw_frame()

    # Broken axis cutout marks also available, try this instead of the frame:
    # ex0.draw_cutout(di=0.05)

    # Compact the plot
    ex1.fig.subplots_adjust(wspace=-0.3)

.. image:: https://cloud.githubusercontent.com/assets/2184487/8859244/b07c0f9c-3141-11e5-8c1c-7d20f77ce7ee.png
    :target: https://cloud.githubusercontent.com/assets/2184487/8859244/b07c0f9c-3141-11e5-8c1c-7d20f77ce7ee.png
    :alt: Two-column YGrid

Three-column ``XGrid`` with advanced features
---------------------------------------------

.. code-block:: python

    import numpy as np
    import matplotlib.pyplot as plt
    import trendvis

    # Make some pseudorandom data
    random_generator = np.random.RandomState(seed=123)
    yvals = random_generator.rand(40)
    yvals1 = np.copy(yvals)
    yvals1[20:] = np.array([0.2, 0.3, 0.2, 0.5, 0.34, 0.24,
                0.15, 0.23, 0.26, 0.21] * 2)
    numpts = 40
    lw = 1.5
    x0 = np.linspace(2, 49.5, num=numpts)
    x1 = np.linspace(1, 49, num=numpts)
    x11 = np.linspace(1.5, 47.5, num=numpts)
    twin0 = np.linspace(2, 50, num=numpts)
    twin1 = np.linspace(0.5, 48, num=numpts)

    # Initialize XGrid and twin axes
    ex2 = trendvis.XGrid([3, 4], xratios=[1, 3, 2], figsize=(5, 5),
                         startside='right')
    ex2.make_twins([0, 1])

    # Convenience function
    trendvis.plot_data(ex2,
        [[(x0, yvals, 'blue')],
         [(x1, yvals1*5, 'red'), (x11, yvals1*5.2, 'orchid')],
         [],
         [(twin1, yvals*2, '0.5')]],
        lw=lw, marker=None)

    # Adjust twinned y-axis positions for readability
    ex2.move_spines(twin_shift=0.6)

    # For any other kind of plot (fill_between, scatter, errorbar, etc),
    # get axis and plot directly
    # Note: ex2.axes[2][2] == ex2.get_axis(0, xpos=2, is_twin=True)
    for ax in ex2.axes[2]:
        ax.fill_between(twin0, yvals+0.075, yvals-0.1,
                        edgecolor='none', color='darkorange')

    # Handle axis ticks
    ex2.cleanup_grid()
    ex2.set_spinewidth(lw)
    ex2.autocolor_spines()
    ex2.set_all_ticknums([(2, 1), (2, 1), (2, 1)],
                         [(0.2, 0.1), (1, 0.5), (1, 0.25), (0.5, 0.25)])
    ex2.set_ticks(major_dim=(6, 1.5), minor_dim=(3, 1))

    ex2.set_ylabels(['row 0', 'row 1', 'twin row 0', 'twin row 1'])

    # Rotate x-axis tick labels
    for ax in ex2.fig.axes:
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    # Draw a vertical bar behind the data - horizontal bars available too
    ex2.draw_bar(ex2.axes[1][2], ex2.axes[0][2], (45, 47), color='lightblue')

    # Ok to set axis limits after drawing on figure using TrendVis methods,
    # TrendVis will reset the bar to the right place!
    ex2.set_xlim([(0, 0, 3), (1, 13, 24), (2, 43, 50)])
    ex2.set_ylim([(2, 0, 2)])

    # matplotlib annotations supported
    ex2.get_axis(0).text(0, 0.75, 'Text')

    # Cutouts instead of frames
    ex2.draw_cutout(lw=lw)

    # Set the suptitle and compact the plot
    ex2.fig.suptitle('Title', fontsize=16, y=1.05);
    ex2.fig.subplots_adjust(hspace=-0.1)

.. image:: https://cloud.githubusercontent.com/assets/2184487/8860699/097e51fa-314b-11e5-93e5-eb158aa5b801.png
    :target: https://cloud.githubusercontent.com/assets/2184487/8860699/097e51fa-314b-11e5-93e5-eb158aa5b801.png
    :alt: Three-column XGrid with advanced features

===========================
Examples in Published Works
===========================
*Great Basin hydrology, paleoclimate, and connections with the North Atlantic: A speleothem stable isotope and trace element record from Lehman Caves, NV* by Mellissa Cross, David McGee, Wallace S. Broecker, Jay Quade, Jeremy D. Shakun, Hai Cheng, Yanbin Lu, and R. Lawrence Edwards.  doi:`10.1016/j.quascirev.2015.06.016 <http://dx.doi.org/10.1016/j.quascirev.2015.06.016>`_
    Figures 2, 3, 4, 5, and panels 1 and 2 in figure 6 made with TrendVis.
    
Additional references to works containing TrendVis figures are welcome!
    
