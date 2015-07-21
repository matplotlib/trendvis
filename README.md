# TrendVis

TrendVis is a plotting package that uses matplotlib to create information-dense, sparkline-like, quantitative visualizations of multiple disparate data sets in a common plot area against a common variable.  This plot type is particularly well-suited for time-series data.  We discuss the rationale behind and the challenges associated with adapting matplotlib to this particular plot style, the TrendVis API and architecture, and various features available for users to customize and enhance the readability of their figures while walking through a sample workflow.

![TrendVis example](https://raw.githubusercontent.com/mscross/scipy_proceedings/trendvis/papers/mellissa_cross_t/barredplot.png)


## Quick Examples

Here are some examples of a range of complexities showing various features in TrendVis and a typical workflow. Version >= 0.2.1 is required.

### Simple 1 column XGrid
``` python
import numpy as np
import matplotlib.pyplot as plt
import trendvis

yvals = np.random.rand(10)
nums = 10
lw = 1.5

# convenience function trendvis.gridwrapper() is available
# to initialize XGrid and do most of the formatting shown here
ex0 = trendvis.XGrid([1,2,1], figsize=(5,5))

# Convenience function for plotting line data
# Automatically colors y axis spines to
# match line colors (auto_spinecolor=True)
trendvis.plot_data(ex0, [[(np.linspace(0, 9.5, num=nums), yvals, 'blue')],
                        [(np.linspace(1, 9, num=nums), yvals*5, 'red')],
                        [(np.linspace(0.5, 10, num=nums),
                          yvals*10, 'green')]],
                  lw=1.5, markeredgecolor='none', marker='s')

# Get rid of extra spines
ex0.cleanup_grid()

ex0.set_spinewidth(lw)

ex0.set_all_ticknums([(2, 1)], [(0.2, 0.1), (1, 0.5), (2, 1)])
ex0.set_ticks(major_dim=(7, 3), minor_dim=(4, 2))

ex0.set_ylabels(['stack axis 0', 'stack axis 1', 'stack axis 2'])

# In XGrid.fig.axes, axes live in a 1 level list
# In XGrid.axes, axes live in a nested list of [row][column]
ex0.axes[2][0].set_xlabel('Main Axis', fontsize=14)

ex0.fig.subplots_adjust(hspace=-0.3)
```

### Slightly more complex 2 row YGrid with frame
``` python
import numpy as np
import matplotlib.pyplot as plt
import trendvis

xvals = np.random.rand(20)
nums = 20
lw = 1.5

ex1 = trendvis.YGrid([1,2,1], yratios=[1, 2], figsize=(5,5))

# Convenience function
trendvis.plot_data(ex1, [[(xvals, np.linspace(2, 18.5, num=nums), 'blue')],
                         [(xvals*5, np.linspace(1, 17, num=nums),  'red')],
                         [(xvals*10, np.linspace(0.5, 20, num=nums),
                           'green')]],
                   lw=1.5, auto_spinecolor=True, markeredgecolor='none', marker='s')

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

# Decrease subplot spacing
# Draw boxes around each row
ex1.draw_frame()

# Broken axis cutout marks also available, try this instead of the frame:
# ex0.draw_cutout(di = 0.05)

ex1.fig.subplots_adjust(wspace=-0.3)
```

### Even more complex 3 column XGrid with rectangle, cutouts, and twins
``` python
import numpy as np
import matplotlib.pyplot as plt
import trendvis

yvals = np.random.rand(40)
yvals1 = np.copy(yvals)
yvals1[20:] = np.array([0.2, 0.3, 0.2, 0.5, 0.34, 0.24,
						0.15, 0.23, 0.26, 0.21] * 2)
nums = 40
x0 = np.linspace(2, 49.5, num=nums)
x1 = np.linspace(1, 49, num=nums)
x11 = np.linspace(1.5, 47.5, num=nums)
twin0 = np.linspace(2, 50, num=nums)
twin1 = np.linspace(0.5, 48, num=nums)

ex2 = trendvis.XGrid([3, 4], xratios=[1, 3, 2], figsize=(5,5),
                     startside='right')
ex2.make_twins([0,1])

ex2.cleanup_grid()

trendvis.plot_data(ex2, [[(x0, yvals, 'blue')],
                         [(x1, yvals1*5, 'red'), (x11, yvals1*5.2,
                         						  'orchid')],
                         [],
                         [(twin1, yvals*2, '0.5')] ],
                   lw=1.5, marker=None)
ex2.move_spines(twin_shift=0.6)

# For any other kind of plot (fill between, scatter, errorbar, etc),
# must get axis and plot directly
# ex2.axes[2][2] == ex2.get_axis(0, xpos=2, is_twin=True)
ex2.axes[2][0].fill_between(twin0, yvals+0.075, yvals-0.1,
							edgecolor='none', color='darkorange')
ex2.axes[2][1].fill_between(twin0, yvals+0.075, yvals-0.1,
							edgecolor='none', color='darkorange')
ex2.axes[2][2].fill_between(twin0, yvals+0.075, yvals-0.1,
							edgecolor='none', color='darkorange')

ex2.autocolor_spines()

ex2.set_all_ticknums([(2, 1), (2, 1), (2, 1)],
					 [(0.2, 0.1), (1, 0.5), (1, 0.25), (.5,0.25)])
ex2.set_ticks(major_dim=(6, 1.5), minor_dim=(3, 1))

ex2.set_ylabels(['row 0', 'row 1', 'twin row 0', 'twin row 1'])

# Horizontal bars available too
ex2.draw_bar(ex2.axes[1][2], ex2.axes[0][2], (45, 47), color='lightblue')

# Ok to set axis limits after drawing on figure using TrendVis methods,
# TrendVis will reset the bar to the right place!
ex2.set_xlim([(0, 0, 3), (1, 13, 24), (2, 43, 50)])
ex2.set_ylim([(2, 0, 2)])

ex2.get_axis(0).text(0, 0.75, 'Text')

ex2.draw_cutout(lw=1.5)
ex2.fig.suptitle('Title', fontsize=16, y=1.05);

ex2.fig.subplots_adjust(hspace=-0.1)
```
