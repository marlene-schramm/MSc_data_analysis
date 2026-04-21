''' This script contains functions for plotting MITgcm ouput'''
import numpy as np
import plotly.graph_objects as go

### Surface animation function for 2D fields

def surface_animation(ds, var, model_run, time_dim, x_dim, y_dim, colorscale):
    ''' Create an animated surface plot for a given variable showing its time evolution.'''
    # Extract coordinate arrays
    x_coords = ds[x_dim].values
    y_coords = ds[y_dim].values

    # Determine global min/max
    var_min = float(ds[var].min())
    var_max = float(ds[var].max())

    frames = []
    time_values = ds[time_dim].values
    num_frames = len(time_values)

    for i in range(num_frames):
        # plot label for each time step (currently simple integer)
        time_label = str(i + 1)

        # Select Data slice for current timestep
        frame_data_slice = ds[var].isel({time_dim: i})
        
        z_data = frame_data_slice.values
        
        trace = go.Contour(
            z=z_data,
            x=x_coords,
            y=y_coords,
            colorscale=colorscale,
            showscale=True,
            colorbar=dict(title=var, thickness=20),
            zmin=var_min,
            zmax=var_max,
            contours=dict(showlines=False, coloring='fill'),
            line=dict(width=0),
            hovertemplate=(
                f"Time: {time_label}<br>" +  # Removed .2f since it's a string now
                "X: %{x:.2f}<br>" +
                "Y: %{y:.2f}<br>" +
                "TFLUX: %{z:.2f}<extra></extra>"
            )
        )
        
        frames.append(
            go.Frame(
                data=[trace],
                name=str(i)
            )
        )

    fig = go.Figure(data=frames[0].data, frames=frames)

    fig.update_layout(
        title="Model Run " + model_run + "<br>Time Evolution of " + var,
        xaxis_title="XC",
        yaxis_title="YC",
        width=1000,
        height=700,
        margin=dict(l=50, r=50, t=60, b=80),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[
                dict(label="▶ Play", method="animate", args=[None, {"frame": {"duration": 500, "redraw": True}, "mode": "immediate"}]),
                dict(label="⏸ Pause", method="animate", args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])
            ]
        )],
        sliders=[dict(
            steps=[
                dict(
                    method="animate",
                    args=[[str(i)], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}}],
                    # FIX 4: Use 'time_label' logic here too
                    label=str(i + 1)
                )
                for i in range(num_frames)
            ],
            currentvalue={"visible": False},
            pad={"t": 50},
            len=0.9,
            x=0.1,
            y=0
        )]  
    )

    fig.show(renderer="browser")


### Functions for 3D block animation with Plotly

def make_face(ds, face, var, cmin, cmax, cmid,colorscale="Viridis"):
    """
    Create a Plotly surface for one cube face.

    Parameters
    ----------
    ds : MITgcm output dataset with only one time (i.e. a snapshot)
    face : str
        One of: 'top', 'bottom', 'front', 'back', 'right', 'left'
    var : str
        Name of variable in ds (e.g. "T", "S")
    cmin, cmax : float
        Global color limits for surfacecolor
    colorscale : str, optional
        Plotly colorscale to use for surfacecolor
    """

    x = ds["XC"].values
    y = ds["YC"].values
    z = ds["Z"].values
    V = ds[var]

    if face == "top":
        face_values = V.isel(Z=0)
        x_face, y_face = np.meshgrid(x, y, indexing="xy")
        z_face = np.full_like(x_face, z[0])

    elif face == "bottom":
        face_values = V.isel(Z=-1)
        x_face, y_face = np.meshgrid(x, y, indexing="xy")
        z_face = np.full_like(x_face, z[-1])

    elif face == "front":
        face_values = V.isel(YC=0)
        x_face, z_face = np.meshgrid(x, z, indexing="xy")
        y_face = np.full_like(x_face, y[0])

    elif face == "back":
        face_values = V.isel(YC=-1)
        x_face, z_face = np.meshgrid(x, z, indexing="xy")
        y_face = np.full_like(x_face, y[-1])

    elif face == "right":
        face_values = V.isel(XC=-1)
        y_face, z_face = np.meshgrid(y, z, indexing="xy")
        x_face = np.full_like(y_face, x[-1])

    elif face == "left":
        face_values = V.isel(XC=0)
        y_face, z_face = np.meshgrid(y, z, indexing="xy")
        x_face = np.full_like(y_face, x[0])

    else:
        raise ValueError("Invalid face name")
    
    # grid lines
    x_edges = grid_edges_from_centers(ds["XC"].values)
    y_edges = grid_edges_from_centers(ds["YC"].values)
    z_edges = grid_edges_from_centers(ds["Z"].values)

    return go.Surface(
        x=x_face,
        y=y_face,
        z=z_face,
        surfacecolor=face_values.values,
        colorscale=colorscale,
        cmin=cmin,
        cmax=cmax,
        cmid=cmid,
        showscale=(face=="top") # this ensures that only one colorbar is shown
    )

