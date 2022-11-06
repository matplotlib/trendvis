from __future__ import division, absolute_import, print_function

"""
TrendVis testing

???

"""

import trendvis

from trendvis.testing import image_comparison

import matplotlib.pyplot as plt

# baseline images use the old default figsize of 10x10 inches.
plt.rcParams["figure.figsize"] = "10, 10"


def test_xgrid_init():
    trendvis.XGrid([2, 3, 1, 2])


def test_ygrid_init():
    trendvis.YGrid([2, 3, 1, 2])


@image_comparison(baseline_images=["xgrid_clean"])
def test_xgrid_clean():
    testgrid = trendvis.XGrid([2, 3, 1, 2])
    testgrid.cleanup_grid()


@image_comparison(baseline_images=["ygrid_clean"])
def test_ygrid_clean():
    testgrid = trendvis.YGrid([4, 6])
    testgrid.cleanup_grid()


@image_comparison(baseline_images=["xgrid_twins"])
def test_xgrid_twins():
    testgrid = trendvis.XGrid([2, 5, 1], alternate_sides=False, xratios=[2, 1])
    testgrid.make_twins([0, 2])
    testgrid.cleanup_grid()


@image_comparison(baseline_images=["ygrid_twins"])
def test_ygrid_twins():
    testgrid = trendvis.YGrid([2, 2, 1], alternate_sides=False, yratios=[2, 1])
    testgrid.make_twins([0, 2])
    testgrid.cleanup_grid()


@image_comparison(baseline_images=["xgrid_multitwin"])
def test_xgrid_multitwin():
    testgrid = trendvis.XGrid([2, 1])
    testgrid.make_twins([0, 1])
    testgrid.make_twins(3)


@image_comparison(baseline_images=["ygrid_multitwin"])
def test_ygrid_multitwin():
    testgrid = trendvis.YGrid([2, 1])
    testgrid.make_twins([0, 1])
    testgrid.make_twins(3)


def test_get_axes_xgrid():
    testgrid = trendvis.XGrid([2, 1])
    testgrid.make_twins([0])

    assert testgrid.get_axis(0, is_twin=True) == testgrid.axes[2][0]


def test_get_axes_ygrid():
    testgrid = trendvis.YGrid([2, 1])
    testgrid.make_twins([0])

    assert testgrid.get_axis(0, is_twin=True) == testgrid.axes[2][0]


#
# def test_get_twin_rownum():


#
# def test_get_twin_colnum():


def test_reverse_axes_xgrid():
    testgrid = trendvis.XGrid([2, 1])
    lim0 = testgrid.fig.axes[0].get_ylim()
    lim1 = testgrid.fig.axes[1].get_ylim()
    mainlim = testgrid.fig.axes[0].get_xlim()

    testgrid.reverse_yaxis()
    testgrid.reverse_xaxis()

    assert lim0 == testgrid.fig.axes[0].get_ylim()[::-1]
    assert lim1 == testgrid.fig.axes[1].get_ylim()[::-1]
    assert mainlim == testgrid.fig.axes[1].get_xlim()[::-1]


def test_reverse_axes_ygrid():
    testgrid = trendvis.YGrid([2, 1])
    lim0 = testgrid.fig.axes[0].get_xlim()
    lim1 = testgrid.fig.axes[1].get_xlim()
    mainlim = testgrid.fig.axes[0].get_ylim()

    testgrid.reverse_xaxis()
    testgrid.reverse_yaxis()

    assert lim0 == testgrid.fig.axes[0].get_xlim()[::-1]
    assert lim1 == testgrid.fig.axes[1].get_xlim()[::-1]
    assert mainlim == testgrid.fig.axes[1].get_ylim()[::-1]


@image_comparison(baseline_images=["xgrid_cutout"])
def test_xgrid_cutout():
    testgrid = trendvis.XGrid([1], xratios=[1, 2])
    testgrid.cleanup_grid()
    testgrid.draw_cutout()


@image_comparison(baseline_images=["ygrid_cutout"])
def test_ygrid_cutout():
    testgrid = trendvis.YGrid([1], yratios=[1, 2])
    testgrid.cleanup_grid()
    testgrid.draw_cutout()


@image_comparison(baseline_images=["xgrid_ylabels"])
def test_xgrid_ylabels():
    testgrid = trendvis.XGrid([1, 2])
    testgrid.set_ylabels(["0", "1"])


@image_comparison(baseline_images=["ygrid_xlabels"])
def test_ygrid_xlabels():
    testgrid = trendvis.YGrid([1, 2, 1])
    testgrid.set_xlabels(["0", "1", None])


@image_comparison(baseline_images=["xgrid_frame"])
def test_xgrid_frame():
    testgrid = trendvis.XGrid([1, 2, 1], xratios=[1, 1])
    testgrid.cleanup_grid()
    testgrid.draw_frame()


@image_comparison(baseline_images=["ygrid_frame"])
def test_ygrid_frame():
    testgrid = trendvis.YGrid([1, 2, 1], yratios=[1, 1])
    testgrid.cleanup_grid()
    testgrid.draw_frame()


if __name__ == "__main__":
    import nose
    import sys

    nose.main(addplugins=[KnownFailure()])

    args = ["-s", "--with-doctest"]
    argv = sys.argv
    argv = argv[:1] + args + argv[1:]
    nose.runmodule(argv=argv, exit=False)
