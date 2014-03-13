"""
Interactive animations in IPython notebooks using matplotlib and JSAnimation.
"""


def ianimate(frame_list,plotdata=None,**kargs):
    """
        frame_list may be:

            - a list of Solution objects
            - a controller possessing a list of Solution objects
            - a string specifying a relative path to a set of output files
    """
    import matplotlib.pyplot as plt
    from matplotlib import animation
    from clawpack.visclaw.JSAnimation import IPython_display
    from clawpack.pyclaw import Controller

    if isinstance(frame_list,Controller):
        frame_list = frame_list.frames

    ivar = 0

    frame = frame_list[0]
    ndim = len(frame.q.shape)-1
    if ndim == 1:
        fig = plt.figure(figsize=(8,4))
        ax = plt.axes()
        xc = frame.state.grid.p_centers
        im, = ax.plot([], [])
    elif ndim == 2:
        fig = plt.figure(figsize=(4,4))
        xc, yc = frame.state.grid.p_centers
        im = plt.imshow(frame.q[ivar,:,:].T,
                extent = [xc.min(), xc.max(), yc.min(), yc.max()], 
                interpolation='nearest',origin='lower')


    def fplot(frame_number):
        frame = frame_list[frame_number]
        if ndim == 1:
            im.set_data(xc, frame.q[ivar,:])
        elif ndim == 2:
            im.set_data(frame.q[ivar,:,:].T)
        else:
            raise Exception('3D animation not yet implemented')
        return im,

    return animation.FuncAnimation(fig, fplot, frames=len(frame_list))