def grid_edges_from_centers(c):
    """
    Helper function to compute cell edges from cell center coordinates for the visualization of the model grid. 
    Only the outermost lines remain on cell centers instead of being shifted to edges
    because the surface also end on the center points.

    Parameters
    ----------
    c : coordinate array of cell centers
    Returns
    -------
    edges : array
        Coordinate array of cell edges
    """
    mid = 0.5 * (c[:-1] + c[1:])
    first = c[0] # this is the center coordintate of the first cell
    last  = c[-1] # this is the center coordinate of the last cell
    edges = np.concatenate([[first], mid, [last]])

    return edges

def add_model_grid_lines(fig, ds, faces=None, line_color="black", line_width=1):
    """
    Add grid lines along cube surfaces representing the model grid.
    """
    if faces is None:
        faces = ["top","bottom","front","back","right","left"]

    # Compute cell edges
    edges = {
        "XC": grid_edges_from_centers(ds["XC"].values),
        "YC": grid_edges_from_centers(ds["YC"].values),
        "Z":  grid_edges_from_centers(ds["Z"].values)
    }

    # Define fixed coordinate and the two varying axes for each face
    face_def = {
        "top":    ("Z", edges["Z"][0], ["XC","YC"]),
        "bottom": ("Z", edges["Z"][-1], ["XC","YC"]),
        "front":  ("YC", edges["YC"][0], ["XC","Z"]),
        "back":   ("YC", edges["YC"][-1], ["XC","Z"]),
        "right":  ("XC", edges["XC"][-1], ["YC","Z"]),
        "left":   ("XC", edges["XC"][0], ["YC","Z"])
    }

    for face in faces:
        fixed_axis, fixed_val, var_axes = face_def[face]
        # Loop over line positions along first varying axis (except first and last as they would be on the cube edges)
        for v in edges[var_axes[1]][1:-1]:
            coords = {fixed_axis: fixed_val,
                      var_axes[0]: edges[var_axes[0]][0],  # start
                      var_axes[1]: v}
            coords_end = coords.copy()
            coords_end[var_axes[0]] = edges[var_axes[0]][-1]  # end

            fig.add_trace(go.Scatter3d(
                x=[coords["XC"], coords_end["XC"]],
                y=[coords["YC"], coords_end["YC"]],
                z=[coords["Z"], coords_end["Z"]],
                mode="lines",
                line=dict(color=line_color, width=line_width),
                showlegend=False
            ))

        # Loop over line positions along second varying axis (except first and last as they would be on the cube edges)
        for v in edges[var_axes[0]][1:-1]:
            coords = {fixed_axis: fixed_val,
                      var_axes[0]: v,
                      var_axes[1]: edges[var_axes[1]][0]}  # start
            coords_end = coords.copy()
            coords_end[var_axes[1]] = edges[var_axes[1]][-1]  # end

            fig.add_trace(go.Scatter3d(
                x=[coords["XC"], coords_end["XC"]],
                y=[coords["YC"], coords_end["YC"]],
                z=[coords["Z"], coords_end["Z"]],
                mode="lines",
                line=dict(color=line_color, width=line_width),
                showlegend=False
            ))

    return fig

