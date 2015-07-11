.. currentmodule:: cycler

====================
 Style/kwarg cycler
====================

.. htmlonly::

    :Release: |version|
    :Date: |today|

:py:mod:`cycler` API
====================

.. autosummary::
   :toctree: generated/

   cycler
   Cycler


The public API of :py:mod:`cycler` consists of a class `Cycler` and a
factory function :func:`cycler`.  The function provides a simple interface for
creating 'base' `Cycler` objects while the class takes care of the composition
and iteration logic.


`Cycler` Usage
==============

Base
----

A single entry `Cycler` object can be used to easily
cycle over a single style.  To create the `Cycler` use the :py:func:`cycler`
function to link a key/style/kwarg to series of values.  The key must be
hashable (as it will eventually be used as the key in a :obj:`dict`).

.. ipython:: python

   from __future__ import print_function
   from cycler import cycler


   color_cycle = cycler('color', ['r', 'g', 'b'])
   color_cycle

The `Cycler` knows it's length and keys:

.. ipython:: python


   len(color_cycle)
   color_cycle.keys

Iterating over this object will yield a series of :obj:`dict` objects keyed on
the label

.. ipython:: python

   for v in color_cycle:
       print(v)

`Cycler` objects can be passed as the second argument to :func:`cycler`
which returns a new  `Cycler` with a new label, but the same values.

.. ipython:: python

   cycler('ec', color_cycle)


Iterating over a `Cycler` results in the finite list of entries, to
get an infinite cycle, call the `Cycler` object (a-la a generator)

.. ipython:: python

   cc = color_cycle()
   for j, c in zip(range(5),  cc):
       print(j, c)


Composition
-----------

A single `Cycler` can just as easily be replaced by a single ``for``
loop.  The power of `Cycler` objects is that they can be composed to easily
create complex multi-key cycles.

Addition
~~~~~~~~

Equal length `Cycler` s with different keys can be added to get the
'inner' product of two cycles

.. ipython:: python

   lw_cycle = cycler('lw', range(1, 4))

   wc = lw_cycle + color_cycle

The result has the same length and has keys which are the union of the
two input `Cycler` s.

.. ipython:: python

   len(wc)
   wc.keys

and iterating over the result is the zip of the two input cycles

.. ipython:: python

   for s in wc:
       print(s)

As with arithmetic, addition is commutative

.. ipython:: python

   lw_c = lw_cycle + color_cycle
   c_lw = color_cycle + lw_cycle

   for j, (a, b) in enumerate(zip(lw_c, c_lw)):
      print('({j}) A: {A!r} B: {B!r}'.format(j=j, A=a, B=b))


Multiplication
~~~~~~~~~~~~~~

Any pair of `Cycler` can be multiplied

.. ipython:: python

   m_cycle = cycler('marker', ['s', 'o'])

   m_c = m_cycle * color_cycle

which gives the 'outer product' of the two cycles (same as
:func:`itertools.prod` )

.. ipython:: python

   len(m_c)
   m_c.keys
   for s in m_c:
       print(s)

Note that unlike addition, multiplication is not commutative (like
matrices)

.. ipython:: python

   c_m = color_cycle * m_cycle

   for j, (a, b) in enumerate(zip(c_m, m_c)):
      print('({j}) A: {A!r} B: {B!r}'.format(j=j, A=a, B=b))




Integer Multiplication
~~~~~~~~~~~~~~~~~~~~~~

`Cycler` s can also be multiplied by integer values to increase the length.

.. ipython:: python

   color_cycle * 2
   2 * color_cycle



Slicing
-------

Cycles can be sliced with :obj:`slice` objects

.. ipython:: python

   color_cycle[::-1]
   color_cycle[:2]
   color_cycle[1:]

to return a sub-set of the cycle as a new `Cycler`.

Examples
--------

We can use `Cycler` instances to cycle over one or more ``kwarg`` to
`~matplotlib.axes.Axes.plot` :

.. plot::
   :include-source:

   from cycler import cycler
   from itertools import cycle

   fig, (ax1, ax2) = plt.subplots(1, 2, tight_layout=True,
                                  figsize=(8, 4))
   x = np.arange(10)

   color_cycle = cycler('c', ['r', 'g', 'b'])

   for i, sty in enumerate(color_cycle):
      ax1.plot(x, x*(i+1), **sty)


   for i, sty in zip(range(1, 5), cycle(color_cycle)):
      ax2.plot(x, x*i, **sty)


.. plot::
   :include-source:

   from cycler import cycler
   from itertools import cycle

   fig, (ax1, ax2) = plt.subplots(1, 2, tight_layout=True,
                                  figsize=(8, 4))
   x = np.arange(10)

   color_cycle = cycler('c', ['r', 'g', 'b'])
   ls_cycle = cycler('ls', ['-', '--'])
   lw_cycle = cycler('lw', range(1, 4))

   sty_cycle = ls_cycle * (color_cycle + lw_cycle)

   for i, sty in enumerate(sty_cycle):
      ax1.plot(x, x*(i+1), **sty)

   sty_cycle = (color_cycle + lw_cycle) * ls_cycle

   for i, sty in enumerate(sty_cycle):
      ax2.plot(x, x*(i+1), **sty)


Exceptions
----------


A :obj:`ValueError` is raised if unequal length `Cycler` s are added together

.. ipython:: python
   :okexcept:

   cycler('c', ['r', 'g', 'b']) + cycler('ls', ['-', '--'])

or if two cycles which have overlapping keys are composed

.. ipython:: python
   :okexcept:

   color_cycle = cycler('c', ['r', 'g', 'b'])

   color_cycle + color_cycle


Motivation
==========


When plotting more than one line it is common to want to be able to cycle over one
or more artist styles.  For simple cases than can be done with out too much trouble:

.. plot::
   :include-source:

   fig, ax = plt.subplots(tight_layout=True)
   x = np.linspace(0, 2*np.pi, 1024)

   for i, (lw, c) in enumerate(zip(range(4), ['r', 'g', 'b', 'k'])):
      ax.plot(x, np.sin(x - i * np.pi / 4),
              label=r'$\phi = {{{0}}} \pi / 4$'.format(i),
              lw=lw + 1,
              c=c)

   ax.set_xlim([0, 2*np.pi])
   ax.set_title(r'$y=\sin(\theta + \phi)$')
   ax.set_ylabel(r'[arb]')
   ax.set_xlabel(r'$\theta$ [rad]')

   ax.legend(loc=0)

However, if you want to do something more complicated:

.. plot::
   :include-source:

   fig, ax = plt.subplots(tight_layout=True)
   x = np.linspace(0, 2*np.pi, 1024)

   for i, (lw, c) in enumerate(zip(range(4), ['r', 'g', 'b', 'k'])):
      if i % 2:
          ls = '-'
      else:
          ls = '--'
      ax.plot(x, np.sin(x - i * np.pi / 4),
              label=r'$\phi = {{{0}}} \pi / 4$'.format(i),
              lw=lw + 1,
              c=c,
              ls=ls)

   ax.set_xlim([0, 2*np.pi])
   ax.set_title(r'$y=\sin(\theta + \phi)$')
   ax.set_ylabel(r'[arb]')
   ax.set_xlabel(r'$\theta$ [rad]')

   ax.legend(loc=0)

the plotting logic can quickly become very involved.  To address this and allow easy
cycling over arbitrary ``kwargs`` the `Cycler` class, a composable
kwarg iterator, was developed.
