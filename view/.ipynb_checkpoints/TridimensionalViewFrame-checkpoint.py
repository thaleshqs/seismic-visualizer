from mayavi import mlab

class TridimensionalViewFrame():
    def __init__(self, seismic_data) -> None:
        fig = mlab.figure(figure='seismic', bgcolor=(1, 1, 1), fgcolor=(0, 0, 0))

        scalars = seismic_data   # specifying the data array
        mlab.volume_slice(scalars, slice_index=0, plane_orientation='x_axes', figure=fig, colormap='gray')   # crossline slice
        mlab.volume_slice(scalars, slice_index=0,  plane_orientation='y_axes', figure=fig, colormap='gray')   # inline slice
        mlab.volume_slice(scalars, slice_index=0, plane_orientation='z_axes', figure=fig, colormap='gray')   # depth slice
        mlab.show()