def cube_time_evol(ds, var, model_run="", colorscale="Viridis", grid = True, quarter=False):
    """
    Create a 3D cube plot with time evolution for a given variable using Plotly (animated surface plot).

    Parameters
    ----------
    ds : MITgcm output dataset with time dimension
    var : str
        Name of variable in ds (e.g. "T", "S")
    model_run : str, optional
        Model run name to include in the title
    colorscale : str, optional
        Plotly colorscale to use for surfacecolor
    quarter : bool, optional
        If True, plot quarter of domain so that the crossections are vissible.
    """
    title_suffix = ""

    if quarter:
        Nx = len(ds.XC)
        Ny = len(ds.YC)
        ds = ds.isel(XC=slice(0,int(Nx/2)+1), YC=slice(0,int(Ny/2)+1))

        title_suffix = "Quarter Domain"

    # Pick colormap based on variable
    if var=="T": colorscale="thermal"
    if var=="S": colorscale="haline"

    # Global color limits -> all faces can have the same color scale
    cmin = np.min(ds[var].values)
    cmax = np.max(ds[var].values)
    cmid = None

    if colorscale == "balance" or colorscale == "balance_r":
        # For diverging colormaps, set cmin and cmax to be symmetric around zero (this is necessary for the colormap to be centered around zero)
        abs_max = max(abs(cmin), abs(cmax))
        cmin = -abs_max
        cmax = abs_max
        cmid = 0 # set cmid to zero
    elif (colorscale == "ice" or colorscale == "ice_r" or colorscale == "blues" or colorscale == "blues_r") and cmax >0:
        # Set cmin = 0 for the monoscale supercooling colormaps to ensure that only supercooled values are colored
        cmin = 0

    faces = ["top", "bottom", "front", "back", "right", "left"]

    # FIRST FRAME
    # For timestep 0, create surfaces for all faces
    face_data = [make_face(ds.isel(time=0), f, var, cmin, cmax, cmid, colorscale) for f in faces]
    # make colorbar
    face_data[0].update(showscale=True)
    # set colorbar title
    face_data[0].update(colorbar=dict(title=var + " [" + ds[var].units + "]"))

    # REMAINING FRAMES
    frames = []
    nt = len(ds["time"])
    for t in range(nt):
        dsi = ds.isel(time=t)
        frame_data = [make_face(dsi, f, var, cmin, cmax, cmid, colorscale) for f in faces]
        frames.append(go.Frame(data=frame_data, name=str(t)))

    # CREATE FIGURE
    fig = go.Figure(data=face_data, frames=frames)

    if grid == True:
        fig = add_model_grid_lines(fig, ds.isel(time=0), faces=faces, line_color="darkgrey", line_width=1)
    
    ## LAYOUT
    # Calculate axis spect ratios based on data ranges
    x_range = np.ptp(ds["XC"].values)  # peak-to-peak (max - min)
    y_range = np.ptp(ds["YC"].values)
    z_range = np.ptp(ds["Z"].values)

    # Set aspect ratios relative to the smallest range z
    if z_range > 0:
        aspect_x = x_range / z_range
        aspect_y = y_range / z_range
        aspect_z = 1.0
    else:
        aspect_x = aspect_y = aspect_z = 1.0

    fig.update_layout(
        title="Model Run " + model_run + "<br>Time Evolution of " + var + "<br>" + title_suffix,
        scene=dict(
            xaxis=dict(title="XC"),
            yaxis=dict(title="YC"),
            zaxis=dict(title="Z [m]"),
            aspectmode="manual",
            aspectratio=dict(x=aspect_x, y=aspect_y, z=aspect_z)
        ),
        width=850, height=750,
        updatemenus=[dict(
            type="buttons",
            buttons=[dict(label="Play", method="animate", args=[None])]
        )],
        sliders=[dict(
            steps=[dict(method="animate", args=[[str(t)]], label=f"{t}")
                for t in range(nt)]
        )]
    )
    fig.show(renderer="browser")
