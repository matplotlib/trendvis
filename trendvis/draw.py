import matplotlib.pyplot as plt


def frame(fig, lowerleft_axis, upperright_axis, linewidth):
    """
    Draws frame around subplots

    Parameters
    ----------
    fig : Figure object
        The figure.
    lowerleft_axis : axis object
        Physically lowest and/or leftmost axis in subplot
    upperright_axis : axis object
        Physically highest and/or rightmost axis in subplot.
        May be the same axis as lowerleft_axis.
    linewidth : int
        Width of frame line.

    """

    # Data coordinates of lower left and upper right corners
    lldx = lowerleft_axis.get_xlim()[0]
    lldy = lowerleft_axis.get_ylim()[0]

    urdx = upperright_axis.get_xlim()[1]
    urdy = upperright_axis.get_ylim()[1]

    origin, w, h = convert_coords(fig, lowerleft_axis, upperright_axis,
                                  [lldx, lldy], [urdx, urdy])

    # # Convert data coordinates to axes coordinates
    # lla = lowerleft_axis.transData.transform([lldx, lldy])
    # ura = upperright_axis.transData.transform([urdx, urdy])

    # # Convert axes coordinates to figure coordinates
    # llf = fig.transFigure.inverted().transform(lla)
    # urf = fig.transFigure.inverted().transform(ura)

    # # Get width and height of frame
    # w = urf[0] - llf[0]
    # h = urf[1] - llf[1]

    # Make frame
    fig.patches.append(plt.Rectangle(origin, w, h, transform=fig.transFigure,
                                     facecolor='none', linewidth=linewidth,
                                     edgecolor='black', zorder=-1))


def bar(fig, lowerleft_axis, upperright_axis, bar,
        vertical):
    """
    Draws vertical bars (called from ystack) or horizontal bars
        (called from xstack) across the subplots.

    Parameters
    ----------
    fig : Figure object
        The figure.
    lowerleft_axis : axis object
        Physically lowest and/or leftmost axis in subplot
    upperright_axis : axis object
        Physically highest and/or rightmost axis in subplot.
        May be the same axis as lowerleft_axis.
    bar : list of tuples
        (lower/left data coordinate, upper/right x or y data coordinate,
            color, alpha value).  If no alpha value given, 0.25 will be used.
    vertical : Boolean
        If True, vertical bars will be plotted; if False, horizontal bars.

    """

    # Step through list of bars
    # for b in bars:
    # Get data coordinates
    if vertical:
        lldx = bar[0]
        lldy = lowerleft_axis.get_ylim()[0]

        urdx = bar[1]
        urdy = upperright_axis.get_ylim()[1]

    else:
        lldx = lowerleft_axis.get_xlim()[0]
        lldy = bar[0]

        urdx = upperright_axis.get_xlim()[1]
        urdy = bar[1]

    # Get lower left corner of rectangle in figure coordinates,
    # get width, height in figure coordinates
    origin, w, h = convert_coords(fig, lowerleft_axis, upperright_axis,
                                  [lldx, lldy], [urdx, urdy])

    # Set bar alpha value
    try:
        alpha = bar[3]
    except:
        alpha = 0.25

    # Make bar
    fig.patches.append(plt.Rectangle(origin, w, h, alpha=alpha, zorder=-1,
                                     transform=fig.transFigure,
                                     facecolor=bar[2], edgecolor='none'))


def cutout(axes, di, xratios, numcols, numrows):
    """
    Draw cutouts on broken x axes.

    Parameters
    ----------
    axes : list of axes objects
        The axes to draw cutouts on.
    di : float
        The dimensions of the cutout mark.
    xratios : list of ints
        Relative widths of the columns
    numcols : int
        The number of columns in the figure
    numrows : int
        The number of rows in the figure

    """

    d = di * xratios[0]
    kwargs = dict(tranform=axes[0][0].transAxes, color='black',
                  clip_on=False)
    axes[0][0].plot((1-d, 1+d), (-d, d), **kwargs)

    kwargs.update(transform=axes[numrows-1][0].transAxes)
    axes[0][0].plot((1-d, 1+d), (1-d,1+d), **kwargs)

    for i in range(1, numcols-1):
        d = di * xratios[i]
        kwargs.update(transform=axes[0][i].transAxes)
        axes[0][i].plot((-d, d), (-d, d), **kwargs)
        axes[0][i].plot((1-d, 1+d), (-d, d), **kwargs)

        kwargs.update(transform=axes[numrows-1][i].transAxes)
        axes[numrows-1][i].plot((-d, d), (1-d, 1+d), **kwargs)
        axes[numrows-1][i].plot((1-d, 1+d),(1-d, 1+d), **kwargs)

    kwargs.update(transform=axes[0][numcols-1].transAxes)
    axes[0][numcols-1].plot((-d, d), (-d, d), **kwargs)

    kwargs.update(transform=axes[numrows-1, numcols-1].transAxes)
    axes[numrows-1][numcols-1].plot((-d, d), (1-d, 1+d), **kwargs)


def convert_coords(fig, lowerleft_axis, upperright_axis, lld, urd):
    """
    Convert data coordinates to axis and figure coordinates.

    Parameters
    ----------
    fig : Figure object
        The figure.
    lowerleft_axis : axis object
        Physically lowest and/or leftmost axis in subplot
    upperright_axis
        Physically highest and/or rightmost axis in subplot.
        May be the same axis as lowerleft_axis.
    lld : list of ints or floats
        The data coordinates of the lower left corner of the rectangle
    urd : list of ints of floats
        The data coordinates of the upper right corner of the rectangle

    Returns
    -------
    origin : tuple of floats
        The lower left corner of the rectangle in figure coordinates
    width : float
        The width of the rectangle in figure coordinates
    height : float
        The height of the rectangle in figure coordinates

    """

    # Convert data coordinates to axes coordinates
    lla = lowerleft_axis.transData.transform(lld)
    ura = upperright_axis.transData.transform(urd)

    # Convert axes coordinates to figure coordintes
    llf = fig.transFigure.inverted().transform(lla)
    urf = fig.transFigure.inverted().transform(ura)

    # Find width and height of rectangle in figure coordinates
    width = urf[0] - llf[0]
    height = urf[1] - llf[1]

    origin = llf

    return origin, width, height
