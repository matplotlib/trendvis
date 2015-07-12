from __future__ import division, absolute_import, print_function

"""
TrendVis testing

???

"""

import trendvis

from trendvis.testing import image_comparison

from matplotlib.testing.decorators import cleanup
import matplotlib.pyplot as plt
from matplotlib.testing.noseclasses import KnownFailure


@cleanup
def test_xgrid_init():
    trendvis.XGrid([2, 3, 1, 2])


@cleanup
def test_ygrid_init():
    trendvis.YGrid([2, 3, 1, 2])


@image_comparison(baseline_images=['xgrid_clean_001'])
def test_xgrid_clean():
    testgrid = trendvis.XGrid([2, 3, 1, 2])
    testgrid.cleanup_grid()


if __name__ == '__main__':
    import nose
    import sys

    nose.main(addplugins=[KnownFailure()])

    args = ['-s', '--with-doctest']
    argv = sys.argv
    argv = argv[:1] + args + argv[1:]
    nose.runmodule(argv=argv, exit=False)
