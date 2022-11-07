from matplotlib.testing.decorators import image_comparison as _ic
from functools import partial

image_comparison = partial(
    _ic,
    extensions=["png"],
    tol=22,
    style=["classic", "_classic_test_patch", {"figure.figsize": (10, 10)}],
)
