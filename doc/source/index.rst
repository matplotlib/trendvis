.. currentmodule:: trendvis

====================
 TrendVis
====================

.. htmlonly::

    :Release: |version|
    :Date: |today|

:py:mod:`trendvis` API
====================

.. autosummary::
   :toctree: generated/

   Grid
   XGrid
   YGrid
   make_grid
   plot_data


The public API of :py:mod:`trendvis` consists of three classes, `Grid`, `XGrid`, and `YGrid`, and two convenience functions :func:`make_grid` and :func:`plot_data`.  The preferred interface is through `XGrid` and `YGrid`, but the convenience functions are provided to quickly create and format an `XGrid` or `YGrid` and draw line plots.


`trendvis` Usage
================


Motivation
==========


When plotting multiple datasets against a common x or y axis, a figure can quickly become cluttered with overlain curves and/or unnecessary axis spines.  `TrendVis` enables construction of complex figures with data plotted in a common plot area against different y or x ('stack') axes and a common x or y (main) axis respectively.
